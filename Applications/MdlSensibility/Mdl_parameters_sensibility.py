import sys
basePath  = __file__.split('/Applications')[0]
sys.path.append(basePath) 

from Applications.BRAY.BRAY_simul import model
from GOplus.goTools.VarsIntegrater import Integrater


###TEST CONDITIONS ######################

#parameters is a list of the paremeters tested for the sensibility response
parameters = [
  'mdl.forest.soil.waterCycle.w_FC', 
  ]

#krange is 
krange = (0.65, 0.85, 0.95, 1, 1.05,  1.15, 1.35)

varsTested = '''
Last: mdl.manager.harvested_Wstem
Mean: mdl.forest.treeStand.canopy.LAI
Mean: mdl.forest.ETR
Mean: mdl.forest.NEE
Mean: mdl.forest.Rnet
Mean: mdl.forest.H
'''

_endYear = 2008

###################################
from time import  time

tstart =time()
simRes = {}

for k in krange:

    #obtain an instance of model with specific parameterisation of Bray
    mdl = model( 
                startYear = 1987,  
                meteoFile = basePath +'/RESSOURCES/BRAY_hour meteo_rebuild.csv', 
                )
    
    #modify tested parameter in proportion to k
    for paramStr in parameters:
        exec('%s *= k' % paramStr)
    
    #conduct simulation
    integrater =Integrater(mdl, varsTested)
    locTime = mdl.locTime
    while  (locTime.Y is None) or (locTime.Y <endYear + 1): 
        mdl.update()
        integrater.integrate()
    
    #outputs
    simRes[k] = integrater.putStr()
    print('%s, %s'%(k, simRes[k]) )

tend =time()
print('Sensibilty test do in %s s.' % str(tend-tstart))


