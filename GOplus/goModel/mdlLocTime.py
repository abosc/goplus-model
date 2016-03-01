from ..goBases import *

class LocTime(ELT):
    ''' LocTime represent the time in the model 
    '''

    Y = var('year')
    DOY =  var('Day Of Year')
    H = var('hour')
    Now = var('number of days since the beginning of simulation')
    NbDayOfYear = var('number of days in current year')
    
    isSimulBeginning =var('True if it is the first instant in simulation', 2)
    isDayBeginning =var('True if it is the first instant in day')
    isYearBeginning =var('True if it is the first instant in year')
    isDayEnd =var('True if it is the last instant in day')
    isYearEnd =var('True if it is the last instant in year')

    #params
    Y_start = param('initial year',  1980)
    allowBissextileYear = param('0: if only 365 days/year, 1: if allow bissextile year', 1)

    def update(self):
        '''update the time states
        '''
        #simulation beginning state modification
        if self.isSimulBeginning: 
            self.isSimulBeginning -= 1
        
        #initialisations
        if self.isSimulBeginning: 
            self.Y = self.Y_start-1
            self.NbDayOfYear = 365 + (self.allowBissextileYear and (self.Y % 4) == 0)
            self.Now=0
            self.DOY =self.NbDayOfYear     
            self.H = 23 

        #time states progression
        self.isDayBeginning = self.isYearBeginning =  self.isDayEnd =  self.isYearEnd = False
        
        self.H =  (self.H + 1) % 24
        if self.H == 0:
            self.isDayBeginning = True
            self.Now +=1
            self.DOY = (self.DOY % self.NbDayOfYear) +1
            
            if self.DOY == 1:
                self.isYearBeginning=True
                self.Y += 1
                self.NbDayOfYear = 365 + (self.allowBissextileYear and (self.Y % 4) == 0)
        
        if self.H == 23:
            self.isDayEnd = True
            if self.DOY == self.NbDayOfYear:
                self.isYearEnd=True


