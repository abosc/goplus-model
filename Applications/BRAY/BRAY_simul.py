# -*- coding: utf-8 -*-

#Add the base path of GOplus to import GOplus modules used
import sys, os
basePath = os.path.realpath(__file__).split('/Applications')[0]
sys.path.append(basePath)

from GOplus import Model, Integrater
from GOplus.goModel.ManagerElements import LANDAIS_Manager

# BRAY PRACTICES :
# SEQUENCE OF THE INTERVENTIONS : dict of YYYY : ('type', density, xxx, xxx)
INTERVENTIONS = {
        1971 : ('PLANTATION', 1600, 2), #hypothetic
        1977 : ('RESPACING', 1100, 1.5, True), #hypothetic
        1983 : ('RESPACING', 828, 1.5, False),  #date hypothetic
        1991 : ('RESPACING', 616, 1.57, True),
        1996 : ('RESPACING', 520, 2.71, True),
        1999 : ('RESPACING', 422, 0.671,True),  #Martin storm
        2001 : ('RESPACING', 409, 0.7, False),  #post storm mortality
        2002 : ('RESPACING', 391, 0.7, False),  #post storm mortality
        2003 : ('RESPACING', 385, 0.7, False),  #post storm mortality
        2004 : ('RESPACING', 310, 3.03, True),
        2006 : ('RESPACING', 302, 0.7, False),  #post storm mortality
        2008 : ('RESPACING', 195, 1.5, True),
        2012 : ('RESPACING', 0, 1.0, True),
        }


class BRAY_Manager(LANDAIS_Manager.Manager):

    def update(self):
        #Manage the interventions
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.sunTime.isYearEnd and self.sunTime.Y == interventionYear  :

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
                    self.lastThinningYear= self.sunTime.Y


def model(
    startYear,      #initial year
    meteoFile,    #meteo file path : str
    ):
    '''return an instance of the Model parameterized and initialized for the Bray site.
    '''

   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = BRAY_Manager()
    mdl.sunTime.Y_start = startYear

   #specific parameters linked to the climate file
    mdl.climate.meteo_file_path = meteoFile
    mdl.sunTime.allowBissextileYear = 1 #1:Agroclim data set, 0:Arpege climat meteo file don't have bissextile year

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
    mdl = None,  #model instance
    endYear = 2008,      #end year
    fileoutName = 'Bray_simul.csv',  #name of the file to write the integrated model variables
    outFrequency = 1,  #0 for end hour, 1 for end day, 2 for end year
    log = True,                #boolean to indicate if simulation information are print
    startYear = 1987, #start year
    ):
    '''conduct a default simulation (Bray)
    '''

    #Define the model if not furnished with specific parameterisation for the exercice
    if mdl is None:
        mdl = model(
            startYear = startYear,
            meteoFile = basePath +'/GOplus/Data/BRAY_hour meteo_rebuild.csv',
            )

    #Define the integrater
    integrater =Integrater(mdl) #use the default integrable variables

    #open the fileOut and write header
    with open(fileoutName, 'w') as fileOut:
        fileOut.write('%s\n' % integrater.varNames)

        #short reference to sunTime object to accelerate conditionnal tests
        sunTime = mdl.sunTime

        #simulation loop
        while (sunTime.Y is None) or (sunTime.Y <endYear + 1):

            #update the model state
            mdl.update()

            #made  the integrations of model variables and output the integrated values each day
            integrater.integrate()

            if (True,  sunTime.isDayEnd,  sunTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())

            #some informations to follow simulation
            if log and sunTime.isYearBeginning:
                print (str(sunTime.Y), ', nb trees: ',  str(mdl.forest.treeStand.treesCount), ', LAI:',  str(mdl.forest.treeStand.canopy.LAI), ', HEIGHTmean:',  str(mdl.forest.treeStand.HEIGHTmean), ', Wa:',  str(mdl.forest.treeStand.Wa))
                
    return mdl


if __name__ == '__main__':
    from time import localtime, time

    def ask(prompt = '',default = ''):
        #to be Python2 and Python3 compatible redefine raw_input
        input3 =  input if  int(sys.version[0]) >2 else raw_input

        rep = input3('%s: (%s) ' % (prompt,default))

        if rep == '' : return default
        return rep


    endYear = int(ask('Please enter the last year of simulation',2008)) #Ask for endYear parameter
    outFrequency = int(ask('Please enter the out frequency (0 : hour,1: day, 2:year)',1) ) #Ask for outFrequency param
    fileoutName = basePath + '/EVALUATION/BRAY_simul_%04d-%02d-%02d %02dH%02d.csv' % localtime()[:5]  #add time stamp on file out

    #Do simulation
    tstart =time()
    mdl = simulate(endYear = endYear, fileoutName = fileoutName, outFrequency = outFrequency, log = True)
    print('simulate in %s s.' % str(time()-tstart))



