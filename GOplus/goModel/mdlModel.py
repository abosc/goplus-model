from ..goBases import *

from .mdlLocTime import LocTime
from .mdlSunLocal import SunLocal
from .mdlClimate import Climate
from .mdlForest import Forest
from .ManagerElements.mdlManager import Manager

class Model(ELT):
    ''' GOplus model 
        - v 2014-05-23- A. Bosc
    '''
    
    #inner elements
    locTime = eltIn(LocTime)
    sunLocal = eltIn(SunLocal)
    climate = eltIn(Climate)
    forest = eltIn(Forest)
    manager = eltIn(Manager)
    
    def update(self):
        
        #initialisation : connect the unbound model elements
        if self.locTime.isSimulBeginning:
            self.sunLocal.locTime = self.locTime
            self.climate.locTime = self.locTime
            self.climate.sunLocal= self.sunLocal
            self.forest.locTime=self.locTime
            self.forest.sunLocal=self.sunLocal
            self.forest.microclim = self.climate.microclim
            self.manager.locTime = self.locTime
            self.manager.forest = self.forest 
        
        #inner elements update
        self.locTime.update()
        self.sunLocal.update()
        self.climate.update()
        self.forest.update()
        self.manager.update()


