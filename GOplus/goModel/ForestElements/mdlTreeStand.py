from ...goBases import *

from .mdlTreeSizes import TreeSizes
from .mdlTrees import Trees
from .mdlLeavesCohort import LeavesCohort
from .Canopy.mdlSunShadeFarquhar_CanopySurface import SunShadeCanopySurface as Canopy

import  random


class TreeStand(Trees):
    '''represent the trees vegetation layer (typically those of Pinus pinaster)
    '''

    # Outer elements
    sunTime = eltOut('SunTime element')
    microclim = eltOut('Upper MicroClimate element')
    microclim_under = eltOut('Under MicroClimate element')
    soil = eltOut('Soil element')

    #Inner elements
    cohorts = eltIn(ELTS)
    canopy = eltIn(Canopy)

    #vars
    ClumpAge= var('age of last clump cut (year) (yyyy)', 0.)
    Age = var('tree age (year)')
    Age_aerial = var('age of the aerial part of the tree  (year)')

    #params
    Area = param('stand area (m2)',  1000)

    def _simul_initialisation(self):
        '''Initialisation step'''

        #connect the inner ELT
        self.canopy.sunTime = self.sunTime
        self.canopy.microclim = self.microclim
        self.canopy.microclim_under = self.microclim_under
        self.canopy.soil = self.soil

        #create the trees
        self.pcs_TreeStandInstallation()

        #Create 4 needle cohorts and fix for each the date of bud burst (B4 stage for P. pinaster) to the  DOY 136
        #TODO  : enable to adjust the initial number of cohort in function of, initial age,  species ... or leafArea
        for _y in (4, 3, 2, 1):
            _cohort = LeavesCohort()
            _cohort.Year =  self.sunTime.Y_start - _y
            _cohort.BudBurst = True
            _cohort.BudBurstDate = 136 - int(_y*365.25)

            _cohort.Retained =(1,0.8,0.17,0)[_y-1]

            _cohort.treeStand = self
            _cohort.sunTime = self.sunTime
            _cohort.microclim = self.microclim

            self.cohorts.add(_cohort)


    def update(self):
        '''hourly update'''
        #PROCESSES EVALUATED AT SIMULATION BEGINNING
        if self.sunTime.isSimulBeginning:
            self._simul_initialisation()

        #Age reevalution
        if self.sunTime.isYearBeginning :
            self.Age = self.sunTime.Y - self._germinationYear + 1
            self.Age_aerial = self.Age -self.ClumpAge

        #Tissues development
        self.pcs_LeafAreaDevelopment()
        self.pcs_SecondaryGrowth()
        self.pcs_Senescence()
        self.pcs_AllocateLitterCarbonToSoil()

        #Canopy surface processes
        self.canopy.update()

        #Water balance processes
        self.pcs_HydraulicStatus()
        self.pcs_HydricStress()

        #Carbon balance processes
        self.pcs_Respiration()
        self.pcs_CarbonFluxesPartition()

   #LEAF AREA DEVELOPMENT
    LeafArea = var('total leaf area (m2_leaf /m2_soil)' )
    LeafFall = var('litterfall (Kg_DM /m2_soil /day)')

    @pcs
    def pcs_LeafAreaDevelopment(self):

        #Manage the presence of the cohorts (creation and disappearance)
        if self.sunTime.isYearBeginning:
            #Remove cohort  if its proportion of leaves retained  is falled under 1%
            for _cohort in   [_c for _c in self.cohorts if _c.Retained <= 0.01]:
                self.cohorts.remove(_cohort)

            #Create a new leaf cohort
            _cohort = LeavesCohort()
            _cohort.Year=self.sunTime.Y
            _cohort.treeStand = self
            _cohort.sunTime = self.sunTime
            _cohort.microclim = self.microclim
            self.cohorts.add(_cohort)

        #Update the status of the leaves cohorts
        for _cohort in self.cohorts:
            _cohort.update()

        #Integration of the leaf area components at the stand level
        if self.sunTime.isDayBeginning:
            self.LeafFall = sum(_cohort.LeafFall for _cohort in self.cohorts)
            self.LeafArea = sum(_cohort.Area for _cohort in self.cohorts)

            # to allow a treeStand functionning without trees (clear-cutting period) LAI can not be zero (as if we have residual tree)

            self.canopy.LAI = max (0.001,sum(_cohort.LAI for _cohort in self.cohorts))




    #SECONDARY GROWTH PHENOLOGY
    GrowthIntensity = var('relative growth rate (annual integration = 1) (?)', 0.)

    @pcs
    def pcs_SecondaryGrowth(self,
        k_Growth_b = param('parameter b of secondary growth model (-)',  105.5),
        k_Growth_c = param('parameter c of secondary growth model (-)',2.084),
        k_Growth_d = param('parameter d of secondary growth model (-)',62.85),
        ):
        ''' Secondary growth phenology'''

        if self.sunTime.isDayBeginning:
            if self.sunTime.DOY < k_Growth_d :
                self.GrowthIntensity = 0
            else :
                _KJref = (self.sunTime.DOY - k_Growth_d)/ k_Growth_b
                self.GrowthIntensity = (k_Growth_c / k_Growth_b) * (_KJref ** (k_Growth_c - 1)) * exp(-(_KJref ** k_Growth_c))


    @pcs
    def pcs_AllocateLitterCarbonToSoil(self):
        '''Add compartment litter to soil carbon incoming'''
        #TODO:devrait probablement etre gere par l'objet forest

        if self.sunTime.isDayBeginning:
            _gC_by_KgMS = 480
            _Day_by_Year = 365.25

            #add leaf litter to soil incoming carbon
            self.soil.carbonCycle.incorporateACarbonLitter(self.LeafFall * _gC_by_KgMS, 2, 2)

            #add branch litter to soil incoming carbon
            #TODO : change Senescenece time unit
            self.soil.carbonCycle.incorporateACarbonLitter(self.BranchSenescence * _gC_by_KgMS / _Day_by_Year, 0.25, 5)

            #add root litter to soil incoming carbon
            self.soil.carbonCycle.incorporateACarbonLitter(self.RootSenescence * _gC_by_KgMS / _Day_by_Year, 0.5, 3)


    #HYDRAULIC STATUS
    SoilRootsWaterPotential = var('soil- roots interface water potential (MPa)')

    @pcs
    def pcs_HydraulicStatus(self,
        k_Rxyl_1  = param('parameter 1 in allometric relation between tree height and hydraulic resistance of the xylem', 14100/2.57),
        k_Rxyl_2  = param('parameter 2 in allometric relation between tree height and hydraulic resistance of the xylem', 0.5838) ,
        k_Rsoil_1 = param('parameter 1 in allometric relation between soil water potential and hydraulic resistance of the soil-roots path', 271824/2.57),
        k_Rsoil_2 = param('parameter 2 in allometric relation between soil water potential and hydraulic resistance of the soil-roots path', 3.063),
        ):
        '''leaf water potential estimate by a simple RC model.
        C is the water capacitance - supposed to be connected on foliage
        R is the sum of soil-root and tree resistances
        '''

        _canopy = self.canopy
        _soilWaterPotential = self.soil.waterCycle.RootLayerWaterPotential

        if self.W >0 :
            #hydraulic resistances in soil ansd xyleme (MPa m2_LAI s kg_H2O-1)
            RhydSoil = k_Rsoil_1*(-_soilWaterPotential)**k_Rsoil_2
            RhydXyl= k_Rxyl_1*self.HEIGHTmean**k_Rxyl_2

            Rhyd=RhydXyl+RhydSoil

            #global capacitance (kg_H2O m-2__leaf MPa-1)
            C=0.07*(self.W/13)**1#0.14

            #new leaf water potentiel
            _eRC = exp(-3600/(Rhyd*C))
            _canopy.WaterPotential = (_soilWaterPotential- _canopy.Transpiration*Rhyd/3600.0/_canopy.LAI)*(1-_eRC)+_canopy.WaterPotential *_eRC

            #soil-roots interface water potential
            self.SoilRootsWaterPotential= (_soilWaterPotential *RhydXyl+ _canopy.WaterPotential * RhydSoil) / Rhyd

        else:
            _canopy.WaterPotential = self.SoilRootsWaterPotential = _soilWaterPotential



    # RESPIRATION
    Rm = var('Respiration part linked to the tissues maintenance (without leaves) (g C /m2_soil /hour)')
    Rg = var('Respiration part linked to the tissues production (growth)  (g C /m2_soil /hour)')
    R_AboveGround = var('Part of the respiration exhausted above soil (g C /m2_soil /hour)')
    R_UnderGround = var('Part of the respiration exhausted under soil (g C /m2_soil /hour)')
    Annual_Rg=var('Annual growth respiration (g_C /m2_soil /year)', 0.)

    @pcs
    def pcs_Respiration(self,
        RmQ10 = param('Q10 of maintenance respiration', 2.13),
        ):
        '''Respiratory carbon fluxes.
            - the model is based on the classical partitionning of respiration between maintenance and growth components
        '''

        if self.sunTime.isYearBeginning and self.W>0:
            #evaluate the base maintenance respiration at 15deg_C (trunk + bches ,LEN 2003, Bilan C bray)
            self._Rm15_TrunkBranches = sum([_tree.Rm15 for _tree in self])/ self.Area
            self._Rm15_Roots = self._Rm15_TrunkBranches * self.Wr / self.Wa

        if self.W>0:
            #Maintenance respiration  (g_C /m2_soil /hour)
            _Rm_AboveGround =  self.canopy.Respiration + self._Rm15_TrunkBranches * RmQ10 ** ((self.microclim.TaC - 15.0) / 10.0)
            _Rm_UnderGround = self._Rm15_Roots * RmQ10 ** ((self.soil.carbonCycle.Ts_resp - 15.0) / 10.0)
            self.Rm =  _Rm_AboveGround + _Rm_UnderGround

            #Growth respiration  (g_C /m2_soil /hour)
            #BE CAREFULL : for the moment growth assimilation is based on last year growth
            self.Rg = self.Annual_Rg * (self.GrowthIntensity / 24.0)

            #Above and Under ground partition of respiration
            _Rg_UnderGround = self.Rg * self.AllocRoot
            _Rg_AboveGround = self.Rg - _Rg_UnderGround
            self.R_AboveGround = _Rm_AboveGround + _Rg_AboveGround
            self.R_UnderGround = _Rm_UnderGround + _Rg_UnderGround

        else:
            self.Rm = self.Rg = self.R_AboveGround = self.R_UnderGround =0


    #SENESCENCE
    BranchSenescence = var('branch biomass leave by senescence (Kg_DM /m2_soil /year)')
    RootSenescence = var('root biomass leave by senescence (Kg_DM /m2_soil /year)')

    @pcs
    def pcs_Senescence(self,
        k_SenBch_1 = param('coefficient 1 of allometric equation to calculate branches senescence', 0.3678),
        k_SenBch_2 = param('coefficient 2 of allometric equation to calculate branches senescence', 1.0966) ,
        k_SenBch_3 = param('coefficient 3 of allometric equation to calculate branches senescence', -1.256) ,
        k_SenRoot_1 = param('coefficient 1 of allometric equation to calculate roots senescence', 0.8),
        k_SenRoot_2 = param('coefficient 2 of allometric equation to calculate roots senescence', 0.5),
        k_SenRoot_3 = param('coefficient 3 of allometric equation to calculate roots senescence', 0),
        ):

        if self.sunTime.isYearBeginning :
            #short names
            _Age_aerial = self.Age_aerial
            _Age = self.Age

            #trees branches senescence (Kg_DM /tree /year) and stand cumul (Kg_DM /m2_soil /year)
            _sum =  0.
            for _tree in self:
                _branchSenescence =  k_SenBch_1 * (_tree.Wa **k_SenBch_2) * (_Age_aerial **k_SenBch_3)
                _tree.BranchSenescence = _branchSenescence
                _sum += _branchSenescence

            self.BranchSenescence = _sum / self.Area

            #trees roots senescence (Kg_DM /tree /year) and stand cumul (Kg_DM /m2_soil /year)
            _sum =  0.
            for _tree in self:
                _rootSenescence = k_SenRoot_1 * (_tree.Wr /(1+_tree.Wr**(1 - k_SenRoot_2))) * (_Age **k_SenRoot_3)
                _tree.RootSenescence = _rootSenescence
                _sum += _rootSenescence

            self.RootSenescence = _sum / self.Area


    #HYDRIC STRESS
    IStress = var('Hydric stress indicator used for root/shoot allocation ([0-1])', 0.)

    @pcs
    def pcs_HydricStress(self):

        if self.sunTime.isYearBeginning:
            self._annual_Transpiration_effective = 0
            self._annual_Transpiration_unStress = 0

        #cumulate transpirations for annual stress evaluation
        _canopy = self.canopy
        if _canopy.Transpiration > 0 and _canopy.LAI>0 and _canopy.g_stom_unstress>0 and _canopy.Gsa>0:
            self._annual_Transpiration_effective +=  _canopy.Transpiration

            #unstress  LE
            _Gsa_unstress = 1 / (1 / _canopy.Ga + 1 / (_canopy.LAI*_canopy.g_stom_unstress))
            _Transpiration_unstress = _canopy.Transpiration * _Gsa_unstress/_canopy.Gsa
            self._annual_Transpiration_unStress +=  _Transpiration_unstress

        #calculate an annual stress indice (transpiration limitation) used to pilote carbon allocation
        if self.sunTime.isYearEnd :
            if self._annual_Transpiration_unStress>0:
                self.IStress = max(0, 1 - (self._annual_Transpiration_effective / self._annual_Transpiration_unStress))
            else:
                self.IStress = 0


    #CARBON FLUXES PARTIONNING
    AllocRoot = var('part of biomass increment allocate to roots [0-1] (Kg_DM /Kg_DM)', 0.3)

    @pcs
    def pcs_CarbonFluxesPartition(self,
        kIstress_1 = param('coefficient 1 of stress index expression', 0.2),
        kIstress_2 = param('coefficient 2 of stress index expression',0.5),
        kIstress_3 = param('coefficient 3 of stress index expression',1),
        RgCost  = param('carbon growth cost  (g_C /g_C)', 0.28),
        BiomassCarbonContent = param('carbon content of dry biomass (g_C /Kg_DM)', 480),
        ):

        if self.sunTime.isYearBeginning:
            self._annualSum_Assimilation = 0
            self._annualSum_Rm = 0

        #Annual integration
        self._annualSum_Assimilation +=  self.canopy.Assimilation
        self._annualSum_Rm +=  self.Rm

        if self.sunTime.isYearEnd:
            #aerial / shoot carbon allocation from Istress
            self.AllocRoot = kIstress_1 * exp(kIstress_2 * self.IStress ** kIstress_3)

            #carbon flux partitionning between trees in proportion to their tissues size implicated in the processes
            #and between roots and aerial compartment in function of AllocRoot
            annual_Assimilation_By_LeafWeight = (self._annualSum_Assimilation * self.Area) / sum(_tree.LeafWeight for _tree in self) if len(self)>0 else 0
            annual_Rm_By_TreeRm15 = (self._annualSum_Rm * self.Area) / sum(_tree.Rm15 for _tree in self) if len(self)>0 else 0
            k_Carbon2Growth = 1/(1+RgCost) /BiomassCarbonContent

            for _tree in self :
                tree_Annual_Assimilation = _tree.LeafWeight * annual_Assimilation_By_LeafWeight
                tree_Annual_Rm = _tree.Rm15 * annual_Rm_By_TreeRm15

                tree_Wproducted = (tree_Annual_Assimilation - tree_Annual_Rm) * k_Carbon2Growth
                _tree.WrProducted = tree_Wproducted * self.AllocRoot
                _tree.WaProducted = tree_Wproducted - _tree.WrProducted

                _tree.update()

            #Annual Rg respiration for next year. An evolution would be to evaluate that during the year in function of growth
            self.Annual_Rg = (self._annualSum_Assimilation - self._annualSum_Rm ) * RgCost/(1+RgCost)

            #mean dimensions
            self.pcs_SetSizes()


    #BIOMASSES AND SIZES
    density = var('number of trees per hectare (tree /ha)')

    W = var('biomass (Kg_DM /m2_soil)')
    Wa = var('aerial biomass (Kg_DM /m2_soil)')
    Wr = var('root biomass (Kg_DM /m2_soil)')
    Wstem = var('stem biomass (Kg_DM /m2_soil)')

    WProducted = var('annual increment of biomass (Kg_DM /m2_soil /year)')
    WaProducted = var('annual increment of aerial biomass (Kg_DM /m2_soil /year)')
    WrProducted = var('annual increment of root biomass (Kg_DM /m2_soil /year)')

    DBHdom = var('mean tree DBH of the 100 bigger trees by hectare (m)')
    HEIGHTdom = var('mean tree height of the 100 bigger trees by hectare (m)')

    @pcs
    def pcs_SetSizes(self):
        '''Dimensions integrated from trees list'''

        #Biomass and biomass increments by soil area unit (kg_DM /m2_soil)
        self.Wa = sum(_tree.Wa for _tree in self) / self.Area
        self.WaProducted = sum(_tree.WaProducted for _tree in self) / self.Area

        self.Wr = sum(_tree.Wr for _tree in self)/ self.Area
        self.WrProducted = sum(_tree.WrProducted for _tree in self)/ self.Area

        self.W = self.Wa + self.Wr
        self.WProducted = self.WaProducted + self.WrProducted

        #Stem wood production
        self.Wstem = sum(_tree.Wstem for _tree in self)/ self.Area

        #Mean tree sizes
        Trees.update(self)
        self.density = self.treesCount*10000./self.Area

        if self.treesCount>0:
            #Dominant trees (100 bigger by hectare)
            _Ndom = round(100 * self.Area / 10000., 0)
            _biggerTrees = sorted(self,  key = (lambda tree: tree.DBH), reverse = True)[:int(_Ndom)]

            #Dimension of the dominant trees (100 bigger by hectare)
            self.DBHdom =  sum(_tree.DBH for _tree in _biggerTrees)/_Ndom
            self.HEIGHTdom =  sum(_tree.Height for _tree in _biggerTrees)/_Ndom

        else :
            self.DBHdom = 0
            self.HEIGHTdom =  0


    #TODO put these process on Manager
    @pcs
    def pcs_TreeStandInstallation(self,
        initialTreesAge = param('Age of trees to install',10),
        initialTreesDimensionsFile = param('file path of trees dimensions', ''),
        initialTreesDensity = param('trees density (tree /ha)', 1600),
        initialTreesWa_avg = param('mean of initial trees  Wa(Kg_DM /tree)', 25)  ,
        initialTreesWa_std = param('st. dev. of initial trees  Wa(Kg_DM /tree)', 8),
        initialTreesWrOnWa_avg = param('mean of initial trees  Wr/Wa ratio (Kg_DM /tree)', 0.15),
        initialTreesWrOnWa_std = param('st. dev. of initial trees  Wr/Wa ratio (Kg_DM /tree)', 0.015),
        ):

        #create the trees
        if initialTreesDimensionsFile !=  '':
            #from a file containing individual tree Wa and Wr (old file format of GRAECO Visual Basic)
            self._install_trees_from_file_definition( initialTreesAge,  initialTreesDimensionsFile )
        else:
            if initialTreesDensity >0:
                #from dimension distributions
                self._install_trees_from_gauss_distribution( initialTreesAge, initialTreesDensity,  initialTreesWa_avg,  initialTreesWa_std,  initialTreesWrOnWa_avg,  initialTreesWrOnWa_std)


    def _install_trees_from_gauss_distribution(self,
       trees_Age=10, nbTreesHa=1600,
       trees_Wa_avg=25.0,
       trees_Wa_std =8.0,
       trees_WrOnWa_avg = 0.15,
       trees_WrOnWa_std = 0.015,
       ):
        '''Do a tree plantation at the specified _germinationYear and with
            trees dimension randomly defined from aerial biomass distribution and roots on shoot  ratio distribution
        '''

        #initialize the random generator
        _nbTrees = int(nbTreesHa * self.Area*1e-4)
        random.seed(_nbTrees)

        #randomly choose trees dimensions (Wa, Wr)
        _trees_dim = []
        for i in range(_nbTrees):
            _tree_Wa = min(max(random.gauss(trees_Wa_avg, trees_Wa_std),  trees_Wa_avg*0.1),  trees_Wa_avg*1.9)
            _tree_Wr = _tree_Wa *min(max(random.gauss(trees_WrOnWa_avg, trees_WrOnWa_std),  trees_WrOnWa_avg*0.1),  trees_WrOnWa_avg*1.9)
            _trees_dim += [(_tree_Wa, _tree_Wr)]

        #create the trees with
        self._include_trees(trees_Age,_trees_dim)


    def _install_trees_from_file_definition(self,
        trees_Age = 0.0,
        treesFileName = '',
        ):
        '''Initialisation step'''

        #Read trees file definition content
        _file = open(treesFileName, 'r')
        _lines = _file.readlines()
        _file.close()

        #remove  lines until trees section
        while _lines.pop(0).strip() != '[Begin - Trees]':
            pass

        #read trees dimension
        _trees_dim = []
        while _lines[0].strip() != '[End - Trees]':
            _line = _lines.pop(0).strip()
            _sName, _sWa, _sWr = _line.split('\t')[0:3]
            _trees_dim += [( float(_sWa), float(_sWr))]

        #create and initialize a tree
        self._include_trees(trees_Age,_trees_dim)


    def _include_trees(self,
       trees_Age=10,
       trees_WaWr_list =[(10, 3), ],
       ):
        '''include trees of stand from their dimensions'''

        if len(self)>0 :
            raise Exception("treeStand ELT  don't support the installation of trees if not empty")

        #treedStand temporallity reinitialisation
        self.Age = trees_Age
        self._germinationYear = self.sunTime.Y -  self.Age + 1
        self.ClumpAge = 0.
        self.Age_aerial = self.Age

        for _t_dim in trees_WaWr_list:
            #create a tree object, link it to other model objects and do its initialisation
            _tree=TreeSizes(self)
            _tree.sunTime = self.sunTime
            (_tree.Wa, _tree.Wr) = _t_dim
            _tree.update()

            self.add(_tree)

        #update some integrative treeStand properties
        self.pcs_SetSizes()


    def _exclude_tree(self, tree_to_remove):
        self.remove(tree_to_remove)

        #update some integrative treeStand properties
        self.pcs_SetSizes()
