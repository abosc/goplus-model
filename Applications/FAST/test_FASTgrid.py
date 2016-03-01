#Grid of simulateGrid 
#with the recording  at YearEnd of the mean of all variables 
import GOplus.FAST 

#Grid parameters range for the exercice and filepath
# fine parameterisation is trust to theMDL.FASt function : simul_parameters
genericMeteoFilePath = '/mnt/ARCHIVES/FAST_test/meteo/meteo_%s.csv'
genericFileOutPath = '/mnt/ARCHIVES/FAST_test/simul/%s.csv'
fileoutName = genericFileOutPath % 'test_FASTgrid' 
rg_Soils =(0, 1, 2)
rg_Practices = (0, 1)
rg_StandAge =(0, 1, 2)
rg_Points=(
                (350, 49.9448),              
                (558, 49.6556), 
                (1071, 49.1828), 
                (2417, 48.3199), 
                (2445, 48.2771), 
                (3031, 47.9086), 
                (5591, 46.3671), 
                (5728, 46.2638), 
                (6150, 45.9447), 
                (7095, 45.0514), 
                (7482, 44.7355), 
                (8764, 43.7098), 
                (9245, 43.2711), 
            )


# imbricated loop of simulations  over grid parameters 
def simulateGrid(rg_Soils = rg_Soils, rg_Practices = rg_Practices, rg_StandAge = rg_StandAge,  rg_Points = rg_Points, fileoutName = fileoutName, outFrequency=2):
    ''' 
    A  test on grid of model parameters
    '''
    Errors_log =[]
  
    fileOutAppend = False
    
    for iSoil in rg_Soils:
        for iPractice in rg_Practices:
            for iStandAge in rg_StandAge:
                for aPoint in rg_Points:

                    simName ='Soil%sSylv%sAge%sPt%s' % (iSoil,  iPractice,  iStandAge,  aPoint[0])
                    print('--> do simulation : %s' %simName)
                    
                    try:
                        GOplus.FAST .simulate(
                                                    startYear=1970, 
                                                    endYear = 2099, 
                                                    latitude =aPoint[1], 
                                                    meteoFile = genericMeteoFilePath % aPoint[0],    
                                                    iPractice = iPractice, 
                                                    iStandAge = iStandAge, 
                                                    iSoilType = iSoil, 
                                                    fileoutName = fileoutName, 
                                                    outFrequency=outFrequency, 
                                                    log = False, 
                                                    simulName = simName, 
                                                    fileOutAppend=fileOutAppend, 
                                                    )
                                                

                    except:
                        Errors_log+=['! Error during simulation %s' %simName]
                    
                    fileOutAppend = True
    
    return Errors_log

############################
if __name__ == '__main__':
    pass
    
    # simulations loop on the grid
    #print(simulateGrid())

