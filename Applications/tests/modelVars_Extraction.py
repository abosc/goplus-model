#Add the base path of GOplus to import GOplus modules used
import sys, os
basePath  = os.path.realpath(__file__).split('/Applications')[0]
sys.path.append(basePath) 


if __name__ == '__main__':
    from GOplus.goModel.mdlModel import Model
    from GOplus.goTools.VarsIntegrater import IntegrateMeanVarsPaths
   
    mdl = Model()
    
    print(IntegrateMeanVarsPaths(mdl))
