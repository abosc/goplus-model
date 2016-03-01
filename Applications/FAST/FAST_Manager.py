## MANAGER PRACTICES defined for FAST project simulations
## Authors: A. Bosc and D. Loustau
## Version: FAST-AGU . 
## Updated: 2013-11-22
from ..goBases import *


import LANDAIS_Manager


class Manager(LANDAIS_Manager.Manager):

    @params(
    practicesType = num('practices type id (a number)', 0), 
    )
    def update(self):
        if self.practicesType == 0 : self.do_LowIntensityPractices()
        if self.practicesType == 1 : self.do_MediumIntensityPractices()
        if self.practicesType == 2 : self.do_HighIntensityPractices()

    def do_LowIntensityPractices(self):
        # PRACTICES : SEQUENCE OF THE INTERVENTIONS #
        _rotationYear=self.rotationYear()
        if _rotationYear==3:
            self.do_plow(areaFractionPlowed = 0.25,soilCarbonFractionAffected = 0.5,soilPerennialFractionAffected =0.95)
            self.do_install_stand( 2, 1600)

        if _rotationYear == 15 : self.do_standard_thinning(830)
        if _rotationYear == 25 : self.do_standard_thinning( 575)
        if _rotationYear == 35 : self.do_standard_thinning( 375)
        if _rotationYear == 45 : self.do_standard_thinning( 250)
        if _rotationYear == 60 : self.do_standard_thinning( 0)


    def do_MediumIntensityPractices(self):
        # PRACTICES : SEQUENCE OF THE INTERVENTIONS #
        _rotationYear=self.rotationYear()
        if _rotationYear ==3 :
            self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5,soilPerennialFractionAffected =0.95)
            self.do_install_stand( 2, 1600)

        if _rotationYear == 15 : self.do_standard_thinning( 830)
        if _rotationYear == 25 : self.do_standard_thinning( 575)
        if _rotationYear == 35 : self.do_aerial_biomass_thinning( 300)
        if _rotationYear == 45 : self.do_aerial_biomass_thinning( 0)


    def do_HighIntensityPractices(self):
        # PRACTICES : SEQUENCE OF THE INTERVENTIONS #
        _rotationYear=self.rotationYear()
        if _rotationYear ==3 :
            self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.75,soilPerennialFractionAffected =0.95)
            self.do_install_stand( 2, 1600)

        if _rotationYear == 15 : self.do_aerial_biomass_thinning( 800)
        if _rotationYear == 30 : self.do_all_biomass_thinning( 0)

