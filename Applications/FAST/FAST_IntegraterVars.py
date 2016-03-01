
def variablesValues(mdl):
    '''return a list of the values of the model variables preceded by the integration type choosed
    '''

    #integration types
    Mean,  Sum, Max,  Min,  Last, SumWatt , SumDay= 0, 1,  2, 3,  4, 5, 6
    
    #type of integration and value of model variables
    return [
                Last, mdl.locTime.Y, 
                SumWatt, mdl.climate.microclim.RsDif,
                SumWatt, mdl.climate.microclim.RsDir,
                SumWatt, mdl.climate.microclim.RsUp,
                Mean, mdl.climate.microclim.TaC,
                Mean, mdl.climate.microclim.d,
                Sum, mdl.climate.microclim.Rain,
                
                Sum, mdl.forest.ETR,
                Sum, mdl.forest.NEE,
                SumWatt, mdl.forest.Rnet,
                SumWatt, mdl.forest.H,
                SumWatt, mdl.forest.LE,
                
                Last, mdl.forest.treeStand.trees[0].Age if len(mdl.forest.treeStand.trees)>0 else -1, 
                Last, mdl.forest.treeStand.treesCount*10, 
                Last, mdl.forest.treeStand.W,
                Last, mdl.forest.treeStand.Wa,
                Last, mdl.forest.treeStand.Wr,
                Last, mdl.forest.treeStand.Wstem,
                Last, mdl.forest.treeStand.dW,
                Last, mdl.forest.treeStand.dWa,
                Last, mdl.forest.treeStand.dWr,
                Last, mdl.forest.treeStand.BranchSenescence,
                Last, mdl.forest.treeStand.RootSenescence,
                Sum, mdl.forest.treeStand.LeafFall,
                Last, mdl.forest.treeStand.LAI,
                Sum, mdl.forest.treeStand.Transpiration,
                Sum, mdl.forest.treeStand.ETR,
                Sum, mdl.forest.treeStand.Assimilation,
                Sum, mdl.forest.treeStand.Rm,
                Sum, mdl.forest.treeStand.Rg,
                Last, mdl.forest.treeStand.IStress,
                Last, mdl.forest.treeStand.AllocRoot,
                
                Max, mdl.forest.underStorey.LAI,
                Sum, mdl.forest.underStorey.Transpiration,
                Sum, mdl.forest.underStorey.ETR,
                Sum, mdl.forest.underStorey.Assimilation,
                Sum, mdl.forest.underStorey.Rm,
                Sum, mdl.forest.underStorey.Rg,

                Max, mdl.forest.underStorey.foliage.W,
                SumDay, mdl.forest.underStorey.foliage.Growth,
                SumDay, mdl.forest.underStorey.foliage.LitterFall,                
                SumDay, mdl.forest.underStorey.foliage.Cpool,                

                Mean, mdl.forest.underStorey.roots.W,
                SumDay, mdl.forest.underStorey.roots.Growth,
                SumDay, mdl.forest.underStorey.roots.LitterFall,   
                SumDay, mdl.forest.underStorey.roots.Cpool,   
                
                Mean, mdl.forest.underStorey.perennial.W,
                SumDay, mdl.forest.underStorey.perennial.Growth,
                SumDay, mdl.forest.underStorey.perennial.LitterFall,   
                SumDay, mdl.forest.underStorey.perennial.Cpool,   
                
                Sum, mdl.forest.soil.ETR,
                Mean, mdl.forest.soil.MoistureDeficit, 
                Mean, mdl.forest.soil.RootLayerWaterPotential, 
                Mean, mdl.forest.soil.w_A, 
                Sum, mdl.forest.soil.Rh,
                Last, mdl.forest.soil.HUM,
                Last, mdl.forest.soil.BIO,
                Last, mdl.forest.soil.DPM,
                Last, mdl.forest.soil.RPM,
                Last, mdl.forest.soil.IOM,
                Sum, mdl.forest.soil._IDPM_sum,
                Sum, mdl.forest.soil._IRPM_sum,
                
                Last, mdl.manager.harvested_Wstem, 
                Last, mdl.manager.harvested_WCrown, 
                Last, mdl.manager.harvested_Wstub, 
            ]


#the names used as header for the variables integrated and saved
#The easier is to make a copy of the list  content return by the function variablesValues
variablesNames = '''
                Last, mdl.locTime.Y, 
                SumWatt, mdl.climate.microclim.RsDif,
                SumWatt, mdl.climate.microclim.RsDir,
                SumWatt, mdl.climate.microclim.RsUp,
                Mean, mdl.climate.microclim.TaC,
                Mean, mdl.climate.microclim.d,
                Sum, mdl.climate.microclim.Rain,
                
                Sum, mdl.forest.ETR,
                Sum, mdl.forest.NEE,
                SumWatt, mdl.forest.Rnet,
                SumWatt, mdl.forest.H,
                SumWatt, mdl.forest.LE,
                
                Last, mdl.forest.treeStand.trees[0].Age if len(mdl.forest.treeStand.trees)>0 else -1, 
                Last, mdl.forest.treeStand.treesCount*10, 
                Last, mdl.forest.treeStand.W,
                Last, mdl.forest.treeStand.Wa,
                Last, mdl.forest.treeStand.Wr,
                Last, mdl.forest.treeStand.Wstem,
                Last, mdl.forest.treeStand.dW,
                Last, mdl.forest.treeStand.dWa,
                Last, mdl.forest.treeStand.dWr,
                Last, mdl.forest.treeStand.BranchSenescence,
                Last, mdl.forest.treeStand.RootSenescence,
                Sum, mdl.forest.treeStand.LeafFall,
                Last, mdl.forest.treeStand.LAI,
                Sum, mdl.forest.treeStand.Transpiration,
                Sum, mdl.forest.treeStand.ETR,
                Sum, mdl.forest.treeStand.Assimilation,
                Sum, mdl.forest.treeStand.Rm,
                Sum, mdl.forest.treeStand.Rg,
                Last, mdl.forest.treeStand.IStress,
                Last, mdl.forest.treeStand.AllocRoot,
                
                Max, mdl.forest.underStorey.LAI,
                Sum, mdl.forest.underStorey.Transpiration,
                Sum, mdl.forest.underStorey.ETR,
                Sum, mdl.forest.underStorey.Assimilation,
                Sum, mdl.forest.underStorey.Rm,
                Sum, mdl.forest.underStorey.Rg,

                Max, mdl.forest.underStorey.foliage.W,
                SumDay, mdl.forest.underStorey.foliage.Growth,
                SumDay, mdl.forest.underStorey.foliage.LitterFall,                
                SumDay, mdl.forest.underStorey.foliage.Cpool,                

                Mean, mdl.forest.underStorey.roots.W,
                SumDay, mdl.forest.underStorey.roots.Growth,
                SumDay, mdl.forest.underStorey.roots.LitterFall,   
                SumDay, mdl.forest.underStorey.roots.Cpool,   
                
                Mean, mdl.forest.underStorey.perennial.W,
                SumDay, mdl.forest.underStorey.perennial.Growth,
                SumDay, mdl.forest.underStorey.perennial.LitterFall,   
                SumDay, mdl.forest.underStorey.perennial.Cpool,   
                
                Sum, mdl.forest.soil.ETR,
                Mean, mdl.forest.soil.MoistureDeficit, 
                Mean, mdl.forest.soil.RootLayerWaterPotential, 
                Mean, mdl.forest.soil.w_A, 
                Sum, mdl.forest.soil.Rh,
                Last, mdl.forest.soil.HUM,
                Last, mdl.forest.soil.BIO,
                Last, mdl.forest.soil.DPM,
                Last, mdl.forest.soil.RPM,
                Last, mdl.forest.soil.IOM,
                Sum, mdl.forest.soil._IDPM_sum,
                Sum, mdl.forest.soil._IRPM_sum,
                
                Last, mdl.manager.harvested_Wstem, 
                Last, mdl.manager.harvested_WCrown, 
                Last, mdl.manager.harvested_Wstub, 
                '''
