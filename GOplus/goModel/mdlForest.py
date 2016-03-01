from ..goBases import *

from .mdlMicroClimate import MicroClimate
from .ForestElements.mdlTreeStand import TreeStand
from .ForestElements.mdlUnderStorey import UnderStorey
from .ForestElements.mdlSoil import Soil

class Forest(ELT):
    '''Forest is an integrative ELT regrouping the two vegetation layers ,
    the  soil layer, and the microclimates associated to each layers.
    It manage :
        - the order of processes evaluations for each of these components.
        - some flux between these components.
        - the ecosystem global fluxes
    '''
    
    #Outer elements
    locTime = eltOut('LocTime element')
    sunLocal = eltOut('SunLocal element')
    microclim  = eltOut('Upper forest MicroClimate')

    #Inner elements
    treeStand = eltIn(TreeStand)
    microclim_UnderStorey = eltIn(MicroClimate)
    underStorey = eltIn(UnderStorey)
    microclim_Soil = eltIn(MicroClimate)
    soil = eltIn(Soil)

    def update(self):
        ''' decline the update over the Forest inner ELT in function of the moment caracteristics'''
        
        #connect the inner ELT of the Forest
        if self.locTime.isSimulBeginning : 
            self.treeStand.locTime = self.locTime
            self.treeStand.sunLocal = self.sunLocal       
            self.treeStand.microclim = self.microclim       
            self.treeStand.microclim_under = self.microclim_UnderStorey
            self.treeStand.soil = self.soil

            self.underStorey.locTime = self.locTime
            self.underStorey.sunLocal = self.sunLocal
            self.underStorey.microclim = self.microclim_UnderStorey
            self.underStorey.microclim_under = self.microclim_Soil
            self.underStorey.soil = self.soil

            self.soil.locTime = self.locTime
            self.soil.microclim = self.microclim_Soil
            self.soil.treeStand = self.treeStand
            self.soil.underStorey = self.underStorey
            self.soil.forest = self

        #update the Treesplanting layer
        self.treeStand.update()
        
        #update the microclimates properties impacted by treeStand canopy surface
        self.pcs_updateMicroclimatesImpactedByACanopy(
                                                    canopy = self.treeStand.canopy, 
                                                    upperMicroclim = self.microclim, 
                                                    underMicroclim = self.microclim_UnderStorey)

        #update the underStorey layer
        self.underStorey.update()
        
        #update the microclimates  properties impacted by underStorey layer
        self.pcs_updateMicroclimatesImpactedByACanopy(
                                                    canopy = self.underStorey.canopy, 
                                                    upperMicroclim = self.microclim_UnderStorey, 
                                                    underMicroclim = self.microclim_Soil)
            
        #update the soil layer
        self.soil.update()
        
        #update the microclimates  properties impacted by soil layer
        _soil_CS = self.soil.surface
        
        self.microclim_Soil.RsUp = _soil_CS.Rs_Sct
        self.microclim_Soil.RthUp = _soil_CS.Rth_Emi + _soil_CS.Rth_Sct
    
        #Integratives Forest fluxes
        self.pcs_integrateForestFluxes()


    #FOREST FLUXES
    ETR = var('evapotranspiratioon (Kg_H2O /m2_soil /hour)')
    NEE = var('carbon net ecosystem exchange (g_C /m2_soil /hour)')
    Rnet = var('net radiation (W /m2_soil)')
    H = var('sensible heat (W /m2_soil)')
    LE = var('latent heat (W /m2_soil)')
    

    def pcs_integrateForestFluxes(self):
        _treeStand_CS = self.treeStand.canopy
        _underStorey_CS = self.underStorey.canopy
        _soil_CS = self.soil.surface
        _microclim = self.microclim
        
        self.ETR = self.soil.surface.ETR + _underStorey_CS.ETR + _treeStand_CS.ETR
        self.NEE = (self.treeStand.Rm +self.treeStand.Rg - _treeStand_CS.Assimilation )  \
                    + (self.underStorey.Rm + self.underStorey.Rg - _underStorey_CS.Assimilation ) \
                    + self.soil.carbonCycle.Rh
        self.Rnet = _microclim.RsDif +_microclim.RsDir + _microclim.RthDw - _microclim.RthUp
        self.H = _soil_CS.H + _underStorey_CS.H + _treeStand_CS.H
        self.LE = _soil_CS.LE + _underStorey_CS.LE + _treeStand_CS.LE
    
    
    def pcs_updateMicroclimatesImpactedByACanopy(self, canopy, upperMicroclim, underMicroclim):
        '''update the microclimates  properties impacted by underStorey layer'''
        
        upperMicroclim.RsUp = underMicroclim.RsUp - canopy.RsUp_Int + canopy.Rs_Sct_Up

        upperMicroclim.RthUp = underMicroclim.RthUp - canopy.RthUp_Int + 0.5 * canopy.Rth_Emi + canopy.Rth_Sct_Up

        underMicroclim.RsDif = upperMicroclim.RsDif - canopy.RsDif_Int + canopy.Rs_Sct_Dw
        underMicroclim.RsDir = upperMicroclim.RsDir - canopy.RsDir_Int
        underMicroclim.RthDw = upperMicroclim.RthDw - canopy.RthDw_Int + 0.5 * canopy.Rth_Emi + canopy.Rth_Sct_Dw
        
        underMicroclim.z_ref = canopy.height_surface
        underMicroclim.CO2 = upperMicroclim.CO2
        underMicroclim.u = canopy.u_surface
        underMicroclim.TaC = upperMicroclim.TaC
        underMicroclim.P = upperMicroclim.P
        underMicroclim.e = upperMicroclim.e
        underMicroclim.Rain = (upperMicroclim.Rain - canopy.InterceptedRain) + canopy.Draining
        
        underMicroclim.update()
