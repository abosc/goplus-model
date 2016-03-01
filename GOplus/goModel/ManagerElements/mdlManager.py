from ...goBases import *
from ..ForestElements.mdlTrees import Trees
import random


class Manager(ELT):
    '''Represent the forest manager
    '''

    # Outer  elements
    locTime = eltOut('LocTime element')
    forest = eltOut('Forest element')

    #group of inner elements
    markedTrees = eltIn(Trees)

    #variables  on harvested trees 
    lastThinningYear = var('year of the last thinning (year)', 0.0)
    harvest_Wstem = var('harvested stem biomass (kg_DM /m2_soil)', 0.0)
    harvest_Wcrown = var('harvested crown biomass (kg_DM /m2_soil)', 0.0)
    harvest_Wstub = var('harvested  stub biomass (kg_DM /m2_soil)', 0.0)
    harvest_Wtaproot = var('harvested  taproot biomass (kg_DM /m2_soil)', 0.0)
    harvest_Wneedles = var('harvested  needles biomass (kg_DM /m2_soil)', 0.0)

    harvest_DBHmean = var('mean tree diameters at breast height (cm)', 0.)
    harvest_DBHsd = var('standard deviation of tree diameters at breast height (cm)', 0.)
    harvest_DBHquadratic = var('mean quadratic tree DBH (cm)', 0.)
    harvest_HEIGHTmean = var('mean tree height (m)', 0.)
    harvest_HEIGHTsd = var('standard deviation of tree height (m)', 0.)
    

    def update(self):
        '''Manage the sylvicultural interventions'''
        
        self.harvest_Wstem = 0.
        self.harvest_Wcrown = 0.
        self.harvest_Wstub = 0.
        self.harvest_Wtaproot = 0.
        self.harvest_Wneedles = 0.

        self.harvest_DBHmean = 0.
        self.harvest_DBHsd = 0.
        self.harvest_DBHquadratic = 0.
        self.harvest_HEIGHTmean = 0.
        self.harvest_HEIGHTsd = 0.

        if self.locTime.isYearEnd:
            self.do_managment()


    def do_managment(self):
        '''Manage the sylvicultural interventions : this method must be overwrite do to something'''
        pass

    
    def do_markRandomLogging(self, randomFactor=1, densityObjective = 1200.0):
        '''Select trees to be cut. 
            All old  marks are cleared.
        '''
        _treeStand = self.forest.treeStand
        
        #create a sorted list of the trees in function of their aerial biomass
        _sortedTrees = sorted(_treeStand,  key = (lambda tree: tree.Wa))
        
        #random generator initialisation 
        random.seed(len(_sortedTrees))     
        
        #choose randomly tree until stopperTest ==True, add it to markedTrees
        del self.markedTrees[:]

        _nbtreesObjective = densityObjective*_treeStand.Area/10000.
        while len(_sortedTrees)> _nbtreesObjective :
            _tree = _sortedTrees[int((random.random() ** randomFactor) * len(_sortedTrees))]
            self.markedTrees +=  [ _tree]
            _sortedTrees.remove(_tree)


    def do_Logging(self, harvestStem = True, harvestStub = False, harvestCrownWood = False, harvestTaproot = False,  harvestNeedles = False):
        '''Cut marked trees and harvest specified compartments.
            Residual biomass is allocate  to litter.
        '''
        
        _standArea = self.forest.treeStand.Area
        _incorporateACarbonLitter = self.forest.soil.carbonCycle.incorporateACarbonLitter
        _KgMs_by_tree_to_gC_by_m2_soil = 500 / _standArea
        
        for _tree in self.markedTrees:
            #cut the tree : exclude it to treeStand
            self.forest.treeStand._exclude_tree( _tree)

            #tree trunk biomass managment
            if harvestStem:
                self.harvest_Wstem += _tree.Wstem /_standArea
            else:
               _incorporateACarbonLitter ((_tree.Wstem) * _KgMs_by_tree_to_gC_by_m2_soil, 1./10.,  _tree.container.Age / 2)
            
            #tree needles biomass managment
            if harvestNeedles:
                self.harvest_Wneedles += _tree.LeafWeight /_standArea
            else:
                _incorporateACarbonLitter ((_tree.LeafWeight) * _KgMs_by_tree_to_gC_by_m2_soil, 4./1., 2)
            
            #tree crown wood  biomass (all aerial biomass witout foliage and stem) managment
            if harvestCrownWood:        
                self.harvest_Wcrown += (_tree.Wa - _tree.LeafWeight - _tree.Wstem) /_standArea
            else:
                _incorporateACarbonLitter ((_tree.Wa - _tree.LeafWeight - _tree.Wstem) * _KgMs_by_tree_to_gC_by_m2_soil, 1./4., min(5, _tree.container.Age / 2))
            
            #for roots harvest stub , taproot, or nothing
            #roots biomass is  shared  on stub and fine roots (unextractable) in proportion of trunk on aerial biomass 
            _Wstub = _tree.Wr * (_tree.Wstem / _tree.Wa)
            if harvestStub:
                self.harvest_Wstub += _Wstub /_standArea
                _incorporateACarbonLitter( (_tree.Wr -_Wstub) * _KgMs_by_tree_to_gC_by_m2_soil, 4./1., 1)  #fine roots
                
            else:
                if harvestTaproot:
                    self.harvest_Wtaproot += _tree.Wtaproot /_standArea
                    _incorporateACarbonLitter( (_tree.Wr -_Wstub) * _KgMs_by_tree_to_gC_by_m2_soil, 4./1., 1)  #fine roots
                    _incorporateACarbonLitter( (_Wstub - _tree.Wtaproot ) * _KgMs_by_tree_to_gC_by_m2_soil, 1./1., 1) #middle roots
                    
                else:
                    _incorporateACarbonLitter( (_tree.Wr -_Wstub) * _KgMs_by_tree_to_gC_by_m2_soil, 4./1., 1)  #fine roots
                    _incorporateACarbonLitter( (_Wstub - _tree.Wtaproot ) * _KgMs_by_tree_to_gC_by_m2_soil, 1./1., 1) #middle roots
                    _incorporateACarbonLitter (_tree.Wtaproot  * _KgMs_by_tree_to_gC_by_m2_soil, 1./8., _tree.container.Age / 2)#taproots
        
        #Evaluate the dendrometrics dimensions of trees cut
        self.harvest_DBHmean = self.markedTrees.DBHmean
        self.harvest_DBHsd = self.markedTrees.DBHsd
        self.harvest_DBHquadratic = self.markedTrees.DBHquadratic
        self.harvest_HEIGHTmean = self.markedTrees.HEIGHTmean
        self.harvest_HEIGHTsd = self.markedTrees.HEIGHTsd


    def do_plow(self, areaFractionPlowed = 0.5, soilCarbonFractionAffected = 0.2, soilPerennialFractionAffected =0.2 ):
        '''plow() : made a plow
            areaFractionPlowed : Area fraction plowed (m2 /m2)
            soilCarbonFractionAffected : soil carbon fraction affected under plowing  (kg_C /kg_C)
            soilPerennialFractionAffected : soil perennial fraction affected under plowing (kg_DM /kg_DM)
        '''

        #estimate the PlowingFactor
        self.forest.soil.carbonCycle.PlowingFactor = max(self.forest.soil.carbonCycle.PlowingFactor, soilCarbonFractionAffected * areaFractionPlowed)
        
        #impact on the underground
        _UG = self.forest.underStorey
        
        #distribute the underground biomass fraction affected by the plow to the litter
        _UG.foliage.LitterFall = areaFractionPlowed * _UG.foliage.W
        _UG.roots.LitterFall = areaFractionPlowed * _UG.roots.W * soilPerennialFractionAffected
        _UG.perennial.LitterFall = areaFractionPlowed * _UG.perennial.W * (_UG.perennial.AboveGroundFraction + (1 - _UG.perennial.AboveGroundFraction) * soilPerennialFractionAffected)

        #update Cpool and biomass of each undergrowth compartments
        for _cpt in (_UG.foliage,  _UG.roots,  _UG.perennial):
            if _cpt.W > 0 : _cpt.Cpool = _cpt.Cpool * (_cpt.W - _cpt.LitterFall) / _cpt.W
            _cpt.W = _cpt.W - _cpt.LitterFall

        #convert undergrowth litter in soil carbon incoming
        _UG.pcs_AllocateLitterCarbonToSoil()



