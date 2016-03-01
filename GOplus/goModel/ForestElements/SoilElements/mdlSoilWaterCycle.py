from ....goBases import *

class SoilWaterCycle(ELT):
    ''' Soil water contents cycle
        GRAECO Version SK18.1.1 - Update 11/09/2013 - Approche couche definie par leur teneur en eau et donc mobiles
            avec calcul de la recharge de la nappe pour Marie G.
    '''

    # Outer elements
    sunTime = eltOut('SunTime element')
    treeStand = eltOut('TreesStand element')
    underStorey = eltOut('UnderStorey element')
    surface = eltOut('SoilSurface element')

    #Soil properties parameters
    Dp_Soil = param("total soil depth (m)", 10.0)
    Dp_Roots = param("Root layer depth (m). Must be smaller than Dp_Soil", 0.75)
    w_SAT = param('Saturation (Kg_H2O /m3_soil)', 420)
    w_FC = param('Field capacity (Kg_H2O /m3_soil)',  187)
    w_WP = param('Wilt point (Kg_H2O /m3_soil)', 40)
    w_RES= param('Residual point (Kg_H2O /m3_soil)', 30) #TODO : ne devrait pas etre utile car devrait juste etre le point limite d'extraction de l atmosphere
    kAds_wA = param('kAds_wA ?',3)

    @pcs
    def update(self):
        #simulation initialisation
        if self.sunTime.isSimulBeginning:
            self.pcs_waterStatusInRootsLayer()

        #Reevalution of soil water components
        self.pcs_drainage()
        self.pcs_layersDepthUpdate()
        self.pcs_waterStatusInRootsLayer()


    #DRAINAGE
    Drainage = var('water loss by drainage by the soil (Kg_H2O /m2_soil /day)', 0.)#TODO : change time step evaluation to avoid init need

    @pcs
    def pcs_drainage(self,
        #TODO : change the name and comments  of parameters to indicate their meaning
        kDrainage_0 = param('coefficient kDr0 in groundwater drainage expression', 1.6),
        kDrainage_1 = param('coefficient kDr1 in groundwater drainage expression', 1.7),
        kDrainage_2 = param('coefficient kDr2 in groundwater drainage expression', 1), ):
        '''Process depth water table drainage  : empiric relationship with one of the state variables of soil water content'''

        if self.sunTime.isDayEnd :
            self.Drainage = kDrainage_0 * max(0, ((kDrainage_1 - self.Dp_C) / kDrainage_1)) ** kDrainage_2  #mdl empirique type Bray
            if self.Dp_C<0:
                self.Drainage *= 5.0


    #LAYERS LIMIT DEPTH
    w_A  = var('water content of layer A (Kg_H2O /m3_soil)', 100)
    Dp_B  = var('depth of the limit between layer B and A (m)', 0.25)
    Dp_C = var('depth of the limit between layer C and B (m)', 0.45)
    Ads = var('free water from draining adsorbed by layer A (Kg_H2O /m2_soil /day)', 0.)#TODO : change time step evaluation to avoid init need

    @pcs
    def pcs_layersDepthUpdate(self):
        '''Evaluate the layers limit depth (B,  C) and water content (A)'''

        #daily initialisation of integrative variables
        if self.sunTime.isDayBeginning :
            self._dailySum_ETR_DrySurface = 0
            self._dailySum_ETR_RootsAbsorption = 0
            self._dailySum_Draining = 0

        #Cumuls des echanges d#eau sol-environnement superieur
        self._dailySum_ETR_DrySurface += self.surface.ETR_DrySurface
        self._dailySum_ETR_RootsAbsorption  += self.treeStand.canopy.Transpiration + self.underStorey.canopy.Transpiration
        self._dailySum_Draining +=  self.surface.Draining

        if self.sunTime.isDayEnd :
            _w_POROSITY = self.w_SAT - self.w_FC

            if self.Dp_C > 0 : #water table was underground
                #adsorption  by layer A of infiltrated rain
                self.Ads = max(0,  min(
                          self._dailySum_Draining,
                          self.Dp_B*(self.w_FC - self.w_A)*((self.w_FC -self.w_A)/(self.w_FC - self.w_RES))**self.kAds_wA
                          ))

                if self.Ads >0 :
                    self.w_A += self.Ads/self.Dp_B
                    if self.w_A == self.w_FC:
                        self.Dp_B = self.Dp_Roots

                #ETR dry surface  is uptaked in  layer A
                if self.Dp_B==0:
                    self.w_A =  self.w_FC * 0.99
                    self.Dp_B = self._dailySum_ETR_DrySurface /(self.w_FC - self.w_A)
                else:
                    self.w_A -= self._dailySum_ETR_DrySurface /self.Dp_B

#                    #Plant transpiration
#                    _TR_C = min(self._dailySum_ETR_RootsAbsorption, max(0, (self.Dp_Roots-self.Dp_C))*_w_POROSITY)
#                    self.Dp_C +=  _TR_C / _w_POROSITY
#
#                    _TR_B = min(self._dailySum_ETR_RootsAbsorption -_TR_C, max(0, (min(self.Dp_C, self.Dp_Roots)-self.Dp_B))*(self.w_FC-self.w_A))
#                    self.Dp_B +=  _TR_B/(self.w_FC-self.w_A)
#
#                    _TR_A = self._dailySum_ETR_RootsAbsorption -_TR_C -_TR_B
#                    self.w_A -= _TR_A /self.Dp_B
#                    self.w_A = max(self.w_A,  self.w_RES) #BAD

                #Plant transpiration
                if self.Dp_C < self.Dp_Roots:
                    _TR_C = min(self._dailySum_ETR_RootsAbsorption, (self.Dp_Roots-self.Dp_C)*_w_POROSITY)
                    self.Dp_C +=  _TR_C / _w_POROSITY
                else:
                    _TR_C = 0

                if self.Dp_B < self.Dp_Roots:
                    _TR_B = min(self._dailySum_ETR_RootsAbsorption -_TR_C, ( self.Dp_Roots-self.Dp_B)*(self.w_FC-self.w_A))
                    self.Dp_B +=  _TR_B/(self.w_FC-self.w_A)
                else:
                    _TR_B = 0

                _TR_A = self._dailySum_ETR_RootsAbsorption -_TR_C -_TR_B
                self.w_A -= _TR_A /self.Dp_B
                self.w_A = max(self.w_A,  self.w_RES) #BAD



                #free water balance
                _dW_FW = self._dailySum_Draining - self.Ads - self.Drainage
                self.Dp_C -=  _dW_FW / _w_POROSITY

                if self.Dp_C < self.Dp_B : #the water table rises above AB limit
                    self.Dp_C = self.Dp_B - (self.Dp_B- self.Dp_C) *_w_POROSITY / (self.w_SAT - self.w_A)
                    self.Dp_B = self.Dp_C

                    if self.Dp_C<0:#the water rises above soil surface
                        self.Dp_C = 0 - (0- self.Dp_C) *(self.w_SAT - self.w_A)/1000 #Kg_H2O/m3  in air
                        self.Dp_B = self.Dp_C

                # depth of C and B layer is limited by soil depth
                self.Dp_C = min(self.Dp_C, self.Dp_Soil)
                self.Dp_B = min(self.Dp_B, self.Dp_Soil)

            else:#water table was above ground
                #adsorption  was nul
                self.Ads =0

                #evolution of layer boundary : all flux impact  C layer
                self.Dp_C += (self.Drainage - self._dailySum_Draining + self._dailySum_ETR_RootsAbsorption + self._dailySum_ETR_DrySurface )/1000 #Kg_H2O/m3  in air
                self.Dp_B = self.Dp_C

                if self.Dp_C>0:#the water drops under soil surface
                    self.Dp_C= self.Dp_C*1000/_w_POROSITY
                    self.Dp_B=0

                self.w_A = self.w_FC


    #WATER STATUS IN ROOTS LAYER
    MoistureDeficit = var('soil moisture deficit in the soil layer prospected by roots  [0-1] (Kg_H2O /Kg_H2O)', 0.)
    RootLayerWaterPotential = var('water potentiel in the soil layer prospected by roots (MPa)', 0.)

    @pcs
    def pcs_waterStatusInRootsLayer(self,
        k_VG_alpha = param('alpha parameter of van Genuchten expression of soil water potential (MPa-1)',7.0),
        k_VG_m = param('m parameter of van Genuchten expression of soil water potential', 0.57),
        ):

        if self.sunTime.isDayEnd :
            #water content in the soil layer prospected by roots (Kg_H2O /m3_soil)
            _w_RootLayer = (self.w_A * self.Dp_B + max(0, (min(self.Dp_Roots, self.Dp_C) - self.Dp_B) * self.w_FC) + max(0, (self.Dp_Roots - self.Dp_C) * self.w_SAT)) / self.Dp_Roots

            #soil moisture deficit
            if self.Dp_Roots > self.Dp_B :
                self.MoistureDeficit = 0
                self.RootLayerWaterPotential=0
            else :
                self.MoistureDeficit = max(0, min((self.w_FC - _w_RootLayer ) / (self.w_FC - self.w_WP), 1))
                #root layer water potential : Van Genuchten relationship
                self.RootLayerWaterPotential = (-1/k_VG_alpha)*max(0, (max(0.0001, _w_RootLayer - self.w_RES)/(self.w_SAT-self.w_RES))**(-1/k_VG_m)-1)**(1-k_VG_m)

