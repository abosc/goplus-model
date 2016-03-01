## Simulation Experiment defined for FOREVER project 
## Authors: A. Bosc and D. Loustau
## Version: 1.0
## Updated: 2014-07-15

#Add the path of GOplus to the path search
import os,sys
basePath  = os.path.dirname(os.path.realpath(__file__))+"/../.." 
#basePath  = os.getcwd().rsplit('/Applications',1)[0]
sys.path.append(basePath) 

#Importation of GOplus elements
from GOplus.goBases import *
from GOplus.Model.mdlModel import Model
from GOplus.Model.ManagerElements import LANDAIS_Manager

from GOplus.goTools.VarsIntegrater import Integrater
#from test_FOREVER_VarsIntegrater import Integrater

from FOREVER_varsToIntegrate import varsToIntegrate
#from GOplus.Model_integrableVars import integrableVars as varsToIntegrate

class Manager(LANDAIS_Manager.Manager):

    practicesType = param('practices type id (a number)', 0), 
    
    def do_managment(self):
        if self.practicesType == 0 : self.do_StandardManagement()
        if self.practicesType == 1 : self.do_IntensiveManagement()

    def do_StandardManagement(self):
        # PRACTICES : SEQUENCE OF THE INTERVENTIONS #
        _rotationYear=self.rotationYear()
        if _rotationYear == 2 :
            #install a new stand after 2 years of nude soil.
            self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5,soilPerennialFractionAffected =0.95)
            self.do_install_stand( 2, 1250)

        #cut 25% of initial trees at each thinning
        if _rotationYear == 15 : self.do_standard_thinning( 1250*0.65)
        if _rotationYear == 25 : self.do_standard_thinning(  1250*0.65*0.65)
        if _rotationYear == 35 : self.do_standard_thinning(  1250*0.65*0.65*0.65)
        if _rotationYear == 45 : self.do_standard_thinning( 0)


    def do_IntensiveManagement(self):
        # PRACTICES : SEQUENCE OF THE INTERVENTIONS #
        _rotationYear=self.rotationYear()
        if _rotationYear == 2 :
            #install a new stand after 2 years of nude soil.
            self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.75,soilPerennialFractionAffected =0.95)
            self.do_install_stand( 2, 2500)

        if _rotationYear == 15 : self.do_aerial_biomass_thinning( 1250)
        if _rotationYear == 30 : self.do_intensive_biomass_thinning( 0)


def model(
    startYear,     #initial year
    latitude,       #latitude of the point : float
    meteoFile,    #meteo file path : str
    iPractice,      #index of the silvicultural practice (0: standard, 1:intensif)
    iStandAge,   #index of the age class of the stand : (0...8 dor practice 0, 0...5 for practice 1)
    iSoilType,      #index of the soil type : (0,1 or 2)
    ):
    '''Return an instance of the Model parameterized and initialized for FOREVER experiment
    '''
    
   #instanciate the model, set a specific manager and define start year
    mdl= Model()

   #Temporal parameters
    mdl.locTime.Y_start = startYear
    mdl.locTime.allowBissextileYear = 0 #Arpege climat meteo file don't have bissextile year

   #Localisation parameters
    mdl.sunLocal.Latitude = latitude
    mdl.climate.meteo_file_path = meteoFile
    
    #Silvicultural practices and initial age class parameters
    mdl.manager = Manager()
    mdl.manager.practicesType = iPractice
    
    
    
    if iPractice == 0:
        _initial_trees_Age = (2, 7, 12, 17, 22, 27, 32, 37, 42)[iStandAge]
        _initial_trees_Density =1250
        if _initial_trees_Age >=15 : _initial_trees_Density *= 0.65
        if _initial_trees_Age >=25 : _initial_trees_Density *= 0.65
        if _initial_trees_Age >=35 : _initial_trees_Density *= 0.65
    if iPractice == 1:
        _initial_trees_Age = (2, 7, 12, 17, 22, 27)[iStandAge]
        _initial_trees_Density =2500
        if _initial_trees_Age >=15 : _initial_trees_Density *= 0.5


   #define the initial stand structure from stand age  using allometric relationship based on
   #pinus pinaster root-shoot ratio obtain on dataset furnished by Trichet P (parcelle L12ans &18ans, Bilos 50ans, parcelle M 63 ans)  
#    _trees_Wa_avg = math.exp( -0.336354*math.log(_initial_trees_Age)**2 + 3.742828*math.log(_initial_trees_Age) - 3.108378) #version FAST
    _trees_Wa_avg = WaEquilLAI(2.75, _initial_trees_Density, _initial_trees_Age)
    _trees_WrOnWa_avg = 0.085365*_trees_Wa_avg**0.176316
    
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    _installation.initialTreesAge = _initial_trees_Age
    _installation.initialTreesDensity = _initial_trees_Density
    _installation.initialTreesWa_avg = _trees_Wa_avg
    _installation.initialTreesWa_std = _trees_Wa_avg * 0.4
    _installation.initialTreesWrOnWa_avg = _trees_WrOnWa_avg
    _installation.initialTreesWrOnWa_std =  _trees_WrOnWa_avg*0.1

    #TreeStand parametrisation to mimic genetic selection effects :
    # modification of  allocationo rate to root
    mdl.forest.treeStand.pcs_CarbonFluxesPartition.kIstress_1 *= (1, 0.65)[iPractice]
    
    #Physical soil water properties independant of soil type( Kg_H2O.m-2_area .m-1_depth = Kg_H2O /m3_soil).
    mdl.forest.soil.waterCycle.w_SAT =  350
    mdl.forest.soil.waterCycle.w_FC =  205
    mdl.forest.soil.waterCycle.w_WP =  80
    mdl.forest.soil.waterCycle.w_RES =  70
    mdl.forest.soil.waterCycle.Dp_Soil = (0.2, 0.6, 1.0)[iSoilType] #correspond to RU = (25,75,125)
    mdl.forest.soil.waterCycle.Dp_Roots =  mdl.forest.soil.waterCycle.Dp_Soil #Soil is completely explored by tree roots
    
    #Soil  hydraulics  parameters for soil without groundwater type
    mdl.forest.soil.waterCycle.pcs_drainage.kDrainage_0 = 1000 #very high drainage coefficient to avoid soil with groundwater
    mdl.forest.soil.waterCycle.kAds_wA  = 0.1 #]0 for high soil adsorption . only very big rain episod  drain directly to waterground
    
    #Initial soil water content : soil at field capacity
    mdl.forest.soil.waterCycle.Dp_C = mdl.forest.soil.waterCycle.Dp_B = mdl.forest.soil.waterCycle.Dp_Soil
    mdl.forest.soil.waterCycle.w_A = mdl.forest.soil.waterCycle.w_FC

    #Soil RothC-plow parameters linked to soil type
    mdl.forest.soil.carbonCycle.HUM =  (4804.0, 7686.0, 10569.0)[iSoilType]
    mdl.forest.soil.carbonCycle.RPM =  (321.0, 514.0, 707.0)[iSoilType] *5.  #*5. is to be near equilibrium at start
    mdl.forest.soil.carbonCycle.DPM =  (230.0, 367.0, 505.0)[iSoilType]
    mdl.forest.soil.carbonCycle.BIO =  (367.0, 588.0, 808.0)[iSoilType]/3. #/3. is to be near equilibrium at start
    mdl.forest.soil.carbonCycle.IOM =  (1157.0, 1851.0, 2546.0)[iSoilType]

    mdl.forest.soil.carbonCycle.pcs_decomposition_RothC.k_HUM = 0.02
    mdl.forest.soil.carbonCycle.pcs_decomposition_RothC.k_DPM = 10
    mdl.forest.soil.carbonCycle.pcs_decomposition_RothC.k_PlowEffect = 3
    
   #return the model 
    return mdl


def WaEquilLAI(LAI, density,Age):
    SLAI = 6.5/2.57 #m2_LAI /Kg_DM
    k_Wn1_1 =  0.8212
    k_Wn1_2 = 0.796
    k_Wn1_3 =  -0.602
    k_Ys = 2.5
    return  (LAI/(k_Ys*k_Wn1_1*(Age**k_Wn1_3)*SLAI*density*1e-4))**(1/k_Wn1_2)
    

def simulate(
    mdl,  #model instance
    endYear,        # final simulation year    
    fileoutName,  #name of the file to write the integrated model variables
    outFrequency,  #0 for end hour, 1 for end day, 2 for end year
    log,                #boolean to indicate if simulation information are print
    header= True, 
    fileOutAppend = False, 
    ):
    '''conduct a simulation for one set of FOREVER exercice parameters '
    '''

    #Define the integrater
    integrater =Integrater(mdl, varsToIntegrate)

    #open the fileOut and write header
    with open(fileoutName, 'a' if fileOutAppend else 'w') as fileOut:
        if header==True and not fileOutAppend:
            fileOut.write('%s\n' % integrater.varNames)

        #short reference to locTime object to accelerate conditionnal tests
        locTime = mdl.locTime 

        #simulation loop
        while locTime.Y< endYear+1 :

            #update the model state
            mdl.update()

            #made  the integrations of model variables and output the integrated values each year
            integrater.integrate()

            if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())

            #some informations to follow simulation
            if log and locTime.isYearEnd:#Beginning:
                print (str(locTime.Y), ', nb trees: ',  str(mdl.forest.treeStand.treesCount), ', LAI:',  str(mdl.forest.treeStand.canopy.LAI), ', HEIGHTmean:',  str(mdl.forest.treeStand.HEIGHTmean), ', DBHmean:',  str(mdl.forest.treeStand.DBHmean), ', Wa:',  str(mdl.forest.treeStand.Wa), 'Rot. Y', str(mdl.manager.rotationYear()))


#example of use
if __name__ == '__main__':
    from time import  localtime, time
    
    #obtain an instance of model with specific parameterisation for the exercice
    mdl = model(
                        startYear = 1987.,
                        latitude =44.7,
                        meteoFile = basePath +'/RESSOURCES/meteo_9455.csv',
                        iPractice = 0,
                        iStandAge = 1,
                        iSoilType = 0
                        )

    #Ask for endYear parameter
    try:
        _endYear = int(input('Please enter the last year of simulation (or 0 to avoid simulation) : ') )
    except : #input  on pypy and eric5 bug
        _endYear = 2050
        
    
    #Do simulation
    if _endYear>0:
        tstart =time()
        
        simulate(
            mdl = mdl, 
            endYear = _endYear, 
            fileoutName = basePath + '/EVALUATION/FOREVER_%04d-%02d-%02d %02dH%02d.csv'% localtime()[:5],  
            outFrequency=2, 
            log =True, 
            header= True, 
            fileOutAppend = False, 
            )
        
        tend =time()
        print('simulate in %s s.' % str(tend-tstart))

##    import cProfile
##    #Do simulation
##
##    if _endYear>0:
##        tstart =time()
##        
##        code='''simulate(
##        mdl = mdl, 
##        endYear = _endYear, 
##        fileoutName = basePath + '/EVALUATION/FOREVER_%04d-%02d-%02d %02dH%02d.csv'% localtime()[:5],  
##        outFrequency=2, 
##        log =True, 
##        header= True, 
##        fileOutAppend = False, 
##        )
##        '''
##        cProfile.run(code)
##        
##        tend =time()
##        print('simulate in %s s.' % str(tend-tstart))
