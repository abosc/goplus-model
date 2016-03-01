from ..goBases import *

class SunLocal(ELT):
    ''' Represent the  sun cycle for a localisation.
    '''
    
    #outer element
    locTime = eltOut('LocTime element')

    #vars
    SinSunElevation = var('sinus of the solar elevation angle')
    SinSunElevationMidday = var('sinus of the solar elevation angle at midday')
    SinSunAzimuth = var('sinus of sun azimuth')

    SunUp = var('sun up day fraction')
    SunDown = var('sun down day fraction')
    DayTime = var('duration of day (solar above horizon)')
    
    #params
    Latitude = param('latitude of the site (deg)', 44.7)
    
    def update(self):
        
        earthInclination =  -0.408407045                        #constant earth inclination (radian)
        sin_Latitude = sin(self.Latitude *pi/180.0)          # sinus of the latitude 
        cos_Latitude = cos(self.Latitude *pi/180.0)        #cosinus of the latitude
       
        sunDeclination = earthInclination * cos(2 * pi * (self.locTime.DOY + self.locTime.H/24.0 + 10) / self.locTime.NbDayOfYear)
        sin_Declination  = sin(sunDeclination)
        cos_Declination = cos(sunDeclination)
        
        FD = pi * (self.locTime.H/12.0 - 1)
        
        self.SinSunElevation = sin_Latitude * sin_Declination + cos_Latitude * cos_Declination * cos(FD)
        self.SinSunAzimuth = cos_Declination * sin(FD) / sin_Latitude #2012-10-16 attention indique faux dans le code VB --> a verifier
        
        #day properties updates  et the beginning of the day
        if self.locTime .isDayBeginning:
            self.SinSunElevationMidday = sin_Latitude * sin_Declination + cos_Latitude* cos_Declination
            
            #Sun up
            _CS = -(sin_Latitude * sin_Declination) / (cos_Latitude *cos_Declination)
            
            try:
                _AT = atan((1 / _CS ** 2 - 1) ** 0.5)
            except:
                raise Exception('Solar elevation incorrect for this day')
            
            if _CS < 0 : _AT = pi - _AT
            self.SunUp = (2 * pi - _AT) * 0.5 / pi - 0.5
            
            #Sun down
            self.SunDown = 1 - self.SunUp
            
            #Day duration
            self.DayTime = 1 - 2 * self.SunUp



