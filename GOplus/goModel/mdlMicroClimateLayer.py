# EN COURS DE DEVELOPPEMENT ....

from ..goBases import *


class MicroClimateLayer(ELT):
    '''Group of a microclimat physical properties
        - many of the properties are only grouped in this type of object and define outer. 
        -  air property linked to the temperature, pressure and vapour content are computed
    ''' #TODO : unadapted

    #Outer elements
    upperMicroClimate = eltOut('MicroClimateLayer')
    underMicroClimate = eltOut('MicroClimateLayer')


    #radiative flux 
    RsDif =  var('down diffuse solar radiation (W/m2)', 0)
    RsDir =  var('down direct solar radiation (W/m2)', 0)
    RsUp =  var('up solar radiation (W/m2)', 0)
    RthDw =  var('down long wave radiation (W/m2)', 0)
    RthUp =  var('up long wave radiation (W/m2)', 0)
    
    #input air properties
    TaC  = var('air temperature in degre celsius (degC)', 20)
    e = var('vapour pressure (Pa)', 2000)
    P = var( 'atmospheric pressure ( Pa)',  101600)    
    
    #other climatic properties
    Rain  =var('rainfall (Kg_H2O /m2_soil /hour)')
    u = var('wind speed (m /s)', 0)
    CO2  = var('air CO2 concentration (ppm)', 385)
    
    #vars
    TaK  = var('air temperature in degre Kelvin (degK)')
    es  = var('vapour pressure at saturation (Pa)')
    s = var('des/dT at T (Pa/degC)')
    d =var('vapour pressure deficit (Pa)')
    dq = var('vapour mass deficit (g_H2O /Kg_air)')
    Rho_Cp = var('heat capacity of air (J /m3_air /K)')
    Lambda = var('vapourisation heat (J /Kg_H2O)')
    Gamma = var('psychrometric constant Gamma (Pa /K)')
    
    def ex_update(self):
    
        #temperature
        self.TaK = self.TaC + 273.15

        #Pression de vapeur saturante (Pa) - Buck 1981
        self.es = (1.0007 + 0.0000000346 * self.P) * 611.21 * exp(17.502 * self.TaC / (240.97 + self.TaC))
        self.s =  self.es * (17.502 * 240.97) / (240.97 + self.TaC) ** 2
        
        #air  vapour properties        
        self.d = max(0, self.es - self.e)
        self.dq = self.d * 0.622 / self.P * 1000
        self.Lambda = 1000000 * (2.501 - 0.00238 * self.TaC) 
        
        #thermodynamics properties of air
        _Cp = 1007         
        self.Rho_Cp = (1.292 - 0.0047132 * self.TaC + 0.000015058 * self.TaC ** 2) * _Cp
        self.Gamma = self.P * _Cp / (0.622 * self.Lambda)


    z_base = var('z at the base of the microClimate layer (m)', 20) 
    
    displacement_height = var('displacement height (m)')
    roughness_length = var('roughness length for momentum (m)')
    
    def update(self):
        pass

    @pcs
    def pcs_aerodynamic_status(self, 
#       zref,    #reference height       (m)
#       Ta_zref,     #Tair at zref (degC)
#       u_zref,  #wind speed at zref (m /s)
#       d,# displacement height      (m)
#       z0,  #roughness length for momentum      (m)
#       Ts,  #T surface      (DegC)
        ):
        #CONSTANTS
        s= p.container
        upperMC = self.upperMicroClimate
        surface = self.surface
       
       #relative z
       z_relatif = (upperMC.z_base - self.displacement_height - self.roughness_length)/self.roughness_length
       
        #Nombre de Richardson that determine the type of air condition
        g = 9.81        #acceleration pesanteur
        RiB =g*(1-surface.TsK/upperMC.TaK)*z_relatif * self.roughness_length/(upperMC.u**2)  #Nombre de Richardson (bulk)        

        if RiB <-0.05: #Instable condition  
            z_on_L = RiB
            X   =(1-16*z_on_L)**(1/4.)
            Fim = 2*log((1+X)/2.)+log((1+X**2)/2.)-2*atan(X)+pi/2.

        elif RiB > 0.05: #Stable condition
            z_on_L = min(0.2, RiB/(1-5*RiB))
            Fim = -5 * z_on_L
            
        else : #Neutral condition
            Fim =0

        #aerodynamique resistance for momentum
        k = 0.41    #von Karman b constant

        self.raM = (log(z_relatif) - Fim)**2/(k**2*u_zref) #(s /m)
--->            
        #u*
        self.ustar = max(0.01, u_zref*k/(log(z_relatif) + Fim))
        




