from ...goBases import *

#from .Canopy.mdlBigLeafCanopySurface import BigLeafCanopySurface as Canopy
from .Canopy.mdlSunShadeFarquhar_CanopySurface import SunShadeCanopySurface as Canopy


class ugCompartment(ELT):

    #Biomass
    W = var('dry biomass (Kg_DM /m2_soil)', 0) #variable
    AboveGroundFraction = param('fraction of the compartment biomass above ground',  1)
    CarbonFraction = param('carbon weight fraction of dry biomass (Kg_C /Kg_DM)',  0.5)

    #Growth
    Growth = var('dry biomass production (Kg_DM /m2_soil /day)', 0) #variable
    GrowthMax = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)', 0.6)
    SMD_Limiting_growth = param('SMD limiting growth', 0.7)

    #Growth pcs_Phenology
    GrowthStart  = var('day of year of growth start (DOY [1-366])') #variable
    HeatSum_GrowthStart = param('Annual heat-sum to start growth (deg day)', 250)
    GrowthLength = param('Growth length of leaf (day)', 270)

    #Mortality parameters
    LitterFall = var('dry biomass litterfall (Kg_DM /m2_soil /day)', 0.) #variable
    k_MortalityTemp = param('Mortality temperature threshold (deg_C)', 0)
    k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)', 0.1)
    k_MortalitySMD = param('Mortality SMD  threshold', 0.85)
    k_MortalitySMDRate = param('SMD mortality rate (Kg_DM /Kg_DM /day)', 0.025)
    k_MortalityDOY = param('DOY threshold [1-365]', 315)
    k_MortalityDOYRate = param('DOY mortality rate (Kg_DM /Kg_DM /day)', 0.05)
    DPM_RPM_rate= param('rate of DPM on RPM fraction of litterfall (Kg_DM /Kg_DM)',  1.44)
    LitterFallAge = param('mean litterfall age (Kg_DM /Kg_DM)',  0.5)

    #Non structural carbohydrate pools
    Cpool = var('non structural carbohydrate pool (g_C /m2_soil)', 25) #variable

    #pcs_Respiration parameters
    RmQ10 = param('Q10 factor of maintenance respiration response to temperature', 2.13)
    Rm15 = param('Maintenance respiration at 15degC (g_C /Kg_Dm /hour)',  0.013)
    RgCost = param('respiration cost of growth (gC /g_C)', 0.28)
    kW_Rm = param('power coefficient of maintenance respiration proportionnality to  biomass (1: proportionnal to volume,  0.666 proportional to surface in case of sphere)', 1)


class UnderStorey(ELT):
    '''Represent the under growth vegetation layer (typicaly  Molinea coerulea)'''

    #Outer elements
    sunTime = eltOut('SunTime element')
    microclim = eltOut('Upper MicroClimate element')
    microclim_under =eltOut('Under MicroClimate element')
    soil = eltOut('Soil element')

    #Inner model elements
    @eltIn
    class foliage(ugCompartment):
        k_MortalitySMD = param('Mortality SMD  threshold', 0.84)

    @eltIn
    class roots(ugCompartment):
        AboveGroundFraction = param('fraction of the compartment biomass above ground',  0)
        k_MortalitySMD = param('Mortality SMD  threshold', 0.85)
        LitterFallAge = param('mean litterfall age (Kg_DM /Kg_DM)',  2.)
        k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)', 0.0125)

    @eltIn
    class perennial(ugCompartment):
        W = var('dry biomass (Kg_DM /m2_soil)', 0.1)
        AboveGroundFraction = param('fraction of the compartment biomass above ground',  0.15)
        GrowthMax = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)', 0.4)
        k_MortalityTemp = param('Mortality temperature threshold (deg_C)', -8)
        k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)', 0.025)
        k_MortalitySMD = param('Mortality SMD  threshold', 0.895)
        k_MortalitySMDRate = param('SMD mortality rate (Kg_DM /Kg_DM /day)', 0.003)
        k_MortalityDOY = param('DOY threshold [1-365]', 0)
        k_MortalityDOYRate = param('DOY mortality rate (Kg_DM /Kg_DM /day)', 0.001)
        Cpool = var('non structural carbohydrate pool (g_C /m2_soil)', 50)

    @eltIn
    class canopy(Canopy):

        pcs_StomatalConductance = pcs(Canopy.pcs_StomatalConductance,
            g_stom_Max = param('maximal stomatal conductance (m/s)', 0.0062 * 2),
            k_Rsabs_P50 = param('Leaf solar radiation absorded for 50%  of stomatal conductance ponderation (W /m2_LAI)', 69.94) , #TODO : change value to be consistent with previous
            k_Rsabs_Curv = param('Curvature parameter of radiative ponderation of stomatal conductance (-)', 1.13), #TODO : change value to be consistent with previous
            k_VPD_P100 = param('VPD that start to close stomata (Pa)', 728), #TODO : change value to be consistent with previous
            k_VPD_Curv = param('Curvature parameter of VPD ponderation of stomatal conductance (-)',1.08), #TODO : change value to be consistent with previous
            k_Yleaf_P0 = param('parameter 1 of leaf water potential ponderation of stomatal conductance (MPa)',-2.0),
            k_Yleaf_Curv = param('parameter 2 of leaf water potential ponderation of stomatal conductance (-)',0.5),
            k_time_P50 = param('ponderation of time response to stationnary state of stomatal conductance ]0-1]', 0.8),
            )

        pcs_ShortWaveBalance = pcs(Canopy.pcs_ShortWaveBalance,
            rho_l = param('Leaf reflection coefficient for shortwave (_)', 0.15),
            theta_l  = param('Leaf transmissivity for shortwave (_)', 0.02),
            )

        pcs_EnergyBalance = pcs(Canopy.pcs_EnergyBalance,
            kLAI1_Rth_Int = param('parameter 1 of longwave radiation interception (-)',  -0.538),
            kLAI2_Rth_Int = param('parameter 2 of longwave radiation interception (-)', 0.0177),
            Emissivity = param('emissivity', 0.98),
            )

        pcs_CanopyRainInterception = pcs(Canopy.pcs_CanopyRainInterception,
            kRainInt_LAI = param('parameter of rain interception by leaf (-)',  -0.33),
            SurfaceWaterStorageCapacity = param('water storage capacity by leaf area index(Kg_H2O /m2_leafAreaIndex)', 0.125 * 2),
            )

        pcs_AssimilationFarquhar = pcs(Canopy.pcs_AssimilationFarquhar,
            Vcmax_25 = param('Vcmax at TCref, expressed on a one-sided leaf area basis (mol_CO2 /m2_leaf /s))',  40.9e-6),   #Delzon 2000 [p 18] (mean of all stages and two traitements)
            Ea_Vcmax = param('Activation energy for Vcmax (J /mol)', 58750.),  #Delzon 2000 [p j]
            Jmax_25 = param('Jmax at TCref, expressed on a one-sided leaf area basis (mol_e /m2_leaf /s', 54.6e-6),#Delzon 2000 [p 18] (mean of all stages and two traitements)
            Ha_Jmax = param('Activation energy for Jmax (J /mol)', 56000.),  #Delzon 2000 [p j]
            Hd_Jmax = param('Deactivation energy for Jmax (J /mol)', 202800.),  #Delzon 2000 [p j]
            alpha = param('Quantum yield of electron transport (mol_e /mol_photon_absorbed). \
                Litterature value obtained on Rs intercepted need to be corrected for leaf absorbance', 0.168/0.9),  #Delzon 2000 [p 18] (mean of all stages and two traitements)
            Rd_25 = param('Dark leaf respiration at 25 degC (mol_CO2 /m2_LAI /s)',  0.8e-6 * 54.6/154.74),  #without reference use same ratio to Jmax than for pine
            )

    def update(self):
        '''hourly update
        '''
        #SIMULATION INITIALISATIONS
        if self.sunTime.isSimulBeginning:
            #connect the inner ELT
            self.canopy.sunTime = self.sunTime
            self.canopy.microclim = self.microclim
            self.canopy.microclim_under = self.microclim_under
            self.canopy.soil = self.soil

            self.pcs_AllometricDimensions()

        #Canopy processes
        self.canopy.update()

        #Water balance processes
        self.pcs_HydraulicStatus()
        self.pcs_Respiration()

        #plantdevelopment
        self.pcs_Phenology()
        self.pcs_Growth()
        self.pcs_AllometricDimensions()
        self.pcs_AllocateLitterCarbonToSoil()


    #DIMENSIONS ALLOMETRICALY LINKED TO COMPARTMENT BIOMASS
    #vars
    HEIGHTmean   = var('height (m)')
    density = privar('plant per hectare (plant /ha)', 3000.)

    @pcs
    def pcs_AllometricDimensions(self,
        SLA = param('specific leaf area (m2_LAI /Kg_DM)', 20),
        Height_max = param('maximal height (m)', 0.8),
        kAerialWeight_Height = param('allometric coefficient of relation between aerial weight and height', 5.),
        ):
        '''Evaluate dimensions  allometricaly linked to compartment biomass'''

        #LAI  (m2_LAI /m2_soil)
        self.canopy.LAI = SLA * self.foliage.W

        #Height (m)
#            self.HEIGHTmean = Height_max * (1 - exp(- kAerialWeight_Height * self.perennial.W * self.perennial.AboveGroundFraction))
        self.HEIGHTmean = Height_max * (1 - exp(- kAerialWeight_Height * self.foliage.W ))

        #density : Be carreful , it's just an order value used for aerodynamic dimension evaluation
        self.density= 1500*self.canopy.LAI


    @pcs
    def pcs_HydraulicStatus(self):
        '''leaf water potential estimate by a simple RC model.
        C is the wter capacitance - supposed to be connected on foliage
        R is the sum of the resistance of soil and plant
        '''
        _canopy = self.canopy
        _soilWaterPotential = self.soil.waterCycle.RootLayerWaterPotential

        if _canopy.LAI>0.0001:

            #soil leaf hydraulic resistance (MPa m2_leaf s kg_H2O-1)
            Rhyd=10000#80000
            #Capacitance (kg_H2O m-2__leaf MPa-1)
            C=0.01#0.14

            _eRC = exp(-3600/(Rhyd*C))

            #new leaf water potentiel
            _canopy.WaterPotential = (_soilWaterPotential - _canopy.Transpiration*Rhyd/3600.0/_canopy.LAI)*(1-_eRC)+_canopy.WaterPotential *_eRC

        else:
            _canopy.WaterPotential = _soilWaterPotential


    # RESPIRATION
    Rm = var('maintenance respiration (without leaves) (g_C /m2_soil /hour)')
    Rg = var('growth respiration (g_C /m2_soil /hour)')
    R_AboveGround = var('aboveground part of respiration  (g_C /m2_soil /hour)')
    R_UnderGround = var('underground part of respiration (g_C /m2_soil /hour)')

    @pcs
    def pcs_Respiration(self):
        '''Respiratory carbon fluxes.
            - the model is based on the classical partitionning of respiration between maintenance and growth components
            - estimation of the two respiration componants  for each compartment (foliage, roots, perennial)(g_C /m2_soil /hour)
            - distribute on AboveGround and Underground composantes
            - decrease carbon pool
        '''

        #initialisation
        (self.Rm, self.Rg,  self.R_AboveGround,  self.R_UnderGround) = (0, 0, 0, 0)

        #Evaluation of respiration components by compartment. Cumuls on maintenance/growth and AboveGround/UndeGround  fractions
        for _cpt in (self.foliage, self.roots, self.perennial):
            #maintenance respiration. For above and under ground parts , the temperature of air or of soil are used respectively
            _cpt_Rm_A = _cpt.AboveGroundFraction * (_cpt.W ** _cpt.kW_Rm) * _cpt.Rm15 * _cpt.RmQ10 ** ((self.microclim.TaC - 15.0) / 10.0)
            _cpt_Rm_U = (1 - _cpt.AboveGroundFraction) * (_cpt.W ** _cpt.kW_Rm) * _cpt.Rm15 * _cpt.RmQ10 ** ((self.soil.carbonCycle.Ts_resp - 15.0) / 10.0)
            self.Rm += _cpt_Rm_A +_cpt_Rm_U

            # growth respiration
            _cpt_Rg =  (_cpt.Growth / 24.0) * _cpt.CarbonFraction * 1000 * _cpt.RgCost
            self.Rg += _cpt_Rg

            #above and under ground respiration parts
            self.R_AboveGround += _cpt_Rm_A + _cpt_Rg * _cpt.AboveGroundFraction
            self.R_UnderGround += _cpt_Rm_U + _cpt_Rg * (1-_cpt.AboveGroundFraction )

            #Cpool
            _cpt.Cpool -=  (_cpt_Rm_A  + _cpt_Rm_U  + _cpt_Rg)


    #PHENOLOGY
    @pcs
    def pcs_Phenology(self):
        ''' For eah compartment, determine when cumulative temperature reach the  level to start growth
        '''

        #update the heat sums used for phenology outbreak
        if self.sunTime.isYearBeginning:
            self._HeatSum_air = 0
            self._HeatSum_soil = 0
            for _cpt in (self.foliage, self.roots,  self.perennial):
                _cpt.GrowthStart = 9999

        self._HeatSum_air  += self.microclim.TaC / 24.0
        self._HeatSum_soil += self.soil.carbonCycle.Ts_resp / 24.0

        #daily test phenology start
        if self.sunTime.isDayEnd:
            for (_cpt, _HeatSum) in ((self.foliage, self._HeatSum_air), (self.roots, self._HeatSum_soil), (self.perennial, self._HeatSum_air)):
                if _HeatSum >= _cpt.HeatSum_GrowthStart and _cpt.GrowthStart > self.sunTime.DOY :
                    _cpt.GrowthStart = self.sunTime.DOY


    @pcs
    def pcs_Growth(self,
        k_Alloc_P = param('Allocation rate to perennial [0-1]', 0.05),
        ):
        ''' For eah compartment, determine growth components:
            - GPP allocation to carbon pool, use of it for
            - Growth (dry biomass production)
            - Literfall production
            - new biomass
        '''

        #Each year add inconditionnality a very little  quantity in Cpool to mimic natural seeding
        if self.sunTime.isYearBeginning:
            for _cpt in (self.foliage, self.roots,  self.perennial):
                _cpt.Cpool +=0.5

        #construct daily variables
        if self.sunTime.isDayBeginning:
            self._Daily_GPP = 0
            self._Daily_Tmin = 9999

        self._Daily_GPP += self.canopy.Assimilation
        self._Daily_Tmin = min(self._Daily_Tmin, self.microclim.TaC)

        #daily development
        if self.sunTime.isDayEnd:
            _RedistributedCpool = 0.0
            for _cpt in (self.foliage, self.roots, self.perennial):
                 _RedistributedCpool +=_cpt.Cpool
                 _cpt.Cpool =0.0

            _CpoolStress = 500 * self.Rm

            if _RedistributedCpool < _CpoolStress:
                _MortalityCpool = (1-_RedistributedCpool/_CpoolStress)**2
            else:
                _MortalityCpool=0

            for _cpt, _Alloc in (
                                 (self.foliage, 0.48),
                                 (self.perennial, k_Alloc_P),
                                 (self.roots, 1 - 0.48 - k_Alloc_P)
                                 ):

                #tissue production (in function of soil water limitation)
                if self.soil.waterCycle.MoistureDeficit < _cpt.SMD_Limiting_growth :
                    _dS = dSigmoide(self.sunTime.DOY, _cpt.GrowthLength, _cpt.GrowthStart, 0.001)
                    _cpt.Growth= max(
                                                    0,
                                                    min(
                                                            _cpt.GrowthMax * _dS,
                                                           (_RedistributedCpool-_CpoolStress)* _Alloc / _cpt.CarbonFraction *0.001
                                                            )
                                                    )/(1+_cpt.RgCost)
                else :
                    _cpt.Growth= 0

                #mortality  (Kg_DM /m2_soil /day) : effect of low temperature, high SMD and senescence
                _cpt.LitterFall = _cpt.W *max (
                                                            _cpt.k_MortalityTempRate if (self._Daily_Tmin <= _cpt.k_MortalityTemp) else 0,
                                                            _cpt.k_MortalitySMDRate if  (self.soil.waterCycle.MoistureDeficit >= _cpt.k_MortalitySMD) else 0,
                                                            _cpt.k_MortalityDOYRate if  (self.sunTime.DOY >= _cpt.k_MortalityDOY) else 0,
                                                            _MortalityCpool
                                                                )

                #new biomass
                _cpt.W += _cpt.Growth - _cpt.LitterFall

                #New carbon pool
                _cpt.Cpool +=  _Alloc *( self._Daily_GPP + _RedistributedCpool) - _cpt.Growth * _cpt.CarbonFraction * 1000


    @pcs
    def pcs_AllocateLitterCarbonToSoil(self):
        '''Add compartment litter to soil carbon incoming'''

        if self.sunTime.isDayEnd:
            for _cpt in (self.foliage,  self.roots,  self.perennial):
                self.soil.carbonCycle.incorporateACarbonLitter(_cpt.LitterFall *1000*_cpt.CarbonFraction, _cpt.DPM_RPM_rate, _cpt.LitterFallAge)
