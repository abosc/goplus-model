from GOplus.Model.mdlSunLocal import SunLocal
from GOplus.Model.mdlLocTime import LocTime
from GOplus.Model.mdlClimate import Climate
from GOplus.Model.mdlPPM import Infestation


def test():
    #create the model elements
    locTime=LocTime()
    sunLocal=SunLocal()
    climate=Climate()    
    infestation = Infestation()    
    
    #connect the model elements
    sunLocal.locTime=locTime
    climate.locTime = locTime
    climate.sunLocal= sunLocal
    infestation.locTime =locTime
    infestation.sunLocal=sunLocal
    infestation.microclim= climate.microclim    
    
    #specific parameters
    climate.meteo_file_path = 'meteo_7334.csv'
    locTime.Y_start = 1970
    locTime.allowBissextileYear = 0 #Arpege climat meteo file don't have bissextile year     
    
    #elements initialisation
    locTime.initialisation()
    sunLocal.initialisation()
    climate.initialisation()
    infestation.initialisation()
    
    #simulate
    while locTime.Y<1972:
        if locTime.isDayBeginning:
            if locTime.Y ==1970 and locTime.DOY==240:
                infestation.isEmerged=True
        
        #update elemnts
        locTime.update()
        sunLocal.update()
        climate.update()
        infestation.update()
        
        if locTime.isDayEnd:
            print('%s,  %s'%(infestation.caterpillar.W, infestation.dailyDefoliation))
            


if __name__ == '__main__':
    test()
    
