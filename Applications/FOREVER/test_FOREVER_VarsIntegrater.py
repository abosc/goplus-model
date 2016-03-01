
sdef = """
_reset = True
_count  = 0

#SHORT OBJECT ACCESS
locTime = mdl.locTime
microclim = mdl.climate.microclim
forest = mdl.forest
treeStand= forest.treeStand
treeStand_canopy = treeStand.canopy
underStorey = forest.underStorey
underStorey_canopy = underStorey.canopy
underStorey_foliage = underStorey.foliage
underStorey_roots = underStorey.roots
underStorey_perennial = underStorey.perennial
soil = forest.soil
soil_surface = soil.surface
soil_waterCycle = soil.waterCycle
soil_carbonCycle = soil.carbonCycle
manager = mdl.manager

#INTEGRATIVE VARIABLES
VI_locTime_Y = 0.
VI_microclim_RsDif = 0.
VI_microclim_RsDir = 0.
VI_microclim_RsUp = 0.
VI_microclim_RthDw = 0.
VI_microclim_RthUp = 0.
VI_microclim_TaC = 0.
VI_microclim_Rain = 0.
VI_microclim_d = 0.
VI_forest_ETR = 0.
VI_forest_NEE = 0.
VI_forest_Rnet = 0.
VI_forest_H = 0.
VI_treeStand_Age = 0.
VI_treeStand_LeafFall = 0.
VI_treeStand_SoilRootsWaterPotential = 0.
VI_treeStand_Rm = 0.
VI_treeStand_Rg = 0.
VI_treeStand_BranchSenescence = 0.
VI_treeStand_RootSenescence = 0.
VI_treeStand_IStress = 0.
VI_treeStand_density = 0.
VI_treeStand_DBHmean = 0.
VI_treeStand_HEIGHTmean = 0.
VI_treeStand_W = 0.
VI_treeStand_Wa = 0.
VI_treeStand_Wr = 0.
VI_treeStand_Wstem = 0.
VI_treeStand_WProducted = 0.
VI_treeStand_canopy_LAI = 0.
VI_treeStand_canopy_Rnet = 0.
VI_treeStand_canopy_H = 0.
VI_treeStand_canopy_Transpiration = 0.
VI_treeStand_canopy_Evaporation = 0.
VI_treeStand_canopy_Assimilation = 0.
VI_underStorey_Rm = 0.
VI_underStorey_Rg = 0.
VI_underStorey_foliage_LitterFall = 0.
VI_underStorey_roots_LitterFall = 0.
VI_underStorey_perennial_LitterFall = 0.
VI_underStorey_canopy_LAI = 0.
VI_underStorey_canopy_Rnet = 0.
VI_underStorey_canopy_H = 0.
VI_underStorey_canopy_Transpiration = 0.
VI_underStorey_canopy_Evaporation = 0.
VI_underStorey_canopy_Assimilation = 0.
VI_underStorey_foliage_W = 0.
VI_underStorey_perennial_W = 0.
VI_underStorey_roots_W = 0.
VI_soil_surface_Rnet = 0.
VI_soil_surface_H = 0.
VI_soil_surface_ETR = 0.
VI_soil_waterCycle_MoistureDeficit = 0.
VI_soil_waterCycle_RootLayerWaterPotential = 0.
VI_soil_carbonCycle_Ra = 0.
VI_soil_carbonCycle_Rh = 0.
VI_soil_carbonCycle_HUM = 0.
VI_soil_carbonCycle_BIO = 0.
VI_soil_carbonCycle_DPM = 0.
VI_soil_carbonCycle_RPM = 0.
VI_manager_harvest_Wstem = 0.
VI_manager_harvest_Wcrown = 0.
VI_manager_harvest_Wtaproot = 0.
VI_manager_harvest_DBHmean = 0.
VI_manager_harvest_DBHsd = 0.
VI_manager_harvest_DBHquadratic = 0.
VI_manager_harvest_HEIGHTmean = 0.
VI_manager_harvest_HEIGHTsd = 0.

def integrate():

    global _count
    global _reset
    global VI_microclim_RsDif
    global VI_microclim_RsDir
    global VI_microclim_RsUp
    global VI_microclim_RthDw
    global VI_microclim_RthUp
    global VI_microclim_TaC
    global VI_microclim_Rain
    global VI_microclim_d
    global VI_forest_ETR
    global VI_forest_NEE
    global VI_forest_Rnet
    global VI_forest_H
    global VI_treeStand_LeafFall
    global VI_treeStand_SoilRootsWaterPotential
    global VI_treeStand_Rm
    global VI_treeStand_Rg
    global VI_treeStand_BranchSenescence
    global VI_treeStand_RootSenescence
    global VI_treeStand_canopy_LAI
    global VI_treeStand_canopy_Rnet
    global VI_treeStand_canopy_H
    global VI_treeStand_canopy_Transpiration
    global VI_treeStand_canopy_Evaporation
    global VI_treeStand_canopy_Assimilation
    global VI_underStorey_Rm
    global VI_underStorey_Rg
    global VI_underStorey_foliage_LitterFall
    global VI_underStorey_roots_LitterFall
    global VI_underStorey_perennial_LitterFall
    global VI_underStorey_canopy_LAI
    global VI_underStorey_canopy_Rnet
    global VI_underStorey_canopy_H
    global VI_underStorey_canopy_Transpiration
    global VI_underStorey_canopy_Evaporation
    global VI_underStorey_canopy_Assimilation
    global VI_soil_surface_Rnet
    global VI_soil_surface_H
    global VI_soil_surface_ETR
    global VI_soil_waterCycle_MoistureDeficit
    global VI_soil_waterCycle_RootLayerWaterPotential
    global VI_soil_carbonCycle_Ra
    global VI_soil_carbonCycle_Rh

    if _reset : #reset
        _count = 1
        _reset = False
        VI_microclim_RsDif = microclim.RsDif 
        VI_microclim_RsDir = microclim.RsDir 
        VI_microclim_RsUp = microclim.RsUp 
        VI_microclim_RthDw = microclim.RthDw 
        VI_microclim_RthUp = microclim.RthUp 
        VI_microclim_TaC = microclim.TaC 
        VI_microclim_Rain = microclim.Rain
        VI_microclim_d = microclim.d 
        VI_forest_ETR = forest.ETR
        VI_forest_NEE = forest.NEE
        VI_forest_Rnet = forest.Rnet 
        VI_forest_H = forest.H 
        VI_treeStand_LeafFall = treeStand.LeafFall 
        VI_treeStand_SoilRootsWaterPotential = treeStand.SoilRootsWaterPotential 
        VI_treeStand_Rm = treeStand.Rm
        VI_treeStand_Rg = treeStand.Rg
        VI_treeStand_BranchSenescence = treeStand.BranchSenescence 
        VI_treeStand_RootSenescence = treeStand.RootSenescence 
        VI_treeStand_canopy_LAI = treeStand_canopy.LAI 
        VI_treeStand_canopy_Rnet = treeStand_canopy.Rnet 
        VI_treeStand_canopy_H = treeStand_canopy.H 
        VI_treeStand_canopy_Transpiration = treeStand_canopy.Transpiration
        VI_treeStand_canopy_Evaporation = treeStand_canopy.Evaporation
        VI_treeStand_canopy_Assimilation = treeStand_canopy.Assimilation
        VI_underStorey_Rm = underStorey.Rm
        VI_underStorey_Rg = underStorey.Rg
        VI_underStorey_foliage_LitterFall = underStorey_foliage.LitterFall 
        VI_underStorey_roots_LitterFall = underStorey_roots.LitterFall 
        VI_underStorey_perennial_LitterFall = underStorey_perennial.LitterFall 
        VI_underStorey_canopy_LAI = underStorey_canopy.LAI
        VI_underStorey_canopy_Rnet = underStorey_canopy.Rnet 
        VI_underStorey_canopy_H = underStorey_canopy.H 
        VI_underStorey_canopy_Transpiration = underStorey_canopy.Transpiration
        VI_underStorey_canopy_Evaporation = underStorey_canopy.Evaporation
        VI_underStorey_canopy_Assimilation = underStorey_canopy.Assimilation
        VI_soil_surface_Rnet = soil_surface.Rnet 
        VI_soil_surface_H = soil_surface.H 
        VI_soil_surface_ETR = soil_surface.ETR
        VI_soil_waterCycle_MoistureDeficit = soil_waterCycle.MoistureDeficit 
        VI_soil_waterCycle_RootLayerWaterPotential = soil_waterCycle.RootLayerWaterPotential 
        VI_soil_carbonCycle_Ra = soil_carbonCycle.Ra
        VI_soil_carbonCycle_Rh = soil_carbonCycle.Rh
        
    else: #Integrate
        _count += 1
        VI_microclim_RsDif += microclim.RsDif #Mean
        VI_microclim_RsDir += microclim.RsDir #Mean
        VI_microclim_RsUp += microclim.RsUp #Mean
        VI_microclim_RthDw += microclim.RthDw #Mean
        VI_microclim_RthUp += microclim.RthUp #Mean
        VI_microclim_TaC += microclim.TaC #Mean
        VI_microclim_Rain += microclim.Rain #Sum
        VI_microclim_d += microclim.d #Mean
        VI_forest_ETR += forest.ETR #Sum
        VI_forest_NEE += forest.NEE #Sum
        VI_forest_Rnet += forest.Rnet #Mean
        VI_forest_H += forest.H #Mean
        VI_treeStand_LeafFall += treeStand.LeafFall #Mean
        VI_treeStand_SoilRootsWaterPotential += treeStand.SoilRootsWaterPotential #Mean
        VI_treeStand_Rm += treeStand.Rm #Sum
        VI_treeStand_Rg += treeStand.Rg #Sum
        VI_treeStand_BranchSenescence += treeStand.BranchSenescence #Mean
        VI_treeStand_RootSenescence += treeStand.RootSenescence #Mean
        VI_treeStand_canopy_LAI += treeStand_canopy.LAI #Mean
        VI_treeStand_canopy_Rnet += treeStand_canopy.Rnet #Mean
        VI_treeStand_canopy_H += treeStand_canopy.H #Mean
        VI_treeStand_canopy_Transpiration += treeStand_canopy.Transpiration #Sum
        VI_treeStand_canopy_Evaporation += treeStand_canopy.Evaporation #Sum
        VI_treeStand_canopy_Assimilation += treeStand_canopy.Assimilation #Sum
        VI_underStorey_Rm += underStorey.Rm #Sum
        VI_underStorey_Rg += underStorey.Rg #Sum
        VI_underStorey_foliage_LitterFall += underStorey_foliage.LitterFall #Mean
        VI_underStorey_roots_LitterFall += underStorey_roots.LitterFall #Mean
        VI_underStorey_perennial_LitterFall += underStorey_perennial.LitterFall #Mean
        VI_underStorey_canopy_LAI = max(VI_underStorey_canopy_LAI,underStorey_canopy.LAI) #Max
        VI_underStorey_canopy_Rnet += underStorey_canopy.Rnet #Mean
        VI_underStorey_canopy_H += underStorey_canopy.H #Mean
        VI_underStorey_canopy_Transpiration += underStorey_canopy.Transpiration #Sum
        VI_underStorey_canopy_Evaporation += underStorey_canopy.Evaporation #Sum
        VI_underStorey_canopy_Assimilation += underStorey_canopy.Assimilation #Sum
        VI_soil_surface_Rnet += soil_surface.Rnet #Mean
        VI_soil_surface_H += soil_surface.H #Mean
        VI_soil_surface_ETR += soil_surface.ETR #Sum
        VI_soil_waterCycle_MoistureDeficit += soil_waterCycle.MoistureDeficit #Mean
        VI_soil_waterCycle_RootLayerWaterPotential += soil_waterCycle.RootLayerWaterPotential #Mean
        VI_soil_carbonCycle_Ra += soil_carbonCycle.Ra #Sum
        VI_soil_carbonCycle_Rh += soil_carbonCycle.Rh #Sum
        
def putStr():
    global _reset
    _reset = True
    return ','.join(['%G' % v for v in (
            locTime.Y,
            VI_microclim_RsDif/_count,
            VI_microclim_RsDir/_count,
            VI_microclim_RsUp/_count,
            VI_microclim_RthDw/_count,
            VI_microclim_RthUp/_count,
            VI_microclim_TaC/_count,
            VI_microclim_Rain,
            VI_microclim_d/_count,
            VI_forest_ETR,
            VI_forest_NEE,
            VI_forest_Rnet/_count,
            VI_forest_H/_count,
            treeStand.Age,
            VI_treeStand_LeafFall/_count,
            VI_treeStand_SoilRootsWaterPotential/_count,
            VI_treeStand_Rm,
            VI_treeStand_Rg,
            VI_treeStand_BranchSenescence/_count,
            VI_treeStand_RootSenescence/_count,
            treeStand.IStress,
            treeStand.density,
            treeStand.DBHmean,
            treeStand.HEIGHTmean,
            treeStand.W,
            treeStand.Wa,
            treeStand.Wr,
            treeStand.Wstem,
            treeStand.WProducted,
            VI_treeStand_canopy_LAI/_count,
            VI_treeStand_canopy_Rnet/_count,
            VI_treeStand_canopy_H/_count,
            VI_treeStand_canopy_Transpiration,
            VI_treeStand_canopy_Evaporation,
            VI_treeStand_canopy_Assimilation,
            VI_underStorey_Rm,
            VI_underStorey_Rg,
            VI_underStorey_foliage_LitterFall/_count,
            VI_underStorey_roots_LitterFall/_count,
            VI_underStorey_perennial_LitterFall/_count,
            VI_underStorey_canopy_LAI,
            VI_underStorey_canopy_Rnet/_count,
            VI_underStorey_canopy_H/_count,
            VI_underStorey_canopy_Transpiration,
            VI_underStorey_canopy_Evaporation,
            VI_underStorey_canopy_Assimilation,
            underStorey_foliage.W,
            underStorey_perennial.W,
            underStorey_roots.W,
            VI_soil_surface_Rnet/_count,
            VI_soil_surface_H/_count,
            VI_soil_surface_ETR,
            VI_soil_waterCycle_MoistureDeficit/_count,
            VI_soil_waterCycle_RootLayerWaterPotential/_count,
            VI_soil_carbonCycle_Ra,
            VI_soil_carbonCycle_Rh,
            soil_carbonCycle.HUM,
            soil_carbonCycle.BIO,
            soil_carbonCycle.DPM,
            soil_carbonCycle.RPM,
            manager.harvest_Wstem,
            manager.harvest_Wcrown,
            manager.harvest_Wtaproot,
            manager.harvest_DBHmean,
            manager.harvest_DBHsd,
            manager.harvest_DBHquadratic,
            manager.harvest_HEIGHTmean,
            manager.harvest_HEIGHTsd
        )])

varNames = ','.join([
    'Last : locTime.Y',
    'Mean : microclim.RsDif',
    'Mean : microclim.RsDir',
    'Mean : microclim.RsUp',
    'Mean : microclim.RthDw',
    'Mean : microclim.RthUp',
    'Mean : microclim.TaC',
    'Sum : microclim.Rain',
    'Mean : microclim.d',
    'Sum : forest.ETR',
    'Sum : forest.NEE',
    'Mean : forest.Rnet',
    'Mean : forest.H',
    'Last : treeStand.Age',
    'Mean : treeStand.LeafFall',
    'Mean : treeStand.SoilRootsWaterPotential',
    'Sum : treeStand.Rm',
    'Sum : treeStand.Rg',
    'Mean : treeStand.BranchSenescence',
    'Mean : treeStand.RootSenescence',
    'Last : treeStand.IStress',
    'Last : treeStand.density',
    'Last : treeStand.DBHmean',
    'Last : treeStand.HEIGHTmean',
    'Last : treeStand.W',
    'Last : treeStand.Wa',
    'Last : treeStand.Wr',
    'Last : treeStand.Wstem',
    'Last : treeStand.WProducted',
    'Mean : treeStand_canopy.LAI',
    'Mean : treeStand_canopy.Rnet',
    'Mean : treeStand_canopy.H',
    'Sum : treeStand_canopy.Transpiration',
    'Sum : treeStand_canopy.Evaporation',
    'Sum : treeStand_canopy.Assimilation',
    'Sum : underStorey.Rm',
    'Sum : underStorey.Rg',
    'Mean : underStorey_foliage.LitterFall',
    'Mean : underStorey_roots.LitterFall',
    'Mean : underStorey_perennial.LitterFall',
    'Max : underStorey_canopy.LAI',
    'Mean : underStorey_canopy.Rnet',
    'Mean : underStorey_canopy.H',
    'Sum : underStorey_canopy.Transpiration',
    'Sum : underStorey_canopy.Evaporation',
    'Sum : underStorey_canopy.Assimilation',
    'Last : underStorey_foliage.W',
    'Last : underStorey_perennial.W',
    'Last : underStorey_roots.W',
    'Mean : soil_surface.Rnet',
    'Mean : soil_surface.H',
    'Sum : soil_surface.ETR',
    'Mean : soil_waterCycle.MoistureDeficit',
    'Mean : soil_waterCycle.RootLayerWaterPotential',
    'Sum : soil_carbonCycle.Ra',
    'Sum : soil_carbonCycle.Rh',
    'Last : soil_carbonCycle.HUM',
    'Last : soil_carbonCycle.BIO',
    'Last : soil_carbonCycle.DPM',
    'Last : soil_carbonCycle.RPM',
    'Last : manager.harvest_Wstem',
    'Last : manager.harvest_Wcrown',
    'Last : manager.harvest_Wtaproot',
    'Last : manager.harvest_DBHmean',
    'Last : manager.harvest_DBHsd',
    'Last : manager.harvest_DBHquadratic',
    'Last : manager.harvest_HEIGHTmean',
    'Last : manager.harvest_HEIGHTsd'
    ])

"""

class Integrater:
    def __init__(self, elt, intgVarsPaths):
        dg ={'mdl':elt}
        exec(sdef, dg)
        self.__dict__ = dg

