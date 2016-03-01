from ...goBases import *

from .SoilElements.mdlSoilSurface import SoilSurface
from .SoilElements.mdlSoilWaterCycle import SoilWaterCycle
from .SoilElements.mdlSoilCarbonCycle import SoilCarbonCycle


class Soil(ELT):
    '''Represent the soil
    '''

    # Outer elements
    sunTime = eltOut('SunTime element')
    microclim = eltOut('MicroClimate upper soil')
    forest = eltOut('Forest container element')
    treeStand = eltOut('TreesStand element')
    underStorey = eltOut('UnderStorey element')
    
    #Inner elements
    surface = eltIn(SoilSurface)
    waterCycle = eltIn(SoilWaterCycle)
    carbonCycle = eltIn(SoilCarbonCycle)

    def update(self):
        #Bound sub elements
        if self.sunTime.isSimulBeginning:
            self.surface.microclim = self.microclim
            
            self.carbonCycle.sunTime= self.sunTime
            self.carbonCycle.microclim = self.microclim
            self.carbonCycle.treeStand = self.treeStand
            self.carbonCycle.underStorey = self.underStorey
            self.carbonCycle.waterCycle = self.waterCycle
            
            self.waterCycle.sunTime= self.sunTime
            self.waterCycle.treeStand = self.treeStand
            self.waterCycle.underStorey = self.underStorey
            self.waterCycle.surface = self.surface
        
        #Soil surface exchange
        self.surface.update()
        
        #Carbon cycle : decomposition and respiration components
        self.carbonCycle.update()
        
        #Water cycle inside soil
        self.waterCycle.update()


