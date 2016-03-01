# -*- coding: utf-8 -*-

from ..goBases import *

class SunTime(ELT):
    ''' SunTime represent the solar time in the model 
    '''

    #vars
    Y = var('year')
    DOY =  var('Day Of Year')
    H = var('hour')
    time = var('number of time steps since the beginning of simulation (hour)')
    NbDayOfYear = var('number of days in current year')
    
    isSimulBeginning =var('True if it is the first instant in simulation', 2)
    isDayBeginning =var('True if it is the first instant in day')
    isYearBeginning =var('True if it is the first instant in year')
    isDayEnd =var('True if it is the last instant in day')
    isYearEnd =var('True if it is the last instant in year')

    SinSunElevation = var('sinus of the solar elevation angle')

    #params
    Y_start = param('initial year',  1980)
    allowBissextileYear = param('0: if only 365 days/year, 1: if allow bissextile year', 1)
    Latitude = param('latitude of the site (deg)', 44.7)
    
    def update(self):
        '''update the time states (1 hour base time) and sun position
        '''
        #simulation beginning initialisations
        if self.isSimulBeginning :
            self.isSimulBeginning -=1
            
        if self.isSimulBeginning :            
            self.Y = self.Y_start-1
            self.NbDayOfYear = 365 + (self.allowBissextileYear and (self.Y % 4) == 0)
            self.time = -1
            self.DOY = self.NbDayOfYear     
            
            self._sin_Latitude = sin(self.Latitude *pi/180.0)   #sinus of the latitude 
            self._cos_Latitude = cos(self.Latitude *pi/180.0)   #cosinus of the latitude            


        #time states progression
        self.isDayBeginning = self.isYearBeginning =  self.isDayEnd =  self.isYearEnd = False
        
        self.time += 1 
        self.H =  self.time % 24
        if self.H == 0:
            self.isDayBeginning = True
            self.DOY = (self.DOY % self.NbDayOfYear) +1
            
            if self.DOY == 1:
                self.isYearBeginning=True
                self.Y += 1
                self.NbDayOfYear = 365 + (self.allowBissextileYear and (self.Y % 4) == 0)
        
        if self.H == 23:
            self.isDayEnd = True
            if self.DOY == self.NbDayOfYear:
                self.isYearEnd = True

        #sun position   (EARTH_INCLINATION = -0.408407045 radian)   
        sunDeclination = -0.408407045 * cos(2 * pi * (self.DOY + self.H/24.0 + 10) / self.NbDayOfYear)
        hourAngle = pi * (self.H/12.0 - 1)
        
        self.SinSunElevation = self._sin_Latitude * sin(sunDeclination) + self._cos_Latitude * cos(sunDeclination) * cos(hourAngle)








