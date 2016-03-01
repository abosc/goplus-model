#
import sys
basePath  = __file__.split('/Applications')[0]
sys.path.append(basePath) 

from Applications.BRAY.BRAY_simul import model
from GOplus.goTools.VarsIntegrater import Integrater


###TEST CONDITIONS ######################

#PARAMETERS is a list of one or more paremeters modified to test the sensibility response of output variables
#if more one variables is furnished, they are modified together
PARAMETERS = [
  'mdl.forest.soil.waterCycle.w_FC', 
  ]

#KRANGE is 
KRANGE = (0.65, 0.85, 0.95, 1, 1.05,  1.15, 1.35)

VARS_TESTED = '''
Last: mdl.manager.harvested_Wstem
Mean: mdl.forest.treeStand.canopy.LAI
Mean: mdl.forest.ETR
Mean: mdl.forest.NEE
Mean: mdl.forest.Rnet
Mean: mdl.forest.H
'''

endYear = 2008

###################################
from time import  time

tstart =time()
simRes = {}

for k in KRANGE:

    #obtain an instance of model with specific parameterisation of Bray
    mdl = model( 
                startYear = 1987,  
                meteoFile = basePath +'/RESSOURCES/BRAY_hour meteo_rebuild.csv', 
                )
    
    #modify tested parameter in proportion to k
    for paramStr in PARAMETERS:
        exec('%s *= k' % paramStr)
    
    #conduct simulation
    integrater =Integrater(mdl, VARS_TESTED)
    sunTime = mdl.sunTime
    while  (sunTime.Y is None) or (sunTime.Y <endYear + 1): 
        mdl.update()
        integrater.integrate()
    
    #outputs
    simRes[k] = integrater.putStr()
    print('%s, %s'%(k, simRes[k]) )

tend =time()
print('Sensibilty test do in %s s.' % str(tend-tstart))


