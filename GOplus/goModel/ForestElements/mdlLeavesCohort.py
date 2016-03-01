from ...goBases import *


class LeavesCohort(ELT):

    #Outer elements
    locTime = eltOut('LocTime element')
    treeStand = eltOut('treeStand element')
    
    #phenology
    Year = var('year of the cohort emergency', 2000)
    HeatSum = var('cumulated degree day (degC day)', 0.0)

    #vars
    DateOfB4 = var('date of emergency (B4  stade) (date)', -9999)
    Expansion = var('surface expansion level [0-1] (m2_leaf /m2_leaf)', 0)
    Retained = var('surface expansion level [0-1] (m2_leaf /m2_leaf)', 1)
    Weight = var('biomass (kg_DM /m2_soil)', 0)
    LeafFall = var('leaf biomass fall (kg_DM /m2_soil /day)')
    Area = var('area (m2_leaf /m2_soil)')
    LAI = var('leaf area index (m2_projected_leaf /m2_soil)')
    
    @pcs    
    def update_daily(self, 
        B4HeatSum = param('Heat sum for B4', 1400), 
        SLA = param('specific leaf area (m2_LeafArea /Kg_DM)', 6.5), 
        LAI_LeafArea_ratio = param('LAI on LeafArea ratio (m2_LAI /m2_LeafArea)', 0.389), 
        _CohortWeightMax = private('CohortWeightMax by tree and soil area ', ELT), 
        ):
        
        #updated the weighmax of the cohort to take into account of the potential tree number evolution
            
        if self.locTime.isYearBeginning :
            if self.locTime.isSimulBeginning: 
                _CohortWeightMax.ofTree = {}

            if len(_CohortWeightMax.ofTree) !=len(self.treeStand):
                _CohortWeightMax.ofTree = {tree: tree.OneYearCohortWeightMax for tree in self.treeStand} #store the CohortWeightMax of all trees
            
            if self.treeStand.treesCount > 0:
                _CohortWeightMax.ofSoil = sum(_CohortWeightMax.ofTree[_tree] for _tree in self.treeStand) / self.treeStand.Area
            else:
                #use to allow a treeStand functionning without trees (clear-cutting period)
                _CohortWeightMax.ofSoil = 0.001

        #update daily phenology
        if self.DateOfB4== -9999:
            if  self.HeatSum > B4HeatSum: 
                self.DateOfB4 = self.locTime.Now
            
            self.Expansion = 0.0
            self.LeafFall = 0.0
            self.Retained = 1.0
            self.Weight = 0.0
            self.Area = 0.0
            self.LAI = 0.0
            
        else:
            #Number of days since emergency
            _Jref = self.locTime.Now - self.DateOfB4 

            #update the proportion of needles retained 
            if _Jref < (365 + 61) :
                self.Retained = 1
            elif _Jref < (365 + 184) :
                self.Retained = 1 - 0.2 * (_Jref - 365.0 - 61.0) / 123.0
            elif _Jref < (730 + 76) :
                self.Retained = 0.8
            elif _Jref < 1002 :
                self.Retained = 0.8 * (1 - (_Jref - 730.0 - 75.0) / 197.0)
            else :
                self.Retained = 0
            
            #Leaf weight fall
            self.LeafFall = max(0, self.Weight -self.Retained * self.Expansion *  _CohortWeightMax.ofSoil)        

            #update the needle expansion rate
            if _Jref < 0 :
                self.Expansion = 0
            elif _Jref < 92 :
                self.Expansion = _Jref / 92.0
            else :
                self.Expansion = 1
            
            #update cohort leaf  biomass and area
            self.Weight = self.Retained * self.Expansion *  _CohortWeightMax.ofSoil
            self.Area = SLA * self.Weight
            self.LAI= self.Area * LAI_LeafArea_ratio




