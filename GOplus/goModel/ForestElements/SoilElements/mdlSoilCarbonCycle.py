from ....goBases import *

class SoilCarbonCycle(ELT):
    ''' Soil carbon decomposition adapted from RothC model:
        - time steph --> daily
        - a plowing factor is add as ponderation of the decomposition rate
        - see Moreaux V. - 2012
    '''

    # Outer elements
    locTime = eltOut('LocTime element')
    microclim = eltOut('MicroClimate upper soil')
    treeStand = eltOut('TreesStand element')
    underStorey = eltOut('UnderStorey element')
    waterCycle = eltOut('SoilWaterCycle element')
    
    #TODO :  manage temperature on the Surface module (if converted on a energy module)
    Ts_resp = var('soil temperature  at depth of maximal respiration activity (degC)', 7.0)
    Ts_prof   = var('soil temperature at depth(degC)', 11.81)
    Ra  = var('autotrophic respiration of soil (gC /m2_soil /hour)')
    
    @pcs
    def update(self, 
        kTresp_Ta = param('coeffient in restore force of Ts_resp to Ta (-)', 0.01128), 
        kTresp_Tp = param('coeffient in restore force of Ts_resp to Ts_prof (-)', 0.004588), 
        ):
        
        #estimation of the soil temperature at 10 cm depth (2 restoring forces : Ta and Ts_prof)
        # Rmq :bien que cette formulation empirique marche bien il faudrait la faire evoluer
        #      pour etre en coherence avec le bilan d#energie et inversement l#inclure dandans le bilan d#energie       
        self.Ts_resp += kTresp_Ta * (self.microclim.TaC - self.Ts_resp) + kTresp_Tp * (self.Ts_prof - self.Ts_resp)
        self.Ts_prof = (self.Ts_prof * 500000.0 + self.Ts_resp) / (500000.0 + 1)

        #heterotrophe respiration estimate from Roth 
        self.pcs_decomposition_RothC()

        #autotrophe respiration
        self.Ra = self.treeStand.R_UnderGround + self.underStorey.R_UnderGround


    #vars
    HUM  = var('humified organic matter (gC /m2_soil)',  7686.0)
    BIO  = var('microbial biomass (gC /m2_soil)',  588.0)
    DPM  = var('decomposable plant material (gC /m2_soil)',  367.0)
    RPM  = var('resistant plant material (gC /m2_soil)',  514)
    IOM  = var('resistant to decomposition carbon (gC /m2_soil)',  1851)
    Rh  = var('CO2 product (gC /m2_soil /hour)', 0.) #TODO : change time step evaluation to avoid init need
    HUM_age  = var('humified organic matter age (y)', 220)
    BIO_age  = var('microbial biomass age (y)',  38)
    DPM_age  = var('decomposable plant material age (y)',  5)
    RPM_age  = var('resistant plant material age (y)',  12)
    IOM_age  = var('resistant to decomposition carbon age (y)',  50000)
    Rh_age  = var('CO2 product age (y)', 0.)#TODO : change time step evaluation to avoid init need
    PlowingFactor = var('soil carbon fraction affected by the plowing  [0-1] ', 0)

    @pcs    
    def pcs_decomposition_RothC(self, 
        clay = param('soil clay content ([0-100%])', 2.8),#TODO: see how to use a clay properties apply at soil level
        k_HUM = param('decomposition rate of HUM (/y)', 0.02), 
        k_BIO = param('decomposition rate of BIO (/y)',  0.66), 
        k_DPM = param('decomposition rate of DPM (/y)',  10), 
        k_RPM = param('decomposition rate of RPM (/y)',  0.16), 
        PlowEffect_HalfTime = param('half time of plowing effect (day)',  92.4196241), 
        k_PlowEffect = param('plowing coefficient effect', 3*0), 
        ):
        
        #Daily reevalution of soil carbon compartments
        if self.locTime.isDayEnd : 
            
            _dage = 1.0 / 365.25
            
            _x= 1.67 * (1.85 + 1.6 * exp(-0.0786 * clay))
            _RothC_xClay = _x/(1.0+_x) #clay constant effect on CO2 rate
            
            #evaluate empirical a,b,c factors and combinaison that control decomposition rate in fonction soil statuts
            _a = 47.9 / (1 + exp(106 / (self.Ts_resp + 18.3)))
            _b = 0.2 + (1 - 0.2) * (1 - self.waterCycle.MoistureDeficit)
            _c = 0.6
            _d = 1.0 + k_PlowEffect * self.PlowingFactor
            _abcd = _a * _b * _c * _d * _dage
            
            #Decomposed part of each compartment
            _DPM_dec = self.DPM * (1 - exp(-k_DPM * _abcd))
            _RPM_dec = self.RPM * (1 - exp(-k_RPM * _abcd))
            _BIO_dec = self.BIO * (1 - exp(-k_BIO * _abcd))
            _HUM_dec = self.HUM * (1 - exp(-k_HUM * _abcd))
            _dec = _DPM_dec + _RPM_dec + _BIO_dec + _HUM_dec
            _dec_age = (_DPM_dec * (self.DPM_age + _dage) + _RPM_dec * (self.RPM_age + _dage) + _BIO_dec * (self.BIO_age + _dage) + _HUM_dec * (self.HUM_age + _dage)) / _dec
            
            #Decomposition allocation
            _to_CO2_rate = _RothC_xClay * (1 - self.PlowingFactor) + 1 * self.PlowingFactor
            _to_BIO_rate = 0.46 * (1 - _to_CO2_rate)
            _to_HUM_rate = 0.54 * (1 - _to_CO2_rate)
            
            #New pool content
            self.DPM = self.DPM - _DPM_dec 
            self.RPM = self.RPM - _RPM_dec 
            self.BIO,  _BIO = (self.BIO - _BIO_dec) + _dec * _to_BIO_rate,  self.BIO
            self.HUM,  _HUM = (self.HUM - _HUM_dec) + _dec * _to_HUM_rate,  self.HUM
            
            #New pool age
            self.DPM_age = self.DPM_age + _dage 
            self.RPM_age = self.RPM_age + _dage
            self.BIO_age = ((_BIO - _BIO_dec) * (self.BIO_age + _dage) + _dec * _to_BIO_rate * _dec_age) / self.BIO
            self.HUM_age = ((_HUM -_HUM_dec) * (self.HUM_age + _dage) + _dec * _to_HUM_rate * _dec_age) / self.HUM
            
            #Heterotrophic respiration result
            self.Rh = _dec * _to_CO2_rate / 24.
            self.Rh_age = _dec_age
            
            #Plowing effect attenuation
            self.PlowingFactor *= 0.5 ** (1.0 / (PlowEffect_HalfTime- 1))
    
    def incorporateACarbonLitter(self, 
        carbonLitter, #carbon litter mass (gC /m2_soil)
        carbonLitter_DPM_RPM_ratio,  #decomposable on resistante part of carbon litter (-)
        carbonLitter_age, #carbon age of carbonLitter (year)
        ):
        '''call by other model element to specified their liter part contribution at stand level
        '''

        if carbonLitter > 0 :
            _IDPM = carbonLitter * carbonLitter_DPM_RPM_ratio / (1 + carbonLitter_DPM_RPM_ratio)
            self.DPM_age =  (self.DPM * self.DPM_age + _IDPM * carbonLitter_age) / (self.DPM + _IDPM)            
            self.DPM += _IDPM

            _IRPM = carbonLitter * 1.0 / (1 + carbonLitter_DPM_RPM_ratio)
            self.RPM_age = (self.RPM  * self.RPM_age + _IRPM * carbonLitter_age) / (self.RPM +  _IRPM)
            self.RPM += _IRPM


