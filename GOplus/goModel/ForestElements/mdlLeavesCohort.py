from ...goBases import *


class LeavesCohort(ELT):

    #Outer elements
    sunTime = eltOut('SunTime element')
    treeStand = eltOut('TreeStand element')
    microclim = eltOut('MicroClimate element')

    #phenology
    Year = var('year of the cohort emergency', 2000)
    HeatSum = var('cumulated degree day (degC day)', 0.0)

    #vars
    BudBurst = var('status of bud burst',False)
    BudBurstDate = var('date of emergency (B4  stade) (date)', -9999)
    Expansion = var('surface expansion level [0-1] (m2_leaf /m2_leaf)', 0)
    Retained = var('leaf fraction attached (not loss) [0-1] (m2_leaf /m2_leaf)', 1)
    Weight = var('biomass (kg_DM /m2_soil)', 0)
    LeafFall = var('leaf biomass fall (kg_DM /m2_soil /day)',0)
    Area = var('area (m2_leaf /m2_soil)',0)
    LAI = var('leaf area index (m2_projected_leaf /m2_soil)',0)


    @pcs
    def update(self,
        SLA = param('specific leaf area (m2_LeafArea /Kg_DM)', 6.5),
        LAI_LeafArea_ratio = param('LAI on LeafArea ratio (m2_LAI /m2_LeafArea)', 0.389),
        ):

        #initialisation at cohort creation
        #store the OneYearCohortWeightMax of all trees and evaluated the initial _CohortWeightMax
        if not hasattr(self,'_CohortWeightMax'):
            self._TreesCohortWeightMax = {id(tree): tree.OneYearCohortWeightMax for tree in self.treeStand}
            self._CohortWeightMax = None

        #update the leaf cohort development
        if not self.BudBurst:
            self.pcs_BudBurstStatus()

        else:
            #the leaf cohort development is updated daily
            if self.sunTime.isDayBeginning:

                #update the weightmax of the cohort to take into account of the potential tree number evolution
                if (len(self._TreesCohortWeightMax) != len(self.treeStand)) or (self._CohortWeightMax is None):
                    self._CohortWeightMax = sum(self._TreesCohortWeightMax[id(tree)] for tree in self.treeStand) / self.treeStand.Area
                    self._TreesCohortWeightMax = {id(tree): self._TreesCohortWeightMax[id(tree)] for tree in self.treeStand}

                self.pcs_LeafExpansion()
                self.pcs_LeafLoss()

                #Leaf weight fall
                self.LeafFall = max(0, self.Weight -self.Retained * self.Expansion *  self._CohortWeightMax)

                #update cohort leaf  biomass and area
                self.Weight = self.Retained * self.Expansion *  self._CohortWeightMax
                self.Area = SLA * self.Weight
                self.LAI= self.Area * LAI_LeafArea_ratio


    @pcs
    def pcs_BudBurstStatus(self,
        BudBurstTempBase = param('Base temperature to cumulate Heat sum for bud burst (deg_C)', 0),
        BudBurstHeatSum = param('Heat sum for bud burst (deg_C day)', 882), #ex 1400
        ):
        '''Update the bud burst status :
            .BudBurst [True | False],
            .BudBurstDate : date
        '''

        #Use a sum of temperature for leaf bud burst date evaluation
        self.HeatSum += max(0,self.microclim.TaC -BudBurstTempBase) / 24.0
        if  self.HeatSum > BudBurstHeatSum:
            self.BudBurstDate = self.sunTime.time // 24.0
            self.BudBurst = True

    @pcs
    def pcs_LeafExpansion(self,
        ExpansionLength = param('Leaf expansion length from budburst(days)',200), #ex 150
        ):
        '''Update the leaf expansion rate : Expansion [0-1]'''

        #'update the leaf expansion rate from the number of days since emergency
        #following a simple S curve on ExpansionLength days

        _Jref = (self.sunTime.time // 24.0 - self.BudBurstDate)* 1./ExpansionLength
        if _Jref <1 :
            self.Expansion = (3-2*_Jref)*(_Jref**2)
        else :
            self.Expansion = 1

    @pcs
    def pcs_LeafLoss(self,
        DOY_start = param('Day of year when start loss of leaves (DOY)', 180),
        DOY_stop = param('Day of year when stop loss of leaves (DOY)', 300),
        sigm_kA  = param('parameter A of the sigmoide used to evaluate the annual leaf retained rate in function of the cohort age' , -2.7 ),
        sigm_kB  = param('parameter B of the sigmoide used to evaluate the annual leaf retained rate in function of the cohort age' , 1.52 ),

        ):
        '''Update the proportion of leaf retained
            The amount of leaves retained is proportionnal to that at the last time step
            and  a rate of loss combining :
             - an age effect describe by a sigmoide with  sigm_kA and sigm_kB as form parameters
             - the fact that leaves are loss during a period in year : DOY_start to DOY_stop parameters
        '''
        _DOY = self.sunTime.DOY

        if DOY_start < _DOY< DOY_stop:
            #reduction factor of the amount of leaves retained is function of the cohort age
            _Age = int(self.sunTime.Y -self.Year)
            _AnnualFractionRetained = 1/(1+exp(-sigm_kA*(_Age - sigm_kB)))
            _k = 6*log(_AnnualFractionRetained)/(DOY_stop - DOY_start)

            #relative date in the period of leaf fall [DOY_start to DOY_stop]
            _Jref = (_DOY -DOY_start)*1./(DOY_stop - DOY_start)

            self.Retained *= 1 +_k*_Jref*(1-_Jref)









