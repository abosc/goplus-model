from ....goBases import *

#TODO : separate the sub process as BigLeafCanopySurface

class SoilSurface(ELT):
    ''' Soil water contents cycle 
    '''

    # Outer elements
    microclim = eltOut('MicroClimate upper soil')

    
    def update(self):
        #canopy hydric balance, part 1: evaluation of the dry fraction
        self.DrySurfaceFraction = 1 - self.WaterSurfaceContent / (1 * self.pcs_waterBalance.SurfaceWaterStorageCapacity)
        
        self.pcs_energyBalance()
        self.pcs_waterBalance()        

    #ENERGY BALANCE
   # Conductances composantes
    Gsa = var('surface - aerodynamique conductance (m /s)')
    Gtot = var('total leaf to air conductance (m /s)')

    # RadiativeFlux
    RsDir_Int = var('direct shortwave radiation intercepted (W /m2_soil)')
    RsDif_Int = var('diffuse shortwave radiation intercepted (W /m2_soil)')
    Rs_Int = var('total shortwave radiation intercepted (W /m2_soil)')
    Rs_Sct = var('shortwave radiation reflected (W /m2_soil)')
    Rs_Abs = var('shortwave radiation absorbed (W /m2_soil)')

    RthDw_Int = var('downward longwave radiation intercepted (W /m2_soil)')
    Rth_Sct = var('longwave radiation reflected (W /m2_soil)')
    Rth_Abs = var('longwave radiation absorbed (W /m2_soil)')
    Rth_Emi = var('longwave radiation emitted (W /m2_soil)')

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
    def pcs_energyBalance(self, 
        kGa_u = param('coefficient of aerodynamic conductance dependance to u (?)', 116), 
        Albedo = param('albedo (?)', 0.2), 
        Emissivity = param('emissivity', 0.98) , 
        ):

        _microclim = self.microclim

        #Diffuse and beam shortwave interception
        self.RsDif_Int = _microclim.RsDif 
        self.RsDir_Int = _microclim.RsDir 

        #total shortwave interception, reflection and absorption
        self.Rs_Int = self.RsDir_Int + self.RsDif_Int 
        self.Rs_Sct = self.Rs_Int * Albedo
        self.Rs_Abs = self.Rs_Int - self.Rs_Sct

        #exchange coefficients for long wave independant of surface temperature
        _K_IntRth = 1
        _Sigma = 0.000000056703 # Stefan-Boltzmann constant (W /m2 /K^4)
        _K_EchRth = 8 * _K_IntRth * Emissivity * _Sigma * _microclim.TaK ** 3
        
        #longwave fluxes components absorbed and reflected
        self.RthDw_Int = _K_IntRth * _microclim.RthDw
        self.Rth_Abs = self.RthDw_Int * Emissivity
        self.Rth_Sct = self.RthDw_Int  - self.Rth_Abs
        
        
        #Aerodynamic conductance
        #CONSTANTS
        k = 0.41    #von Karman b constant
        
        #layer_aerodynamic_sizes
        height_surface = 0.15 #TODO : link to litter sizes
        z0 = 0.01 #    roughness length for momentum
        d = 0.9*(height_surface-z0)

        #u*
        ustar = self.microclim.u*k/log((self.microclim.z_ref - d)/z0)
        
        #aerodynamique  resistance for momentum
        raM = self.microclim.u /ustar**2
        _Ga = 1/raM
        
        #Surface resistance in function of soilwater content - Van de Grien and Owe (1994) ((in Bitelli et al. 2008, J hydrol.) <-- DL
        _waterCycle = self.container.waterCycle
#            raS = 10* exp(0.3563*(_waterCycle.w_WP - _waterCycle.w_A)) #Van de Grien and Owe (1994) ((in Bitelli et al. 2008, J hydrol.) <-- DL --> values to small
        if _waterCycle.w_A -_waterCycle.w_RES <= 0:
            raS = 1e8
        else:
            raS = 100.*((_waterCycle.w_SAT - _waterCycle.w_RES)/(_waterCycle.w_A -_waterCycle.w_RES) - 1) #raS=infini at w_RES, and raS=0 at w_SAT (free water)
        
        #Conductance totale
        self.Gsa = 1/(raM+raS)
        
##            #Conductance totale
##            # Gs = 0.1 * minof(1 / (2.55 * 10 ** 5 * exp(WaterContent * (-0.06))), 0.002)
##            _Gs = 0.1 *  0.002 ##en attendant une reformulation
##            _Ga = _microclim.u / kGa_u##en attendant une reformulation
##            if (_Gs > 0 and _Ga > 0) :
##                self.Gsa = 1 / (1 / _Ga + 1 / _Gs)
##            else :
##                self.Gsa = 0

        #radiative balance in the case of a temperature surface egal to that of air
        self.Rnet_star = (self.Rs_Abs + self.Rth_Abs) -  _K_IntRth * Emissivity * _Sigma * _microclim.TaK ** 4

        #test if we are in condition of condensation to use the appropiate Gtot formulation
        if ((_K_EchRth + _Ga * _microclim.Rho_Cp) * _microclim.d + _microclim.s * self.Rnet_star) < 0 :
            self.Gtot = _Ga
        else :
            self.Gtot = self.DrySurfaceFraction * self.Gsa + (1 - self.DrySurfaceFraction) * _Ga

        #air-surface temperature difference
        self.dTsTa = (self.Rnet_star - self.Gtot * (_microclim.Rho_Cp /_microclim.Gamma) * _microclim.d) / (_K_EchRth + _microclim.Rho_Cp * (_Ga + self.Gtot * _microclim.s  / _microclim.Gamma)) 
        self.dTsTa=max(-15, min(self.dTsTa, 15)) 

        #longwave flux emitted
        self.Rth_Emi =  _K_IntRth * Emissivity * _Sigma * (_microclim.TaK + self.dTsTa) ** 4
        
        #sensible heat flux 
        self.H = _Ga * _microclim.Rho_Cp * self.dTsTa

        #net radiation
        self.Rnet = self.Rnet_star - _K_EchRth * self.dTsTa

        #Evaporation of wet canopy part and evapotranspiration of dry layer part
        _LEgradient = _microclim.Rho_Cp / _microclim.Gamma * (_microclim.d + _microclim.s * self.dTsTa )

        if _LEgradient > 0 :
            self.LE_WetSurface = _Ga * _LEgradient * (1 - self.DrySurfaceFraction)
            self.LE_DrySurface = self.Gsa * _LEgradient * self.DrySurfaceFraction
        else :
            self.LE_WetSurface = _Ga * _LEgradient
            self.LE_DrySurface = 0

        self.LE = self.LE_DrySurface + self.LE_WetSurface


    #vars
    WaterSurfaceContent = var('water storage content on surface (Kg_H2O /m2_soil)', 0)
    DrySurfaceFraction = var('rate of surface dry ([0-1])')
    InterceptedRain = var('rain intercepted by surface (Kg_H2O /m2_soil /hour)')
    Draining = var('rain intercepted by surface lost by draining (Kg_H2O /m2_soil /hour)')
    ETR_DrySurface = var('ETR of water retained on  surface (Kg_H2O /m2_soil /hour)')
    ETR_WetSurface = var('ETR from soil porosity (Kg_H2O /m2_soil /hour)')
    ETR = var('evapotranspiration (Kg_H2O /m2_soil /hour)')

    @pcs    
    def pcs_waterBalance(self, 
        SurfaceWaterStorageCapacity = param('water storage capacity by surface area (Kg_H2O /m2_leaf)', 0.5), 
        ):
        '''Process hydric balance'''
        
        #convert the latent heat flux (W/ m2) in Evapotranspiration (Kg_H2O/ m2 /hour)
        self.ETR_DrySurface = self.LE_DrySurface / self.microclim.Lambda * 3600
        self.ETR_WetSurface = self.LE_WetSurface / self.microclim.Lambda * 3600
        self.ETR = self.ETR_DrySurface + self.ETR_WetSurface

        #part of rain intercepted (mm/h),  draining  (mm/h) and new water content retained on the  surface
        #Loustau et al. 1992 J of Hydrol
        self.InterceptedRain = self.microclim.Rain
        self.Draining = max(0, (self.WaterSurfaceContent + self.InterceptedRain - self.ETR_WetSurface) - SurfaceWaterStorageCapacity)

        #surface water surface content
        self.WaterSurfaceContent = max(0, self.WaterSurfaceContent + (self.InterceptedRain - self.ETR_WetSurface - self.Draining))
        self.DrySurfaceFraction = 1 - self.WaterSurfaceContent / (1 * SurfaceWaterStorageCapacity)
