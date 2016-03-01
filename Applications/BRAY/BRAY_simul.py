
varsToIntegrate = '''
Last: mdl.locTime.Y
Mean: mdl.climate.microclim.RsDif
Mean: mdl.climate.microclim.RsDir
Mean: mdl.climate.microclim.RsUp
Mean: mdl.climate.microclim.RthDw
Mean: mdl.climate.microclim.RthUp
Mean: mdl.climate.microclim.TaC
Sum: mdl.climate.microclim.Rain
Mean: mdl.climate.microclim.d
Sum: mdl.forest.ETR
Sum: mdl.forest.NEE
Mean: mdl.forest.Rnet
Mean: mdl.forest.H
Last: mdl.forest.treeStand.Age
Mean: mdl.forest.treeStand.LeafFall
Mean: mdl.forest.treeStand.SoilRootsWaterPotential
Sum: mdl.forest.treeStand.Rm
Sum: mdl.forest.treeStand.Rg
Mean: mdl.forest.treeStand.BranchSenescence
Mean: mdl.forest.treeStand.RootSenescence
Last: mdl.forest.treeStand.IStress
Last: mdl.forest.treeStand.treesCount
Last: mdl.forest.treeStand.DBHmean
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.W
Last: mdl.forest.treeStand.Wa
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.Wstem
Last: mdl.forest.treeStand.WProducted
Mean: mdl.forest.treeStand.canopy.LAI
Mean: mdl.forest.treeStand.canopy.Rnet
Mean: mdl.forest.treeStand.canopy.H
Sum: mdl.forest.treeStand.canopy.Transpiration
Sum: mdl.forest.treeStand.canopy.Evaporation
Sum: mdl.forest.treeStand.canopy.Assimilation
Sum: mdl.forest.underStorey.Rm
Sum: mdl.forest.underStorey.Rg
Mean: mdl.forest.underStorey.foliage.LitterFall
Mean: mdl.forest.underStorey.roots.LitterFall
Mean: mdl.forest.underStorey.perennial.LitterFall
Max: mdl.forest.underStorey.canopy.LAI
Mean: mdl.forest.underStorey.canopy.Rnet
Mean: mdl.forest.underStorey.canopy.H
Sum: mdl.forest.underStorey.canopy.Transpiration
Sum: mdl.forest.underStorey.canopy.Evaporation
Sum: mdl.forest.underStorey.canopy.Assimilation
Mean: mdl.forest.soil.surface.Rnet
Mean: mdl.forest.soil.surface.H
Sum: mdl.forest.soil.surface.ETR
Mean: mdl.forest.soil.waterCycle.MoistureDeficit
Mean: mdl.forest.soil.waterCycle.RootLayerWaterPotential
Mean: mdl.forest.soil.carbonCycle.Ra
Mean: mdl.forest.soil.carbonCycle.Rh
Last: mdl.forest.soil.carbonCycle.HUM
Last: mdl.forest.soil.carbonCycle.BIO
Last: mdl.forest.soil.carbonCycle.DPM
Last: mdl.forest.soil.carbonCycle.RPM
Last: mdl.forest.soil.carbonCycle.HUM_age
Last: mdl.forest.soil.carbonCycle.BIO_age
Last: mdl.forest.soil.carbonCycle.DPM_age
Last: mdl.forest.soil.carbonCycle.RPM_age
Mean: mdl.manager.harvest_Wstem
Mean: mdl.manager.harvest_Wcrown
Mean: mdl.manager.harvest_Wstub
Mean: mdl.manager.harvest_Wtaproot
Mean: mdl.manager.harvest_Wneedles
'''

#Add the base path of GOplus to import GOplus modules used
import sys, os
basePath  = os.path.realpath(__file__).split('/Applications')[0]
sys.path.append(basePath) 

from GOplus import Model,  Integrater
from GOplus.goModel.ManagerElements import LANDAIS_Manager 

# BRAY PRACTICES : SEQUENCE OF THE INTERVENTIONS : dict of YYYY : ('type', density, xxx, xxx)
INTERVENTIONS = {
        1971 : ('PLANTATION', 1600, 2), #hypothetic
        1977 : ('RESPACING', 1100, 1.5, True), #hypothetic
        1983 : ('RESPACING', 828, 1.5,  False),  #date hypothetic
        1991 : ('RESPACING', 616, 1.57, True), 
        1996 : ('RESPACING', 520, 2.71, True), 
        1999 : ('RESPACING', 422,  0.671, True),  #Martin storm
        2001 : ('RESPACING', 409, 0.7, False),  #post storm mortality
        2002 : ('RESPACING', 391, 0.7, False),  #post storm mortality
        2003 : ('RESPACING',  385, 0.7, False),  #post storm mortality
        2004 : ('RESPACING',  310, 3.03,  True),  
        2006 : ('RESPACING',  302,  0.7,  False),  #post storm mortality
        2008 : ('RESPACING',  195,  1.5,  True), 
        2012 : ('RESPACING',  0,  1.0,  True), 
        }


class BRAY_Manager(LANDAIS_Manager.Manager):

    def update(self):
        #Manage the interventions
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.locTime.isYearEnd and self.locTime.Y == interventionYear  : 
                
                if  interventionParameters[0] == 'PLANTATION' :         
                    self.do_plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5,soilPerennialFractionAffected =0.95)
                    self.do_install_stand( interventionParameters[2], interventionParameters[1])
                    
                if  interventionParameters[0] == 'RESPACING' :
                    self.do_rouleau_Landais()
                    self.do_markRandomLogging(
                            randomFactor=interventionParameters[2], 
                            densityObjective = interventionParameters[1], 
                            )
                    self.do_Logging(
                            harvestStem = interventionParameters[3], 
                            harvestStub = False, 
                            harvestCrownWood = False, 
                            harvestTaproot = False, 
                            harvestNeedles = False, 
                            )
                    self.lastThinningYear= self.locTime.Y


def model(
    startYear,      #initial year
    meteoFile,    #meteo file path : str
    ):
    '''return an instance of the Model parameterized and initialized for the Bray site.
    '''
    
   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = BRAY_Manager() 
    mdl.locTime.Y_start = startYear
    
   #specific parameters linked to the climate file
    mdl.climate.meteo_file_path = meteoFile
    mdl.locTime.allowBissextileYear = 1 #1:Agroclim data set, 0:Arpege climat meteo file don't have bissextile year     

   #define the initial stand age and density from  INTERVENTIONS parameters and the startYear
    yearLastPlantation = max([y for y in INTERVENTIONS.keys() if y < startYear and INTERVENTIONS[y][0] == 'PLANTATION'])
    _initial_trees_Age =  startYear -  yearLastPlantation + INTERVENTIONS[yearLastPlantation][2] - 1

    yearLastIntervention = max([y for y in INTERVENTIONS.keys() if y < startYear])
    _initial_trees_Density = INTERVENTIONS[yearLastIntervention][1]
    
   #define the initial stand structure from stand age  using allometric relationship based on
   #pinus pinaster root-shoot ratio obtain on dataset furnished by Trichet P (parcelle L12ans &18ans, Bilos 50ans, parcelle M 63 ans)  
    from math import exp, log
    _trees_Wa_avg = exp( -0.336354*log(_initial_trees_Age)**2 + 3.742828*log(_initial_trees_Age) - 3.108378) #version FAST
    _trees_WrOnWa_avg = 0.085365*_trees_Wa_avg**0.176316
    
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    _installation.initialTreesAge = _initial_trees_Age
    _installation.initialTreesDensity = _initial_trees_Density
    _installation.initialTreesWa_avg = _trees_Wa_avg
    _installation.initialTreesWa_std = _trees_Wa_avg * 0.4
    _installation.initialTreesWrOnWa_avg = _trees_WrOnWa_avg
    _installation.initialTreesWrOnWa_std =  _trees_WrOnWa_avg*0.1
    
   #return the model 
    return mdl


def simulate(
    mdl,  #model instance
    endYear,      #end year
    fileoutName,  #name of the file to write the integrated model variables
    outFrequency,  #0 for end hour, 1 for end day, 2 for end year
    log,                #boolean to indicate if simulation information are print
    ):    
    '''conduct a default simulation (Bray) 
    '''

    #Define the integrater
    integrater =Integrater(mdl, varsToIntegrate) #use the default integrable variables

    #open the fileOut and write header
    with open(fileoutName, 'w') as fileOut:
        fileOut.write('%s\n' % integrater.varNames)

        #short reference to locTime object to accelerate conditionnal tests
        locTime = mdl.locTime 
        
        #simulation loop
        while (locTime.Y is None) or (locTime.Y <endYear + 1): 
            
            #update the model state
            mdl.update()
            
            #made  the integrations of model variables and output the integrated values each day
            integrater.integrate()
            
            if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())
            
            #some informations to follow simulation
            if log and locTime.isYearBeginning: 
                print (str(locTime.Y), ', nb trees: ',  str(mdl.forest.treeStand.treesCount), ', LAI:',  str(mdl.forest.treeStand.canopy.LAI), ', HEIGHTmean:',  str(mdl.forest.treeStand.HEIGHTmean), ', Wa:',  str(mdl.forest.treeStand.Wa))




def main():
    from time import localtime, time

    #obtain an instance of model with specific parameterisation for the exercice
    mdl = model( 
        startYear = 1987.0,  
        meteoFile = basePath +'/RESSOURCES/BRAY_hour meteo_rebuild.csv', 
        )

    #Ask for endYear parameter
    try:
        endYear = int(input('Please enter the last year of simulation (or 0 to avoid simulation) : ') )
    except : #input  on pypy and eric5 bug
        endYear = 2099
    
    #Do simulation
    if endYear>1987:
        tstart =time()

        simulate(
            mdl = mdl, 
            endYear = endYear, 
            fileoutName = basePath + '/EVALUATION/BRAY_simul_%04d-%02d-%02d %02dH%02d.csv' % localtime()[:5], 
            outFrequency=1, 
            log = True, 
            )
        tend =time()
        print('simulate in %s s.' % str(tend-tstart))





