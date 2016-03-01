# -*- coding: utf-8 -*-

from ....goBases import *
from .mdlSunShadeFarquhar_CanopySurface import SunShadeCanopySurface as CanopySurface

class SunShadeCanopySurface(CanopySurface):
    '''!!! version test !!!
    Big leaf canopy associated to Farquhar photosynthetic model
    to evaluated the gain of the SunShade approach
    '''

    @pcs
    def  pcs_AssimilationFarquhar(self, 

        #Biochemistry photosynthetic parameters at the reference temperature and activation energies
        #from Bernacchi et al. 2001 in Medlyn et al. 2002    
        Kc_25= param('Michaelis-Menten constant of rubisco for CO2 at TCref (mol_CO2 /mol)', 404.9e-6),#Medlyn et al. 2002 [eq 5]
        Ea_Kc = param('Activation energy for Kc (J /mol)',  79430. ),#Medlyn et al. 2002 [eq 5]
        Ko_25 = param('Michaelis-Menten constant of rubisco for O2 at TCref (mol_O2 /mol)',278.4e-3),#Medlyn et al. 2002 [eq 6]
        Ea_Ko =   param('Activation energy for Kc (J /mol)', 36380.),#Medlyn et al. 2002 [eq 6]
        GammaStar_25 = param('CO2 compensation point of photosynthesis in the absence of mitochondrial respiration (mol_CO2 /mol_air : ppm)', 42.75e-6),#Medlyn et al. 2002 [eq 12]
        Ea_GammaStar = param('Activation energy for GammaStar (J /mol)', 37830.),#Medlyn et al. 2002 [eq 12]

        #Medlyn et al. 2002 
        Vcmax_25 = param('Vcmax at TCref, expressed on a one-sided leaf area basis (mol_CO2 /m2_LAI /s))',  89.98e-6),#Medlyn et al. 2002 [tb 2]
        Ea_Vcmax = param('Activation energy for Vcmax (J /mol)', 62220.),#Medlyn et al. 2002 [tb 2]

        Jmax_25 = param('Jmax at TCref, expressed on a one-sided leaf area basis (mol_e /m2_LAI /s', 154.74e-6),#Medlyn et al. 2002 [tb 3]
        Ha_Jmax = param('Activation energy for Jmax (J /mol)', 34830.),#Medlyn et al. 2002 [tb 3]
        Hd_Jmax = param('Deactivation energy for Jmax (J /mol)', 200000.),#Medlyn et al. 2002 [tb 3]
        TCopt_Jmax = param('temperature of Jmax optimum (deg_C)', 36.87),#Medlyn et al. 2002 [tb 3]
        alpha = param('Quantum yield of electron transport (mol_e /mol_photon_absorbed). \
                Litterature value obtained on Rs intercepted need to be corrected for leaf absorbance', 0.124/0.9),  #Porte 1998 [tb 2] :  for LAI based

        Rd_25 = param('Dark leaf respiration at TCref (mol_CO2 /m2_LAI /s)',  1e-6),  # ##to update
        Ea_Rd= param('Activation energy for Rd (J /mol)', 46390),                                     # ##to update

        ):
        ''' Photosynthesys is modelised by Farquhar's model for mean layer
            Resolution of Anet from the system of equation of :
             - Farquhar model : Anet =min(Ac,Aj) - Rd
             - Diffusivity of CO2 trouth stomata:   Anet = gc(Ca - Ci)
            Along Medlyn 2002, parameter(Vcmax,Jmax,Rd)  and internal variables (gCO2,Q,J,Aj,Ac,Anet) 
            were evaluated on one-sided base, it was verified, that does'nt modified results (A).
        '''

        if self.LAI > 0.001 :
            #calculated parameters
            R = 8.3145 #J /mol /K
            TKref = 25 + 273.15 #K
            TKopt_Jmax = TCopt_Jmax +273.15
            KHa_Jmax = Ha_Jmax/(R* TKopt_Jmax)
            KHd_Jmax = Hd_Jmax/(R* TKopt_Jmax)
            K_Jmax_25 = Jmax_25*(KHd_Jmax  -KHa_Jmax*(1-exp(KHd_Jmax*(1 - TKopt_Jmax/TKref))))
            
            TK_leaf = self.microclim.TaK + self.dTsTa          #K 
            T_factor = (TK_leaf-TKref)/(R*TK_leaf*TKref)    #mol /J

            #Biochemistry photosynthetic parameters dependence to temperature
            Rd = Rd_25 * exp(Ea_Rd*T_factor)      

            Kc = Kc_25 * exp(Ea_Kc*T_factor)
            Ko = Ko_25 * exp(Ea_Ko*T_factor)
            Oi = 0.2095 #mol_O2 /mol_air
            Km = Kc*(1. + Oi/Ko)                             #effective Michaelis-Menten coefficient for CO2 (mol_CO2 /mol_air)
            GammaStar = GammaStar_25 * exp(Ea_GammaStar*T_factor)

            Vcmax = Vcmax_25 * exp(Ea_Vcmax*T_factor)               
            Jmax = K_Jmax_25 * exp(Ha_Jmax*T_factor )/ (KHd_Jmax - KHa_Jmax*(1 - exp(KHd_Jmax*(1 - TKopt_Jmax/TK_leaf))))

            #stomata vapour conductance to air conductance for CO2
            gCO2=2*self.g_stom * (self.microclim.P)/(R*TK_leaf) /1.6 #convert G in m/s (m3_vapour /m2_LAI /s) to mol_CO2/m2_LAI/s
            Ca = self.microclim.CO2 * 1.0e-6      #mol_CO2 /mol_air

            #Assimilation in case of a limitation by the carboxylation rate (mol_CO2 /m2_LAI/s)
            #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
            b = gCO2*(Ca+Km) + Vcmax - Rd
            c = gCO2*((Ca+Km)*Rd - (Ca-GammaStar)*Vcmax)            
            Anet_c = (b - sqrt(b*b +4.*c))/2.

            #Resolution of minimum of Assimilation
            #Electron transport rate 
            #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
            theta = 0.9
            Q = self.Rs_Abs/ self.LAI*4.6e-6 #W /m2_soil to mol_photon /m2_LAI/s
            b = (alpha*Q +Jmax )/theta
            c = -alpha*Q * Jmax /theta
            J = (b - sqrt(b*b +4.*c))/2.

            #Assimilation in case of a limitation by the electron transfert rate (mol_CO2 /m2_LAI /s)
            #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
            b = gCO2*(Ca+2*GammaStar) + J/4. - Rd
            c = gCO2*((Ca+2*GammaStar)*Rd - (Ca-GammaStar)*J/4.)
            Anet_j = (b - sqrt(b*b +4.*c))/2.

            #net assimilation is the minimal of the  assimilation limited by J or Vc. Convertion of mol_CO2 /m2_LAI /s to g_C /m2_soil /hour
            self.Anet= min(Anet_j, Anet_c) * (12 * self.LAI* 3600)

        else: 
            self.Anet = 0


