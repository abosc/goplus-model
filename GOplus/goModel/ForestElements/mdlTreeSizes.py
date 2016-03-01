from ...goBases import *

class TreeSizes(ELT):
    # Outer elements
    locTime = eltOut('LocTime element')

    #biomasse production   allocation
    WaProducted = var('Aerial biomass producted (Kg_DM /year)', 0.)
    WrProducted = var('Root biomass producted (Kg_DM /year)', 0.)

    #biomass state variables
    Wa = var('aerial weight (Kg_DM)', 20.46)
    Wr = var('root weight (Kg_DM)', 3.02)
    
    #allometric dimensions models

    W = var('total tree weight (Kg_DM)')
    
    BranchSenescence = var('branch senescence (Kg_DM /year)', 0.)
    RootSenescence = var('root senescence (Kg_DM /year)', 0.)

    DBH = var('diameter at breast height (?cm)')
    Height = var('tree height (m)')

    LeafWeight = var('total leaf weight (Kg_DM)')
    OneYearCohortWeightMax = var('one year old cohort weight max (Kg_DM)', 0.)

    Wstem = var('stem weight (Kg_DM)')
    WstemLastYear = var('stem weight one year before(Kg_DM)')
    
    Wtaproot = var('taproot weight (Kg_DM)')
    
    Rm15 = var('maintenance respiration at 15degC  (g_C)')

    @pcs
    def update(self, 
        k_SenBch_1 = param('coefficient 1 of allometric equation to calculate branches senescence', 0.3678), 
        k_SenBch_2 = param('coefficient 2 of allometric equation to calculate branches senescence', 1.0966), 
        k_SenBch_3 = param('coefficient 3 of allometric equation to calculate branches senescence', -1.256), 
        k_SenRoot_1 = param('coefficient 1 of allometric equation to calculate roots senescence', 0.8), 
        k_SenRoot_2 = param('coefficient 2 of allometric equation to calculate roots senescence', 0.5), 
        k_SenRoot_3 = param('coefficient 3 of allometric equation to calculate roots senescence', 0), 
        k_Wn_1 = param('coefficient 1 of allometric equation to calculate total needle biomass', 1.7495), 
        k_Wn_2 = param('coefficient 2 of allometric equation to calculate total needle biomass', 0.8682), 
        k_Wn_3 = param('coefficient 3 of allometric equation to calculate total needle biomass', -0.761), 
        k_Wn1_1 = param('coefficient 1 of allometric equation to calculate cohort 1 biomass', 0.8212), 
        k_Wn1_2 = param('coefficient 2 of allometric equation to calculate cohort 1 biomass', 0.796), 
        k_Wn1_3 = param('coefficient 3 of allometric equation to calculate cohort 1 biomass', -0.602), 
        k_DBH_1 = param('coefficient 1 of allometric equation to calculate DBH', 3.633), 
        k_DBH_2 = param('coefficient 2 of allometric equation to calculate DBH', 0.42208), 
        k_DBH_3 = param('coefficient 3 of allometric equation to calculate DBH', -0.064594), 
        k_Height_1 = param('coefficient 1 of allometric equation to calculate tree height', 1.5814), 
        k_Height_2 = param('coefficient 2 of allometric equation to calculate tree height', 0.39745), 
        k_Height_3 = param('coefficient 3 of allometric equation to calculate tree height', 0.04182), 
        k_Wstem_1 = param('coefficient 1 of allometric equation to calculate stem biomass', 0.34387), 
        k_Wstem_2 = param('coefficient 2 of allometric equation to calculate stem biomass', 1.0628), 
        k_Wstem_3 = param('coefficient 3 of allometric equation to calculate stem biomass', 0.13145), 
        k_WreqWa_1= param('coefficient 1 of allometric equation to calculate Wr from Wa on an equilibrate tree' , 0.085365), 
        k_WreqWa_2= param('coefficient 1 of allometric equation to calculate Wr from Wa on an equilibrate tree' , 1.176316), 
        k_Wtaproot_1 = param('coefficient 1 of allometric equation to calculate taproot biomass', 0.0755), 
        k_Wtaproot_2 = param('coefficient 2 of allometric equation to calculate taproot biomass', 0.9989), 

        _flag = private('Flag to manage some initialisations', ELT), 
        ):

        '''update the tree biomasses and dimensions calculated allometrically from aerial or underground biomasses (Wa, Wr)
        '''
        #TODO : initialize fluxes 
        
        #biomass (kg_DM)
        self.Wa += self.WaProducted - self.BranchSenescence - self.OneYearCohortWeightMax  ##! now use OneYearCohortWeightMax  to reflected Leaf weigth loss isn't really adapted
        self.Wr += self.WrProducted - self.RootSenescence 
        
        #shortcut names
        _Age = self.container.Age
        _Age_aerial = self.container.Age_aerial
        _Wa = self.Wa
        _Wr = self.Wr
        
        #total tree biomass
        self.W = _Wa + _Wr

        #manager tree size: breastheight diameter (cm) and tree height (m)
        self.DBH = k_DBH_1 * (_Wa ** k_DBH_2)* (_Age_aerial ** k_DBH_3)
        self.Height = k_Height_1 *( _Wa ** k_Height_2 )*( _Age_aerial ** k_Height_3)

        #maximal weight  (Kg_DM) and leafarea (m2) of the future needle cohort 
##        #version A :total biomass is used in place of Wa after to have proportionnalize to the aerial biomass that equilibrate root biomass
##        #this relation  don't reflect the actual growth of the aerial part, in term of vigor or weather variability
##        _WaEqWr = (_Wr/self.k_WreqWa_1)**(1/self.k_WreqWa_2)
##        self.OneYearCohortWeightMax = self.k_Wn1_1 * (((_Wa+_Wr)/(1+_Wr/_WaEqWr))**self.k_Wn1_2 )* (_Age **self.k_Wn1_3)

##        #version B (2013-06-27):  link directly the biomass of the new cohort those allocated to aerial part  (as a fraction of that) 
##        # this version don't smooth the response and can generate negative surface area  if NPP is negative. 
##        #--> generate exponential comportement in the two direction
##        self.OneYearCohortWeightMax = 0.45*self.dWa
        
##            #version C (2013-09-11): as no interannual pool of C could be use to construct a allocation more mechanistic  allocation scheme
##            #this version mean the versions A and B
##            _WaEqWr = (_Wr/k_WreqWa_1)**(1/k_WreqWa_2)
##            _v_A = k_Wn1_1 * (((_Wa+_Wr)/(1+_Wr/_WaEqWr))**k_Wn1_2 )* (_Age **k_Wn1_3)
##            _v_B =  0.45*self.WaProducted
##            if self.locTime.isSimulBeginning :
##                self.OneYearCohortWeightMax = _v_A
##            else:
##                self.OneYearCohortWeightMax =0.5* _v_A+ 0.5*_v_B

##            #version D (2014-07-04): as no interannual pool of C could be use to construct a allocation more mechanistic  allocation scheme
##            #this version made the assumption than the new needle cohort primordium production is limited by :
##            #    -  A : the physical supportable value by crown structure 
##            #    - B : the carbon limitation
##            #--> generate the same problem than B version
##            _WaEqWr = (_Wr/k_WreqWa_1)**(1/k_WreqWa_2)
##            _v_A = k_Wn1_1 * (((_Wa+_Wr)/(1+_Wr/_WaEqWr))**k_Wn1_2 )* (_Age **k_Wn1_3)
##            _v_B =  0.45*self.WaProducted
##            if hasattr(_flag,'isInitialized') :
##                self.OneYearCohortWeightMax = min(_v_A, _v_B)
##            else:
##                self.OneYearCohortWeightMax =_v_A
##                _flag.isInitialized = True

        #version use : A (2014-07-07)
        #B version don't allow to simulate interannual variation of new needle area  without problem. 
        #So come back to version A. 
        _WaEqWr = (_Wr/k_WreqWa_1)**(1/k_WreqWa_2)
        self.OneYearCohortWeightMax = k_Wn1_1 * (((_Wa+_Wr)/(1+_Wr/_WaEqWr))**k_Wn1_2 )* (_Age **k_Wn1_3)

        #total leaf biomass (Kg_DM)
        self.LeafWeight = k_Wn_1 * (_Wa **k_Wn_2 )* (_Age_aerial **k_Wn_3)
        
        #stem biomass  the current and past year (Kg_DM)
        self.Wstem = k_Wstem_1 * (_Wa ** k_Wstem_2) * (_Age_aerial ** k_Wstem_3)
        self.WstemLastYear = k_Wstem_1 * (_Wa ** k_Wstem_2) * ((_Age_aerial - 1) ** k_Wstem_3)
        
        #taproot biomass (Kg_DM)
        self.Wtaproot =  k_Wtaproot_1 * (_Wa ** k_Wtaproot_2)
        
        #maintenance respiration at 15degC : composantes tronc + bches (LEN 2003, Bilan C bray) and conversion micromol/tree/s en gC/tree/heure
        #Attention il manque une composante racinaire
        _trunk_Rm15 = (0.0507 * self.DBH ** 1.605) 
        _brch_Rm15 =  (0.000984 * self.DBH ** 2.844)   

        self.Rm15 =(_trunk_Rm15 +_brch_Rm15) *(12 *1e-6) * 3600                         
