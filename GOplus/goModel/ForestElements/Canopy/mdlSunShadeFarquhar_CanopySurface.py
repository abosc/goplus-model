# -*- coding: utf-8 -*-

from ....goBases import *

class SunShadeLeafLayer(ELT):
    Rs_Abs = var('shortwave radiation absorbed (W /m2_soil)')

    LAI = var('Part of the canopy LAI associated with this fraction (m2_LAI /m2_soil)')
    Anet = var('Assimilation net (g_C /m2_soil /hour)')

class SunShadeCanopySurface(ELT):
    '''Canopy surface exchanges modelised according to Sun /Shade model approach (DePury and Farquhar 1997)'''

    # Outer elements
    locTime = eltOut('LoctTime element')
    sunLocal = eltOut('SunLocal element')
    microclim = eltOut('Upper MicroClimate element')
    microclim_under = eltOut('Under MicroClimate element')
    soil = eltOut('Soil element')

    #Inner elements
    sunLayer = eltIn(SunShadeLeafLayer)
    shadeLayer = eltIn(SunShadeLeafLayer)

    #state variables define outer
    LAI = var('Leaf area Index (m2_leafAreaIndex / m2_soil)', 1.)
    WaterPotential = var('leaf water potential (MPa)', 0.)

    def update(s):
        #Energy balance processes
        s.pcs_AerodynamicConductance()
        s.pcs_StomatalConductance()
        s.pcs_ShortWaveBalance()
        s.pcs_EnergyBalance()

        #Water balance processes
        s.pcs_EvapoTranspiration()
        s.pcs_CanopyRainInterception()

        #Carbon balance processes
        s.pcs_AssimilationFarquhar()


    #AERODYNAMIC CONDUCTANCE
    #  we considere that it is the same for H and LE  : TODO --> change that
    Ga = var('aerodynamic conductance (m /s)')
    u_surface = var('wind speed at canopy surface (m /s)')
    height_surface  = var('heigth of the surface (m)')

    @pcs
    def pcs_AerodynamicConductance(self):
        '''Process the aerodynamique conditions'''
            
        if self.container.density >0:
            
            #CONSTANTS
            k = 0.41    #von Karman b constant
            alpha=0.000724  #Nakai et al. 2008
            beta=0.273  
            
            #r heig
            self.height_surface = max(0.20, self.container.HEIGHTmean) #always upper soil litter height
            d   =(1-((1-exp(-alpha*self.container.density))/(alpha*self.container.density))*((1-exp(-beta*self.LAI))/(beta*self.LAI+0.000000001)))*self.height_surface   #displacement height        (m)
            z0 = 0.264*(self.height_surface-d) #    roughness length for momentum
            
            if z0>0:
                #u*
                ustar = self.microclim.u*k/log((self.microclim.z_ref - d)/z0)

                #wind speed at canopy surface
                self.u_surface = ustar/k*log((self.height_surface-d)/z0) 
                if self.u_surface<0:raise Exception('u negative')
                
                #aerodynamique  resistance for momentum
                raM = self.microclim.u /ustar**2
                
                #Use constant boundary conductance, in place of DL formule <-- need reference
                self.Ga = 1 / (raM + 1 / 0.04)
            
            else:
                self.height_surface = self.microclim.z_ref 
                self.u_surface = self.microclim.u
                self.Ga=0
            
        else:
            self.height_surface = self.microclim.z_ref 
            self.u_surface = self.microclim.u
            self.Ga=0


    # STOMATAL CONDUCTANCE
    g_stom = var('stomatal conductance (m3_vapour /m2_leafAreaIndex /s = m/s)', 0)
    g_stom_unstress = var('stomatal conductance without hydric stress (m3_vapour /m2_leafAreaIndex /s = m/s)')

    @pcs
    def pcs_StomatalConductance(self, 
        g_stom_Max = param('maximal stomatal conductance (m/s)', 0.00424 * 2.57), 
        k_Rsabs_P50 = param('Leaf solar radiation absorded for 50%  of stomatal conductance ponderation (W /m2_LAI)', 69.94) , 
        k_Rsabs_Curv = param('Curvature parameter of radiative ponderation of stomatal conductance (-)', 1.13), 
        k_VPD_P100 = param('VPD that start to close stomata (Pa)', 728), 
        k_VPD_Curv = param('Curvature parameter of VPD ponderation of stomatal conductance (-)',1.08), 
        k_Yleaf_P0 = param('Leaf water potential at stomata closure (MPa)',-1.80), 
        k_Yleaf_Curv = param('Curvature parameter of leaf water potential ponderation of stomatal conductance (-)',0.2), 
        k_time_P50 = param('time for 50% response of stomatal conductance to stationnary state (min.)', 12.), 
        ):

        '''Pinus pinaster Stomatal conductance from A Bosc - 1999 - Thesis model :
        - Jarvis approach 
        - unequilibrate with stationnary response
        - parameters are rearranged from those of A. Bosc 1999 to give it unit meaning
        '''
        if self.LAI > 0.001:
            #radiation control of stomata
            _pond_Rs = 1 - 1 / (1 + ( self.Rs_Abs /self.LAI/k_Rsabs_P50) ** k_Rsabs_Curv)

            #hydric stress controls of stomata
            _pond_VPD =  1 / (max(1, self.microclim.d /k_VPD_P100) ** k_VPD_Curv)        
            _pond_Yleaf = max(0, 1- self.WaterPotential/k_Yleaf_P0)**k_Yleaf_Curv

            #transitionnal Gstom between last value and stationnary response
            _g_Stat =  g_stom_Max * _pond_Rs * _pond_VPD * _pond_Yleaf
            self.g_stom =  _g_Stat +(self.g_stom -_g_Stat)*2**(-60./k_time_P50)

            #stomatal conductance without hydric stress
            self.g_stom_unstress =  g_stom_Max * _pond_Rs 

        else:
            self.g_stom = 0
            self.g_stom_unstress =0

    # SHORT WAVE BALANCE
    RsDir_Int = var('direct shortwave radiation intercepted (W /m2_soil)', 0)
    RsDif_Int = var('diffuse shortwave radiation intercepted (W /m2_soil)', 0)
    RsUp_Int = var('upward shortwave radiation intercepted (W /m2_soil)', 0)
    Rs_Sct_Up = var('shortwave radiation reflected up(W /m2_soil)', 0)
    Rs_Sct_Dw = var('shortwave radiation reflected down(W /m2_soil)', 0)
    Rs_Abs = var('shortwave radiation absorbed (W /m2_soil)', 0)

    @pcs
    def pcs_ShortWaveBalance(self, 
        k_Beam = param('Extinction coefficient of canopy for perpendicular beam radiation taking into account of aggregation factor ', 0.33),  #Hassika et al (1997)
        k_d = param('diffuse shortwave extinction coefficient taking into account of aggregation factor', 0.467),#Hassika et al (1997)
        rho_l = param('Leaf reflection coefficient for shortwave (_)', 0.09),  #Berbigier and Bonnefond (1995)
        theta_l  = param('Leaf transmissivity for shortwave (_)', 0.014), #Berbigier and Bonnefond (1995)
        rho_cd  = param('Canopy reflection coefficient for diffuse shortwave (_)', 0.036), 
        ):
        '''Shortwave absorption is partionned between a Sun and a Shade layer (DePury and Farquhar 1997)
            We add the source of beam and diffuse from under 'layer'
        '''
        #TODO : it could be better to  evaluated :
        #   - in a  first time, proportion of sun shortwave (Dir and Dif) intercepted and reflected for each strate  : only function of sinB and LAI
        #   - in a second time , absorbstion after to have integrated over strates * sun shortwave intensity
        
        microclim = self.microclim
        microclim_under = self.microclim_under
        L_c = self.LAI
        absorbance = 1- rho_l - theta_l #Leaf absorbance : (1-sigma) of DePury
        
        if L_c > 0 :
            #solar elevation
            sinB = self.sunLocal.SinSunElevation
            if sinB >0:

                #modified radiation extinction coefficient of canopy to take into account the solar angle and the scattering effect [eq: A4]
                k_b = k_Beam / sinB
                kp_b = k_b * absorbance**0.5 
                kp_d = k_d * absorbance**0.5

                #canopy reflection coefficient for beam shortwave [eq: A20, A19]
                rho_h = (1-absorbance**0.5)/(1+absorbance**0.5)
                rho_cb= 1- exp(-2*rho_h * k_b/(1+k_b)) #with A19 correction (sign - before 2)

                # __CANOPY _____________________________________________
                #canopy shortwave components interception (W /m2_soil) .From  decomposition of [eq: 13] and extantion to RsUp
                self.RsDir_Int = microclim.RsDir * (1 - exp(-kp_b*L_c)) 
                self.RsDif_Int = microclim.RsDif * (1 - exp(-kp_d*L_c)) 
                self.RsUp_Int = microclim_under.RsUp * (1 - exp(-kp_d*L_c))

                #canopy shortwave components reflection (W /m2_soil): need to be verified to be in accordance with DePury
                self.Rs_Sct_Up  = rho_cb * self.RsDir_Int + rho_cd * self.RsDif_Int 
                self.Rs_Sct_Dw = rho_cd * self.RsUp_Int

                # __SUN LAYER __________________________________________
                #Sunlit leaf area index of the canopy (m2_LAI /m2_soil)) [eq: 18]
                self.sunLayer.LAI =(1 - exp(-k_b * L_c  )) / k_b

                #Fractions of beam , scaterred beam  and diffuse  shortwave absorbed by the sunLayer [eq: 20a]
                fracSunDir_abs = absorbance * (1 - exp(-k_b*L_c  )) #[eq: 20b]
                fracSunDirScat_abs = (1 - rho_cb)*(1-exp(-(kp_b + k_b)*L_c))*kp_b/(kp_b + k_b) - absorbance*(1 - exp(-2*k_b*L_c))/2 #[eq: 20d]
                fracSunDif_abs = (1 - rho_cd) * (1-exp(-(kp_d + k_b)*L_c)) * kp_d /(kp_d + k_b) #[eq: 20c]

                #Absorbed  shortwave by sunlit canopy fraction (W /m2_soil) [eq: 20a]
                #we take into account of RsUp (ignored by DePury)
                self.sunLayer.Rs_Abs = microclim.RsDir * ( fracSunDir_abs + fracSunDirScat_abs) + (microclim.RsDif  + microclim_under.RsUp) * fracSunDif_abs#
                
            else:
                kp_d = k_d * absorbance**0.5
                self.RsDir_Int = 0
                self.RsDif_Int = microclim.RsDif * (1 - exp(-kp_d*L_c)) 
                self.RsUp_Int = microclim_under.RsUp * (1 - exp(-kp_d*L_c))
                self.Rs_Sct_Up  = rho_cd * self.RsDif_Int
                self.Rs_Sct_Dw = rho_cd * self.RsUp_Int

                self.sunLayer.LAI = 0.
                self.sunLayer.Rs_Abs = 0.

        else:
            self.RsDir_Int = 0.
            self.RsDif_Int = 0.
            self.RsUp_Int = 0.
            self.Rs_Sct_Up  = 0.
            self.Rs_Sct_Dw = 0.

            self.sunLayer.LAI = 0.
            self.sunLayer.Rs_Abs = 0.            
        
        #Total absorbed  shortwave by canopy  (W /m2_soil) 
        self.Rs_Abs = (self.RsDir_Int + self.RsDif_Int + self.RsUp_Int) - (self.Rs_Sct_Up + self.Rs_Sct_Dw)

        # Shade Layer
        self.shadeLayer.Rs_Abs = max(0., self.Rs_Abs - self.sunLayer.Rs_Abs)
        self.shadeLayer.LAI = self.LAI - self.sunLayer.LAI




    #ENERGY BALANCE
   # Conductances composantes
    Gsa = var('stomatal - aerodynamique conductance (m /s)')
    Gtot = var('total leaf to air conductance (m /s)')

    # Longwave fluxes
    RthDw_Int = var('downward longwave radiation intercepted (W /m2_soil)', 0)
    RthUp_Int = var('upward longwave radiation intercepted (W /m2_soil)', 0)
    Rth_Sct_Up = var('longwave radiation reflected (W /m2_soil)', 0)
    Rth_Sct_Dw = var('longwave radiation reflected (W /m2_soil)', 0)
    Rth_Abs = var('longwave radiation absorbed (W /m2_soil)', 0)
    Rth_Emi = var('longwave radiation emitted (W /m2_soil)', 0)

    #Radiative balance
    Rnet_star = var('radiative balance in the case of a leaf area temperature equal to that of air  (W /m2_soil)')
    Rnet = var('radiative balance (W /m2_soil)')

    #HeatFlux
    dTsTa = var('leaf-air temperature gradient (degK)', 0)
    H = var('heat flux (W /m2_soil')

    # LatentFlux
    LE_DrySurface = var('latent flux of dry leaf area part  (W /m2_soil)')
    LE_WetSurface = var('latent flux of wet leaf area part  (W /m2_soil)')
    LE = var('latent flux (W /m2_soil)')

    @pcs    
    def pcs_EnergyBalance(self, 
        kLAI1_Rth_Int = param('parameter 1 of longwave radiation interception (-)',  -0.538), 
        kLAI2_Rth_Int = param('parameter 2 of longwave radiation interception (-)', 0.0177), 
        Emissivity = param('emissivity', 0.98) , 
        ):

        if self.LAI >0.001:
            _microclim = self.microclim
            _microclim_under = self.microclim_under

            #exchange coefficients for long wave independant of surface temperature
            _K_IntRth = 1 - exp((kLAI1_Rth_Int  + kLAI2_Rth_Int * self.LAI )*self.LAI)
            _Sigma = 0.000000056703 # Stefan-Boltzmann constant (W /m2 /K^4)
            _K_EchRth = 8 * _K_IntRth * Emissivity * _Sigma * _microclim.TaK ** 3

            #longwave fluxes intercepted
            self.RthDw_Int = _K_IntRth * _microclim.RthDw
            self.RthUp_Int = _K_IntRth * _microclim_under.RthUp

            #longwave fluxes reflected
            self.Rth_Sct_Up = (1-Emissivity)* (self.RthDw_Int  * 0.75 + self.RthUp_Int * 0.25)
            self.Rth_Sct_Dw = (1-Emissivity)* (self.RthDw_Int  * 0.25 + self.RthUp_Int * 0.75)

            #longwave fluxes absorbed
            self.Rth_Abs = (self.RthDw_Int + self.RthUp_Int) - (self.Rth_Sct_Up + self.Rth_Sct_Dw)

            #Conductance totale
            _Ga = self.Ga
            try:
                self.Gsa = 1 / (1 / _Ga + 1 / (self.LAI*self.g_stom))
            except:
                self.Gsa =0

            #radiative balance in the case of a temperature surface egal to that of air
            self.Rnet_star = (self.Rs_Abs + self.Rth_Abs) - 2 * _K_IntRth * Emissivity * _Sigma * _microclim.TaK ** 4

            #test if we are in condition of condensation to use the appropiate Gtot formulation
            #TODO : verified this conditionnal formulation of Gtot. Why not use always the second part
            if ((_K_EchRth + _Ga * _microclim.Rho_Cp) * _microclim.d + _microclim.s * self.Rnet_star) < 0 :
                self.Gtot = _Ga
            else :
                self.Gtot = self.DrySurfaceFraction * self.Gsa + (1 - self.DrySurfaceFraction) * _Ga

            #air-surface temperature difference
            self.dTsTa = (self.Rnet_star - self.Gtot * (_microclim.Rho_Cp /_microclim.Gamma) * _microclim.d) / (_K_EchRth + _microclim.Rho_Cp * (_Ga + self.Gtot * _microclim.s * 0 / _microclim.Gamma))  # pourquoi le 0/gamma
            self.dTsTa=max(-15, min(self.dTsTa, 15)) 

            #longwave flux emitted
            self.Rth_Emi = 2 * _K_IntRth * Emissivity * _Sigma * (_microclim.TaK + self.dTsTa) ** 4

            #sensible heat flux 
            self.H = _Ga * _microclim.Rho_Cp * self.dTsTa

            #net radiation
            self.Rnet = self.Rnet_star - _K_EchRth * self.dTsTa

            #Evaporation of wet canopy part and evapotranspiration of dry canopy part
            # 2008-12-11 ATTENTION :
            #       Le differentiel de temperature surface-air n'est pas pris en compte dans la formule suivante de _LEgradient car
            #       les modeles de Gstom employees ont ete parametres en considerant que la temperature de l'aiguille etait egale a celle de l'air.
            #       Normalement cette consideration ne devrait pas s'appliquer a LE_WetSurface.  --> evolution necessaire
            _LEgradient = _microclim.Rho_Cp / _microclim.Gamma * (_microclim.d + _microclim.s * self.dTsTa * 0)

            if _LEgradient > 0 :
                self.LE_WetSurface = _Ga * _LEgradient * (1 - self.DrySurfaceFraction)
                self.LE_DrySurface = self.Gsa * _LEgradient * self.DrySurfaceFraction
            else :
                self.LE_WetSurface = _Ga * _LEgradient
                self.LE_DrySurface = 0

            self.LE = self.LE_DrySurface + self.LE_WetSurface

        else:
            self.Gtot = 0
            self.Gsa = 0
            self.RthDw_Int = 0
            self.RthUp_Int = 0
            self.Rth_Sct_Up = 0
            self.Rth_Sct_Dw = 0
            self.Rth_Abs = 0
            self.Rnet_star = 0
            self.dTsTa = 0
            self.Rth_Emi = 0
            self.H = 0
            self.Rnet = 0
            self.LE_WetSurface = 0
            self.LE_DrySurface = 0
            self.LE = 0


    #VAPOUR FLUXES
    Transpiration = var('transpiration (Kg_H2O /m2_soil /hour)')
    Evaporation = var('evaporation of water retained on leaf surface (Kg_H2O /m2_soil /hour)')
    ETR = var('evapotranspiration (Kg_H2O /m2_soil /hour)')

    @pcs
    def pcs_EvapoTranspiration(self):
        '''canopy evapotranspiration
        '''

        #convert the latent heat flux (W/ m2) in Evapotranspiration (Kg_H2O/ m2 /hour)
        _factor = 3600./self.microclim.Lambda
        self.Transpiration = self.LE_DrySurface * _factor
        self.Evaporation = self.LE_WetSurface * _factor
        self.ETR = self.Transpiration + self.Evaporation 


    # RAINFALL RETENTION
    InterceptedRain = var('rain intercepted by leaf (Kg_H2O /m2_soil /hour)')
    Draining = var('rain intercepted by leaf lost by draining (Kg_H2O /m2_soil /hour)')
    WaterSurfaceContent = var('water storage content on leaf surface (Kg_H2O /m2_soil)', 0.)
    DrySurfaceFraction = var('rate of leaf surface dry ([0-1])', 1.)

    @pcs
    def pcs_CanopyRainInterception(self, 
        kRainInt_LAI = param('parameter of rain interception by leaf (-)',  -0.33), 
        SurfaceWaterStorageCapacity = param('water storage capacity by leaf area index(Kg_H2O /m2_leafAreaIndex)', 0.125 * 2.57), 
        ):
        '''Process interception of rain by the canopy  '''

        if self.LAI>0:
            _waterSurfaceCapacity = self.LAI * SurfaceWaterStorageCapacity

            #part of rain intercepted (mm/h),  draining  (mm/h) (Loustau et al. 1992 J. of Hydrol.)
            self.InterceptedRain = self.microclim.Rain * (1 - exp(kRainInt_LAI * self.LAI))
            self.Draining = max(0, (self.WaterSurfaceContent + self.InterceptedRain - self.Evaporation) - _waterSurfaceCapacity)

            #canopy water surface content
            self.WaterSurfaceContent = max(0, self.WaterSurfaceContent + (self.InterceptedRain - self.Evaporation - self.Draining))
            self.DrySurfaceFraction = 1 - self.WaterSurfaceContent / _waterSurfaceCapacity

        else:
            self.InterceptedRain =  self.Draining = self.WaterSurfaceContent = 0.
            self.DrySurfaceFraction = 1.


    #ASSIMILATION   
    Assimilation = var('Raw assimilation  (g C /m2_soil /hour)')
    Respiration = var('Dark respiration  (g C /m2_soil /hour)')

    @pcs
    def pcs_AssimilationFarquhar(self, 
        #Biochemistry photosynthetic parameters at the reference temperature and activation energies
        #from Bernacchi et al. 2001 in Medlyn et al. 2002    
        Kc_25= param('Michaelis-Menten constant of rubisco for CO2 at 25 degC (mol_CO2 /mol)', 404.9e-6),#Medlyn et al. 2002 [eq 5]
        Ea_Kc = param('Activation energy for Kc (J /mol)',  79430. ),#Medlyn et al. 2002 [eq 5]
        Ko_25 = param('Michaelis-Menten constant of rubisco for O2 at 25 degC (mol_O2 /mol)',278.4e-3),#Medlyn et al. 2002 [eq 6]
        Ea_Ko =   param('Activation energy for Kc (J /mol)', 36380.),#Medlyn et al. 2002 [eq 6]
        GammaStar_25 = param('CO2 compensation point of photosynthesis in the absence of mitochondrial respiration (mol_CO2 /mol_air : ppm)', 42.75e-6),#Medlyn et al. 2002 [eq 12]
        Ea_GammaStar = param('Activation energy for GammaStar (J /mol)', 37830.),#Medlyn et al. 2002 [eq 12]

        #Medlyn et al. 2002 
        Vcmax_25 = param('Vcmax at 25 degC, expressed on a one-sided leaf area basis (mol_CO2 /m2_LAI /s))',  89.98e-6),#Medlyn et al. 2002 [tb 2]
        Ea_Vcmax = param('Activation energy for Vcmax (J /mol)', 62220.),#Medlyn et al. 2002 [tb 2]

        Jmax_25 = param('Jmax at 25 degC, expressed on a one-sided leaf area basis (mol_e /m2_LAI /s', 154.74e-6),#Medlyn et al. 2002 [tb 3]
        Ha_Jmax = param('Activation energy for Jmax (J /mol)', 34830.),#Medlyn et al. 2002 [tb 3]
        Hd_Jmax = param('Deactivation energy for Jmax (J /mol)', 200000.),#Medlyn et al. 2002 [tb 3]
        TCopt_Jmax = param('temperature of Jmax optimum (deg_C)', 36.87),#Medlyn et al. 2002 [tb 3]
        alpha = param('Quantum yield of electron transport (mol_e /mol_photon_absorbed). \
                Litterature value obtained on Rs intercepted need to be corrected for leaf absorbance', 0.124/0.9),#Porte 1998 [tb 2]s

        Rd_25 = param('Dark leaf respiration at 25 degC (mol_CO2 /m2_LAI /s)',  0.8e-6),  #Porte 1998 [tb 2] ponderate value
        Ea_Rd= param('Activation energy for Rd (J /mol)', 46390),                                     # ##to update

        ):
        ''' Process photosynthesys along Farquhar's model for each sun and shade layers
            Resolution of Anet from the system of equation of :
             - Farquhar model :  Anet =min(Ac,Aj) - Rd
             - Diffusivity of CO2 trouth stomata :  Anet = gc(Ca - Ci)
            Along Medlyn 2002, parameters (Vcmax,Jmax,Rd)  and internal variables (gCO2,Q, J, Aj, Ac,A net) 
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

            #Resolution of minimum of Assimilation limitation for each layer
            for layer in (self.sunLayer, self.shadeLayer):
                if layer.LAI >0:
                    #Electron transport rate 
                    #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
                    theta = 0.9
                    Q = layer.Rs_Abs/ layer.LAI*4.6e-6 #W /m2_soil to mol_photon /m2_LAI/s
                    b = (alpha*Q +Jmax )/theta
                    c = -alpha*Q * Jmax /theta
                    J = (b - sqrt(b*b +4.*c))/2.

                    #Assimilation in case of a limitation by the electron transfert rate (mol_CO2 /m2_LAI /s)
                    #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
                    b = gCO2*(Ca+2*GammaStar) + J/4. - Rd
                    c = gCO2*((Ca+2*GammaStar)*Rd - (Ca-GammaStar)*J/4.)
                    Anet_j = (b - sqrt(b*b +4.*c))/2.

                    #net assimilation is the minimnetal of the  assimilation limited by J or Vc. Convertion of mol_CO2 /m2_LAI /s to g_C /m2_soil /hour
                    layer.Anet = min(Anet_j, Anet_c) * (12 * layer.LAI* 3600)

                else:
                    layer.Anet = 0
                
            #Assimilation and respiration of the canopy (g_C /m2_soil /hour)
            self.Respiration = Rd * (12 * self.LAI* 3600)
            self.Assimilation = self.sunLayer.Anet + self.shadeLayer.Anet + self.Respiration 

        else: 
           self.Respiration = self.Assimilation = self.sunLayer.Anet = self.shadeLayer.Anet = 0


