#Test
import GOplus.FAST 


############################
if __name__ == '__main__':
    
    GOplus.FAST.simulate(
                                startYear=1970, 
                                endYear = 1990, 
                                latitude =44.9, 
                                meteoFile = 'meteo_7334.csv',    
                                iPractice = 1, 
                                iStandAge = 1, 
                                iSoilType = 1, 
                                fileoutName = 'test_FAST.csv', 
                                outFrequency=1, 
                                log = True, 
                                fileOutAppend=False
                                )
