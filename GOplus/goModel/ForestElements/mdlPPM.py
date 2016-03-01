from ..goBases import *
from .mdlSunTime import SunTime
from .mdlMicroClimate import MicroClimate


class CaterpillarsCohort(ELT):
    ''' Represent a PPM caterpillar  cohort on a stand
        A. Bosc - 2014-02-04
    '''
    
    #Outer elements
    sunTime = eltOut('SunTime element', SunTime)
    microclim = eltOut('MicroClimate element', MicroClimate)
    treeStand = eltOut('TreeStand element', TreeStand)

    #emergence status
    isEmerged = var_bool('True if caterpillar have emerged (True/False)', False)
    
    #caterpillar population size
    populationSize = var('number of caterpillar by soil square meter (caterpillar /m2_soil)', 1)
    
    #defoliation
    dailyDefoliation = var('amount of foliage heat by day (g_DM/day)')
    
    #caterpillar biomass
    W= var('weight of caterpillar (g_MS /caterpillar)', 0.0008)
    W_max = param('maximal weight of a caterpillar at end growth(g_MS /caterpillar)', 0.8)
    carbonFraction = param('dry biomass carbon content (g_C /g_DM)', 0.5)

    #caterpillar feeding
    feed = var('feed (g_DM /caterpillar /hour')
    feed_Tmin = param('minimal temperature to enable caterpillar feeding (degC)', 10)
    feed_Rsmax = param('maximal radiation to enable caterpillar feeding (W /m2)', 10)
    feed_Q10 = param('Q10 of feeding activitie()', 2)
    feed_ref = param('feeding at the reference temperature (15degC) and for a biomass W = 0.5*Wmax (g_DM /hour)', 0.05)
    
    #caterpillar carbon physiology
    rdtHerbivory = param('herbivory rendement : convertion factor of needle biomass to caterpillar biomass (include growth respiration) (g_MS /g_MS)', 0.05)

    Rm_15 = param('maintenance respiration at 15 degC (g_C /g_DM /hour)', 1.4E-4)
    Rm_Q10 = param('Q10 of maintenance respiration ()', 2)
    
    
    def initialisation(self):
        '''Initialisation step'''
        
        pass
    
    
    def update(self):
        '''update'''
        
        if self.isEmerged:
            #individual caterpillar biology
            self.individualActivity()

            #leaf area consumption
            if self.sunTime.isDayBeginning :  self.dailyDefoliation = 0
            self.dailyDefoliation += self.feed * self.populationSize
            
            if self.sunTime.isDayEnd :  
                #TODO : apply the defoliation on treeStand
                
                self.dailyDefoliation = 0
        
        else:
            pass
            #Manage the cycle to emerge
    
    
    def individualActivity(self):
        '''Feeding : only if climatic conditions  are OK'''
        
        if self.microclim.TaC>self.feed_Tmin and (self.microclim.RsDir+ self.microclim.RsDif)< self.feed_Rsmax :
            _k_temp = self.feed_Q10 **((self.microclim.TaC - 15)/10)     #feeding activity dependency to temperature
            _k_dev = 4*(self.W/self.W_max) * (1-self.W/self.W_max)       #feeding need in function of the caterpillar size (sigmoide)
            self.feed = self.feed_ref *  _k_temp * _k_dev        
        
        else:
            self.feed = 0

        #respiration 
        self.Rm = self.W * self.Rm_15 * self.Rm_Q10**((self.microclim.TaC - 15)/10)
        
        #biomass change
        self.W += self.feed * self.rdtHerbivory -  (self.Rm/self.carbonFraction)



class PPM_Cycle(ELT):
    ''' Represent  the PPM caterpillar  cycle. 
        A. Bosc - 2013-11-26
    '''
    #associated outer elements
    sunTime = eltOut('SunTime element',  SunTime)
    microclim = eltOut('MicroClimate element',  MicroClimate)
    
    Tcycle = var('temperature for cycle phenology (deg_C)', 8.0)
    k_TcyclePond = param('inertial ponderation of Tcycle (hour)', 30*24)
    
    def initialisation(self):
        pass
    
    def update(self):
        ''' Manage the phenology of the PPM cycle.
            If climate conditions are suitable, a new PPM infestation is induice
        '''
        #evaluate a smooth temperature used for cycle management
        self.Tcycle += (self.microclim.TaC - self.Tcycle) / self.k_TcyclePond
        
        if self.Tcycle
        
    
    
    
    
