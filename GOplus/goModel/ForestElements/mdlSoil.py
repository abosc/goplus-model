from ...goBases import *

from .SoilElements.mdlSoilSurface import SoilSurface
from .SoilElements.mdlSoilWaterCycle import SoilWaterCycle
from .SoilElements.mdlSoilCarbonCycle import SoilCarbonCycle


class Soil(ELT):
    '''Represent the soil
    '''

    # Outer elements
    locTime = eltOut('LocTime element')
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
        if self.locTime.isSimulBeginning:
            self.surface.microclim = self.microclim
            
            self.carbonCycle.locTime= self.locTime
            self.carbonCycle.microclim = self.microclim
            self.carbonCycle.treeStand = self.treeStand
            self.carbonCycle.underStorey = self.underStorey
            self.carbonCycle.waterCycle = self.waterCycle
            
            self.waterCycle.locTime= self.locTime
            self.waterCycle.treeStand = self.treeStand
            self.waterCycle.underStorey = self.underStorey
            self.waterCycle.surface = self.surface
        
        #Soil surface exchange
        self.surface.update()
        
        #Carbon cycle : decomposition and respiration components
        self.carbonCycle.update()
        
        #Water cycle inside soil
        self.waterCycle.update()


