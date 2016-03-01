## Model parameterized and initialized for FAST exercic
## Authors: A. Bosc and D. Loustau
## Version: FAST-AGU . 
## Updated: 2013-11-22

from Model.mdlModel import Model
from GOtools.Integrater import Integrater

from FAST_IntegraterVars import variablesValues, variablesNames
from FAST_Manager import Manager
import math

def model(
    startYear,     #initial year
    latitude,       #latitude of the point : float
    meteoFile,    #meteo file path : str
    iPractice,      #index of the silvicultural practice (0: standard, 1:semi dedie, 2:dedie)
    iStandAge,   #index of the age class of the stand : (0,1 or 2)
    iSoilType,      #index of the soil type : (0,1 or 2)
    ):
    '''return an instance of the Model parameterized and initialized for FAST exercice .
    '''

   #instanciate the model
    mdl= Model()

   #Temporal FAST parameters
    mdl.locTime.Y_start = startYear
    mdl.locTime.allowBissextileYear = 0 #Arpege climat meteo file don't have bissextile year

   #Localisation parameters
    mdl.sunLocal.Latitude = latitude
    mdl.climate.meteo_file_path = meteoFile

    #Silvicultural practices and initial age class parameters
    mdl.manager = Manager()
    mdl.manager.practicesType = iPractice
    if iPractice == 0:
        _initial_trees_Age = (5, 26, 47)[iStandAge]
        _initial_trees_Density = (1600, 575, 250)[iStandAge]
    elif iPractice == 1:
        _initial_trees_Age = (5, 21, 37)[iStandAge]
        _initial_trees_Density = (1600, 830, 300)[iStandAge]
    elif iPractice == 2:
        _initial_trees_Age = (5, 16, 27)[iStandAge]
        _initial_trees_Density = (1600, 800, 800)[iStandAge]
    
   #define the initial stand structure from stand age  using allometric relationship based on
   #pinus pinaster root-shoot ratio obtain on dataset furnished by Trichet P (parcelle L12ans &18ans, Bilos 50ans, parcelle M 63 ans)
#    _trees_Wa_avg = 0.2146*_initial_trees_Age**2.0481
    _trees_Wa_avg =math.exp( -0.336354*math.log(_initial_trees_Age)**2 + 3.742828*math.log(_initial_trees_Age) - 3.108378)
    _trees_WrOnWa_avg =0.085365*_trees_Wa_avg**0.176316

    mdl.forest.treeStand.initialTreesAge = _initial_trees_Age
    mdl.forest.treeStand.initialTreesDensity = _initial_trees_Density
    mdl.forest.treeStand.initialTreesWa_avg = _trees_Wa_avg
    mdl.forest.treeStand.initialTreesWa_std = _trees_Wa_avg*0.4
    mdl.forest.treeStand.initialTreesWrOnWa_avg = _trees_WrOnWa_avg
    mdl.forest.treeStand.initialTreesWrOnWa_std = _trees_WrOnWa_avg*0.1
    
    #TreeStand LUE ponderation linked to practices <-- fertilisation and genetic selection effects
    mdl.forest.treeStand.kLUE_N = (1.1, 1.2, 1.4)[iPractice]

    #Soil  hydraulics  parameters for soil without groundwater type
    mdl.forest.soil.Dp_Soil = (0.50, 0.80, 1.10)[iSoilType] 
    mdl.forest.soil.Dp_Roots =  mdl.forest.soil.Dp_Soil #Soil is completely explored by roots
    mdl.forest.soil.Dp_C = mdl.forest.soil.Dp_B = mdl.forest.soil.Dp_Soil
    mdl.forest.soil.kDrainage_0 = 1000 #very high drainage coefficient to avoid soil with groundwater
    mdl.forest.soil.kAds_wA  = 50 #high soil adsorption coeeficient. only very big rain episod  drain directly to waterground
    
    #Soil water content parameters ( Kg_H2O.m-2_area .m-1_depth = Kg_H2O /m3_soil). Independant of soil type
    mdl.forest.soil.k_wSAT =  350
    mdl.forest.soil.k_wFC =  205
    mdl.forest.soil.k_wWP =  80
    mdl.forest.soil.k_wRES =  70

    #Soil RothC-plow parameters linked to soil type
    mdl.forest.soil.HUM =  (4804.0, 7686.0, 10569.0)[iSoilType]
    mdl.forest.soil.RPM =  (321.0, 514.0, 707.0)[iSoilType]
    mdl.forest.soil.DPM =  (230.0, 367.0, 505.0)[iSoilType]
    mdl.forest.soil.BIO =  (367.0, 588.0, 808.0)[iSoilType]
    mdl.forest.soil.IOM =  (1157.0, 1851.0, 2546.0)[iSoilType]

    mdl.forest.soil.k_HUM = 0.02
    mdl.forest.soil.k_DPM = 10
    mdl.forest.soil.k_PlowEffect = 3

   #Return the model 
    return mdl


def simulate(
    startYear,      #initial year
    endYear,        # final simulation year
    latitude,       #latitude of the point : float
    meteoFile,    #meteo file path : str
    iPractice,      #index of the silvicultural practice (0: LowIntensity, 1:MediumIntensity, 2:HighIntensity)
    iStandAge,   #index of the age class of the stand : (0,1 or 2)
    iSoilType,      #index of the soil type : (0,1 or 2)
    fileoutName,  #name of the file to write the integrated model variables
    outFrequency,  #0 for end hour, 1 for end day, 2 for end year
    log,                #boolean to indicate if simulation information are print
    simulName ='GO simulation', 
    header= True, 
    fileOutAppend = True, 
    
    ):
    '''conduct a simulation for one set of FAST exercice parameters '
    '''

    #obtain an instance of model with specific parameterisation for the exercice
    mdl = model(
                                startYear = startYear,
                                latitude =latitude,
                                meteoFile = meteoFile,
                                iPractice = iPractice,
                                iStandAge = iStandAge,
                                iSoilType = iSoilType
                                )

    locTime = mdl.locTime #short reference to locTime object to accelerate conditionnal tests
    integrater =Integrater()

    #open the fileOut and write header
    fileOut = open(fileoutName, 'a' if fileOutAppend else 'w')
    if header==True and not fileOutAppend:
        _header = variablesNames.replace('\n', '')
        _header = _header.replace(', mdl.', ':')
        _header = _header.replace(' ', '')
        _header = _header.replace('\t', '')
        fileOut.write('%s,%s\n' % (simulName, _header))

    #simulation loop
#    try:
    while locTime.Y< endYear+1 :

        #update the model state
        mdl.update()

        #made  the integrations of model variables and output the integrated values each year
        integrater.integrate(variablesValues(mdl))

        if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
            fileOut.write('%s,%s\n' % (simulName, integrater.putStr()))

        #some informations to follow simulation
        if log and locTime.isYearBeginning:
            print (str(locTime.Y), ', nb trees: ',  str(mdl.forest.treeStand.treesCount), ', LAI:',  str(mdl.forest.treeStand.LAI), ', HEIGHTmean:',  str(mdl.forest.treeStand.HEIGHTmean), ', Wa:',  str(mdl.forest.treeStand.Wa))

#    except:
#        pass

    #close the output file
    fileOut.close()



##########################################
##invocation of the main function to help Shedskin to  identified type
if False:

    simulate(
                    startYear = 1970.0,
                    endYear = 2100.0,
                    latitude =44.9,
                    meteoFile = '/mnt/ARCHIVES/FAST_test/meteo/meteo_350.csv',
                    iPractice = 0,
                    iStandAge = 0,
                    iSoilType = 0,
                    fileoutName = 'test.csv',
                    outFrequency = 2,
                    log = True,
                    )
