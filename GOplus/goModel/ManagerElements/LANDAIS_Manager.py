## MANAGER PRACTICES defined for FAST project simulations
## A. Bosc
## 2013-05-23
from . import mdlManager
import math


class Manager(mdlManager.Manager):

    def do_managment(self):
        #Sequence of the interventions
        _rotationYear=self.rotationYear()

        if _rotationYear==3:
            self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5, soilPerennialFractionAffected = 0.95)
            self.do_install_stand( 2, 1600)

        if _rotationYear == 8 : self.do_standard_respacing( 1200)
        if _rotationYear == 15 : self.do_standard_thinning( 828)
        if _rotationYear == 20 : self.do_standard_thinning( 621)
        if _rotationYear == 25 : self.do_standard_thinning( 525)
        if _rotationYear == 30 : self.do_standard_thinning( 371)
        if _rotationYear == 35 : self.do_standard_thinning( 290)
        if _rotationYear == 45 : self.do_standard_thinning( 0)


    def rotationYear(self) :
        '''year in the rotation. Return a value only if isYearEnd.  Suppose :
            - even-aged trees
            - 1 year of bare ground between 2 successive stands
        '''
        if self.locTime.isYearEnd:
            if len(self.forest.treeStand)>0:
                return self.forest.treeStand.Age +1
            else:
                try:
                    return self.locTime.Y - self.lastThinningYear
                except:
                    return 0.0
        else:
            return -9999.9



##    def isEndYear(self, Y) :
##        ''' Return True if isYearEnd of Y.
##        '''
##        if self.locTime.isYearEnd and self.locTime.Y == Y :
##            return True
##        else:
##            return False


    ###########################################################
    ###UNITARY INTERVENTIONS        ######################################
    ###########################################################

    def do_rouleau_Landais(self):
        ''' A light plow preceding intervention in the stand
        '''
        _AF = 0.75 #areaFractionPlowed
        _Wp_obj= 0.025 #perennial biomass objective

        _UG = self.forest.underStorey

        #intensity of the plow (soilPerennialFractionAffected) to the objective
        _PFA = ((1- _Wp_obj/_UG.perennial.W)/_AF - _UG.perennial.AboveGroundFraction)/(1- _UG.perennial.AboveGroundFraction)
        _PFA =max(0, min(_PFA, 1))

        self.do_plow(
                areaFractionPlowed = _AF,
                soilCarbonFractionAffected = 0.15,
                soilPerennialFractionAffected =_PFA,
                )

    def do_marquage_par_le_bas(self, nbTrees):
        ''' the classic thinning selection for pine_ from Bray
        '''
        self.do_markRandomLogging(
                randomFactor=4.3473626E+00*math.exp(-1.0525463E-03*nbTrees),
                densityObjective = nbTrees,
                )

    def do_standard_respacing(self, nbTrees):
        ''' A very early thinning operation to reduce the number of trees per unit area.
            Normally executted  as first thinning when initial trees number is large,
            typically on a stand  outcome of a sowing.
            A light soil plow is realized to allow stand accessibility.
            None biomass is exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = False,
                harvestStub = False,
                harvestCrownWood = False,
                harvestTaproot = False, 
                harvestNeedles = False, 
                )
        self.lastThinningYear= self.locTime.Y


    def do_standard_thinning(self, nbTrees):
        ''' Do a thinning operation to reduce the number of trees per unit area and harvest stem wood.
            Normally executed  periodically to limit tree competition.
            A light soil plow is realized to allow stand accessibility.
            Stem biomass is exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = True,
                harvestStub = False,
                harvestCrownWood = False,
                harvestTaproot = False, 
                harvestNeedles = False, 
                )
        self.lastThinningYear= self.locTime.Y


    def do_aerial_biomass_thinning(self, nbTrees):
        ''' Do a thinning operation to reduce the number of trees per unit area.
            Normally executed  periodically to limit tree competition.
            A light soil plow is realized to allow stand accessibility.
            Stem and crown biomass are exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = True,
                harvestStub = False,
                harvestCrownWood = True,
                harvestTaproot = False, 
                harvestNeedles = False, 
                )
        self.lastThinningYear= self.locTime.Y


    def do_intensive_biomass_thinning(self, nbTrees):
        ''' Do a thinning operation to reduce the number of trees per unit area.
            Normally executed  periodically to limit tree competition.
            A light soil plow is realized to allow stand accessibility.
            Stem, crown and taproot biomass are exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = True,
                harvestStub = False,
                harvestCrownWood = True,
                harvestTaproot = True, 
                harvestNeedles = False, 
                )
        self.lastThinningYear= self.locTime.Y

    def do_all_woody_thinning(self, nbTrees):
        ''' Do a thinning operation to reduce the number of trees per unit area.
            Normally executed  periodically to limit tree competition.
            A light soil plow is realized to allow stand accessibility.
            All trees woody biomass is exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = True,
                harvestStub = True,
                harvestCrownWood = True,
                harvestTaproot = False, 
                harvestNeedles = False, 
                )
        self.lastThinningYear= self.locTime.Y
        
    def do_all_biomass_thinning(self, nbTrees):
        ''' Do a thinning operation to reduce the number of trees per unit area.
            Normally executed  periodically to limit tree competition.
            A light soil plow is realized to allow stand accessibility.
            All trees biomass is exported.
        '''
        self.do_rouleau_Landais()
        self.do_marquage_par_le_bas(nbTrees)
        self.do_Logging(
                harvestStem = True,
                harvestStub = True,
                harvestCrownWood = True,
                harvestTaproot = False, 
                harvestNeedles = True,
                )
        self.lastThinningYear= self.locTime.Y


    def do_install_stand(self, trees_Age, nbTreesHa):
        '''Do a tree plantation at the specified density
        '''
        #from pinus pinaster root-shoot ratio obtain on dataset furnished by Trichet P (parcelle L12ans &18ans, Bilos 50ans, parcelle M 63 ans)
#        _trees_Wa_avg = 0.2146*trees_Age**2.0481
#        _trees_Wa_avg = 0.1793*trees_Age**2.2708
        _trees_Wa_avg = math.exp( -0.336354*math.log(trees_Age)**2 + 3.742828*math.log(trees_Age) - 3.108378) #version FAST
        _trees_WrOnWa_avg =0.085365*_trees_Wa_avg**0.176316

        self.forest.treeStand._install_trees_from_gauss_distribution(
                                                                     trees_Age = trees_Age,
                                                                     nbTreesHa = nbTreesHa,
                                                                     trees_Wa_avg = _trees_Wa_avg,
                                                                     trees_Wa_std =_trees_Wa_avg * 0.4,
                                                                     trees_WrOnWa_avg = _trees_WrOnWa_avg,
                                                                     trees_WrOnWa_std = _trees_WrOnWa_avg*0.1
                                                                     )
