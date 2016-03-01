from ..goBases import *

from .mdlSunTime import SunTime
from .mdlClimate import Climate
from .mdlForest import Forest
from .ManagerElements.mdlManager import Manager

class Model(ELT):
    ''' GOplus model 
    '''
    
    #inner elements
    sunTime = eltIn(SunTime)
    climate = eltIn(Climate)
    forest = eltIn(Forest)
    manager = eltIn(Manager)
    
    def update(self):
        
        #initialisation : connect the unbound model elements
        if self.sunTime.isSimulBeginning:
            self.climate.sunTime = self.sunTime       
            self.forest.sunTime=self.sunTime
            self.forest.microclim = self.climate.microclim
            self.manager.sunTime = self.sunTime
            self.manager.forest = self.forest 
        
        #inner elements update
        self.sunTime.update()
        self.climate.update()
        self.forest.update()
        self.manager.update()


