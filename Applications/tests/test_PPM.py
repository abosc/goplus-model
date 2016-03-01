from GOplus.Model.mdlSunTime import SunTime
from GOplus.Model.mdlClimate import Climate
from GOplus.Model.mdlPPM import Infestation


def test():
    #create the model elements
    sunTime=SunTime()
    climate=Climate()    
    infestation = Infestation()    
    
    #connect the model elements
    sunTime.sunTime=sunTime
    climate.sunTime = sunTime
    infestation.sunTime =sunTime
    infestation.microclim= climate.microclim    
    
    #specific parameters
    climate.meteo_file_path = 'meteo_7334.csv'
    sunTime.Y_start = 1970
    sunTime.allowBissextileYear = 0 #Arpege climat meteo file don't have bissextile year     
    
    #elements initialisation
    sunTime.initialisation()
    climate.initialisation()
    infestation.initialisation()
    
    #simulate
    while sunTime.Y<1972:
        if sunTime.isDayBeginning:
            if sunTime.Y ==1970 and sunTime.DOY==240:
                infestation.isEmerged=True
        
        #update elemnts
        sunTime.update()
        climate.update()
        infestation.update()
        
        if sunTime.isDayEnd:
            print('%s,  %s'%(infestation.caterpillar.W, infestation.dailyDefoliation))
            


if __name__ == '__main__':
    test()
    
