from ..goBases import *

from .mdlMicroClimate import MicroClimate


def CO2_mdl(YearFrac = 1990.5):
    '''model of CO2 evolution as a function with an alone time parameter (year and fraction as float)'''
    return 0.0000000297892*(YearFrac-2000)**4 + 0.0000786964*(YearFrac-2000)**3 + 0.0202866*(YearFrac-2000)**2 + 1.99387*(YearFrac-2000) + 369.645


def RsDifFrac_mdl(sinB =0.5,DOY=100.0,  Rs=1000.0):
    '''Evaluate the diffuse part of solar radiation
        - sinB in sinus of solar elevation
        - DOY: the day of the year 
        - Rs : the solar radiation (W /m2_soil)
    '''
    
    #RAYONNEMENT INCIDENT AU SOL S0 (W.m-2)
    SCS=1370.0 #W.m-2 (solar constant at the to of the atmosphere
    S0=SCS*(1+0.033*cos(360*DOY/365.0*pi/180.0))*sinB

    #atmosphere transmissivity
    ATMTRANS=Rs/S0

    #RATIO DIFFUS/GLOBAL  
    if ATMTRANS<=0.22:
        return 1
    elif ATMTRANS<=0.35:
        return 1-6.4*((ATMTRANS-0.22)**2)
    
    RR=0.847-1.61*sinB+1.04*(sinB**2)
    KK=(1.47-RR)/1.66
    
    if ATMTRANS<KK:
        return 1.47-1.66*ATMTRANS
    else:
        return RR


class Climate(ELT):

    #outer elements
    locTime = eltOut('LocTime element')
    sunLocal = eltOut('SunLocal element')
    
    #inner element
    microclim = eltIn(MicroClimate)
    
    #meteo file path
    meteo_file_path = param('complete path-name to meteo file', 'defaultMeteoData.csv' ), 
    
    def update(self):
        self.pcs_climateConditionsFromDataFile()
    
    @pcs
    def pcs_climateConditionsFromDataFile(self, 
        _ = private('use to store file object of meteorological data', ELT), 
        ):
    
        #initialize private vars
        if self.locTime.isSimulBeginning:
            _.meteo_file = open(self.meteo_file_path, 'r')

        try :
            #read a record string and ignore  those commented,reload file if end of file reached
            _strRecord = "#"      
            while _strRecord=='' or _strRecord.strip()[0]=='#':
                _strRecord=_.meteo_file.readline()
                if _strRecord=='': 
                    _.meteo_file=open(self.meteo_file_path, 'r')
            
            #split record on a numerique data list
            _data =  _strRecord.strip().split(',')
        
            _microclim = self.microclim
            
            #if pressure is not present use default value
            if  _data[3].strip()!='':
                _microclim.P = float(_data[3])
            else:
                 _microclim.P = 101600
            
            _microclim.TaC =float( _data[4])
            _microclim.e = float(_data[5])
            _microclim.Rain = float(_data[6])
            _microclim.u = float(_data[7])
            
            #RsDir and RsDif from Rs and RsDifFrac if present, else use model partitition
            if  _data[9].strip()!='':
                _RsDifFrac = float(_data[9])
            else:
                if _microclim.Rain >0 :
                    _RsDifFrac = 1
                else:
                    _RsDifFrac = RsDifFrac_mdl(self.sunLocal.SinSunElevation, self.locTime.DOY,  float(_data[8]))
            
            _microclim.RsDir = float(_data[8])*(1-_RsDifFrac)
            _microclim.RsDif = float(_data[8])*_RsDifFrac
            
            _microclim.RthDw = float(_data[10])
            
            #CO2 from file or model
            _microclim.CO2 = CO2_mdl(self.locTime.Y+self.locTime.DOY/365.0)
            
        except :
            print('Error during conversion of climatic data file,  on position %i' % _.meteo_file.tell())
            raise
                        
        self.microclim.update()


