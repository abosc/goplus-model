from ELT import *


class Microclim(ELT):
    d = var('vpd', 600.)


class StomatalConductance_ABosc1999(ELT):    
    G = var('stomatal conductance (m3_H2O /m2_leafArea /s)', 0.)
    G_unstress = var('  (m/s)')
    _pond_Rs = var('radiative ponderation of stomatal conductance ([0-1])')
    _pond_VPD = var('VPD ponderation of stomatal conductance ([0-1])')
    _pond_Yleaf = var('leaf water potentiel ponderation of stomatal conductance ([0-1])')
    
    @pcs
    def update(self, 
        G_Max = param('maximal stomatal conductance (m/s)', 0.00424), 
        k_Rs1 = param('parameter 1 of radiative ponderation of stomatal conductance (-)', 0.00918), 
        k_Rs2 = param('parameter 2 of radiative ponderation of stomatal conductance (-)', 1.13), 
        k_VPD1 = param('parameter 1 of VPD ponderation of stomatal conductance (-)', 0.000811), 
        k_VPD2 = param('parameter 2 of VPD ponderation of stomatal conductance (-)',1.08), 
        k_Yleaf1 = param('parameter 1 of leaf water potential ponderation of stomatal conductance (MPa)',-1.80), 
        k_Yleaf2 = param('parameter 2 of leaf water potential ponderation of stomatal conductance (-)',0.2), 
        k_dt = param('ponderation of time response to stationnary state of stomatal conductance ]0-1]', 0.6), 
        ):
        
        _RsToPAR = 2.1 #Conversion factor of solar radiation (W/m2) to PAR (micromol/m2/s)
        canopy = self.container
        
        self._pond_Rs = 1 - 1 / (1 + k_Rs1 * (canopy.Rs_Int * _RsToPAR / canopy.LeafArea) ** k_Rs2)
        self._pond_VPD = min(1, 1 / (k_VPD1 * (canopy.microclim.d + 1) ** k_VPD2))
        self._pond_Yleaf = max(0, 1 - canopy.LeafWaterPotential/k_Yleaf1) ** k_Yleaf2

        #Gstom if stationnary condition
        _G_Stat =  G_Max * self._pond_Rs * self._pond_VPD * self._pond_Yleaf

        #transitionnal Gstom between last value and stationnary response
        self.G = self.G*(1 -  k_dt) + _G_Stat* k_dt
        self.G_unstress =  G_Max * self._pond_Rs
            


class Leaf(ELT):
    microclim = eltIn( Microclim)
    stomata = eltIn( StomatalConductance_ABosc1999)
    
    Rs_Int = var('rad int', 250.)
    LeafArea  = var('leaf surface area', 2.6)

    LeafWaterPotential = var('leaf w pot', -0.65)

    @pcs
    def update(self):
        self.stomata.update()



####
l= Leaf()
from time import time

tsart =time()

for i in range(1000000):
    l.update()
tend=time()

print(l.stomata.G , tend-tsart)
