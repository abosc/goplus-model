# -*- coding: utf-8 -*-
'''Entry point of GO+ '''

version = {'rolling': True , 'serie':'PCS', 'major' : 26, 'minor': 0, 'rev': 0, 'date' : '2015-01-08'}
authors = u'Alexandre BOSC, Denis Loustau, Delphine Picart, Virginie Moreau, Annabel Porté'

#import all core objects of GOplus
from .goModel.mdlModel import Model
from .goTools.VarsIntegrater import Integrater
from .goTools import ELTinfos as infos

# HISTORIC OF GOplus versions (newer in top)
historic = '''
PCS in dev (rolling version)
***************************
PCS26-0-1 - 2015-01-14
***********************
- Pour atelier GO+
- If the intgVarsPaths parameter of  Integrater constructor is not pass, by default all variables are now integrated
- Simplification of the "GOplus package" :
    - less hierarchical level
    - more homogen subpackage name
- add the possibility to use GO+ as package or script (goStart)


PCS26-0-0 - 2014-09-15
***********************
NEW :
- New branch of model bases : branch PCS
    - In this branch processes are not ELT type and are defined by a method tagged by the @PCS decorator.
    - The implementation of process provides the same avantages than PP branch :
        - process parameters could be modified by ELT instance
        - process have the possibility to inherit from one define in an another class 
    - the implementation offer new avantages:
        - a syntax more in adequation with instance method. So inside the process, like for instance method of Python, the instance of the class is the first argument and we recommand to use name 'self' for it.
        - the possibility to inherit from a function, and so use function library.
        - a more ligth syntax inside the process expression, as parameter are defined locally from the function parameters.
        - a more rapid execution time as parameter are local variable of the function use by processes
    
    

DEBUG:
- goTools.VarsIntegrater: 
 A bug, that only increased dramatically the simulation time (when variables were saved), was discovered and corrected (Thank you cProfile).
 Finally code was optimized for time consumption, and now the fact to save model variables don't change significantly the simulation time.
 
-mdlUnderStorey:
  parameters names of pcs_StomatalConductance process for Yleaf sensibility are corrected from old denomination (<24.5.0) to new
  in last version they are ignored (so pine parameters were used in place)
  #TODO : change parameters value to be consistent with previous 
  
  
PP25-0-2 - 2014-07-16
***********************
DEBUG:
-manage the case of LAI not >0 in pcs_ShortWaveBalance


PP25-0-1 - 2014-07-16
***********************
DEBUG:
-manage the case of infinity low value of LAI in pcs_AerodynamicConductance to avoid division by z0=0

PP25-0-0 - 2014-07-15  
***********************
NEW : 
- Implementation of aerodynamique wind profil  to evaluate aerodynamique resistance taking into accound stand structure.
    - Neutral conditions
    - for the 3 layers
    - for treeStand and understorey height parameter used in calculs could not be less than 0.2 m (height of soil litter)
    - for soil a different formulation of surface resistance (raS) than those propose by Denis was used to have:
        raS=infiny at w_RES, and raS=0 at w_SAT (free water)

-treeStand.density variable is introducted : number of trees per hectare
-Manager has dendrometric dimensions of harvested trees :
    * DBHmean
    * DBHsd
    * DBHquadratic
    * HEIGHTmean
    * HEIGHTsd
    

DEBUG:
- pcs_ShortWaveBalance:
    correction of the sign inside the formul (exponentiel) to evaluate rho_cb (canopy reflection coefficient for beam irradiance with uniform leaf-angle distribution)
    <-- error in A19 equation of DePury 1997
- mathematic correction of the calcul of decomposition rate in RothC to take into account of an daily evaluation with annual parameter.
    Time step (dage ) must  be applied only inner the exponentiel (--> to dage) and not to dec.
- soil.waterCycle.pcs_layersDepthUpdate: 
    * correction of the modality to substract transpiration. Manage the case of w_A = w_FC
    
CHANGES:
- OneYearCohortWeightMax is anew evaluated only by allomtric relationship to Wa  
- albedo of soil was increased (0.1 -->0.2) 
- reflectance of understorey was increased (0.1 -->0.15) 
- Rd_25 for understorey was proportionnalize to Jmax_25 (pending a reference)
- soil.waterCycle.pcs_layersDepthUpdate: 
    * Evaporation is now substract to layer A and not B (to avoid, hight w_A and an infiny decrase od depth B)
- soil.surface



PP24-7-0 - 2014-07-04  
***********************
NEW:
- Add, for FOREVER  scenarii, the evaluation  of :
    - the  taproot biomass (TreeSizes) allometrically calculated from Wa. Necessary for intensive scenario where taproot are exported.
    - the HEIGHTdom,DBHdom and standard deviation of heigth and DBH (HEIGHTsd, DBHsd) for treeStand.
- The applications scripts  are isolated in a the directory file Applications. Where applications are
    - script that conduct a simulation for particular conditions
    - scripts that manipulate data simulated
    -... all that is not purely model element.
    

CHANGES:
- k_time_P50 : parameter used to define time response of stomata is now the time for 50% to equilibration (replace k_dt)
- the evaluation of OneYearCohortWeightMax was modified. The new version made the assumption than the new needle cohort primordium production is limited by :
            -  A : a physical supportable value by crown structure  evaluated allometrically to aerial Biomass
            -  B : a carbon allocation limitation
    
DEBUG:
- correct the under estimation of OneYeayCohortWeightMax at SimulBeginning linked to the reference to dWa (nul at initialisation).
- Leaf respiration was evaluated two time, respiration and Farquhar processes and, and removed two time from carbon balance.
    --> Only Farquahr process 

PP24-6-2 - 2014-06-16  
***********************
Debug :
- the alpha  parameter ('Quantum yield of electron transport ') of pcs_Assimilation for pine was bugged. 
    It's not a dimension linked to LAI, and don't need to be multiplied by the ratio LeafArea / LAI
    --> simply the litterature value
- in the module  BRAY the initial dimensions of trees was not defined. Do.

PP24-6-1 - 2014-06-13  
***********************
- pcs_Assimilation :
    -Jmax_Topt parameter was replace by Jmax_25 more easy to find in litterature --> inner formulation rearranged to take into account
    - alpha parameter (quantum yield of electron transport) was integrated
    - parameters of Vcmax_25 and Jmax_25, alpha for understorey where take on the DEA of Delzon S. (2000).

PP24-6-0 - 2014-06-12  
***********************
This version is an intermediate version to the SunShade-Farquahr model version
- Assimilation process is now evaluated by Farquahr model applied independly for the sun and shade Layer but simply with common 
 photosynthetic parameters for the two layers and not with parameters integrated on sun and shade layers according to DePury 1997
 - However, camparison with previous version show:
    - that Anet evaluated by Farquahr model is more stable from one day to another, as it is less sensible to RsDir
    - that Anet is now  in phase with g_stom used for evalauation of carbon limitation of Anet
    - that Anet could be now negative during very drougth period
 

PP24.5.0 - 2014-06-11 
***********************
This version is an intermediate version to the SunShade-Farquahr model version, for debug and comparison with previous version (BigLeaf -LUE)
Shortwave absorbtion is evaluated  according to the SunShade model of DePury et al. 1997 on to LeafLayer object (sunLayer, shadeLayer)

pcs_EnergyBalance losses shortwave evaluation.
All other canopy processes are not changed in particular Assimilation (LUE) and evaluated at canopy level.
Canopy Rs_Abs is cumulated from Sun and Shade Layer for other processes need.
Parametrage (based on that of DePury 1997) increase Rs_Abs by 50% in comparison with previous version --> Necessity to verified parameters

Parameters of pcs_StomatalConductance are reformulated to have meaning (default parameter values have changed but not the process response)

PP24.0.0 - 2014-06-04 
***********************
Version based on PP23.1.0

- Model bases :
    - Trés forte modification de goModelComponents pour permettre l'utilisation de 'process' paramétrés. 
        - d'avoir les paramètres liés aux process et donc de ne pas avoir a gérer 'l'évacuation des paramètres' quand un process change d'implémentation.
        - d'avoir une moindre pression sur les noms de paramètres car non mis dans un pot commun
    - Standardisation de la façon d'écrire les processus qui sont eux meme des ELT
        - Utilisation des nom p et s pour  designer l'objet processus et son element conteneur
        - p: processus, parameters,  s: shell, self (de l'objet element conteneur)
        - le processus peut accéder à son element conteneur par son attribut container
    - Les attributs non déclarés dans le corps des classes heritant de ELT ne sont pas autorisés(varibales, parameters) 
    
- Grosse refonte de l'ordonnancement des calculs pour donner la priorité aux process sur l'enboitement des pas de temps (year,day,hour)
    - le but est que chaque process soit complet, appelé au plus petit pas de temps et détermine seul  quand il se réévalue. 
    - ceci permet d'échanger des implémentation d'un meme processus var des versions pouvant avoir des pas de temps de résolution différents et avec leur jeu de paramètres propres

- Creation de l'element CanopySurface 
    - regroupant l'ensemble des processus  rapides : bilan d'energie, regulation stomatique, assimilation, rain interception ...
    - commun a treeStand et a underStorey
    - suppression de la référence à LeafArea , tous les flux étant ramenés au LAI,
        (ce choix est soutenu par la prédominance des jeux de paramètres de la biblio exprimés par m2 de LAI)
    
- Simplification de l'objet Tree --> TreeSize 
    - TreeSize ne contient plus les processus de gestion du carbone --> assumés par TreeStand
    - TreeSize ne contient que les dimensions d'un arbre et celles évaluées allométriquement
    - TreeStand fait désormais office de list des objets TreeSize
    
PP23.2.0 - 2014-03-08 
***********************
- Farquhar model was implemented to modelised photosynthesis (Medlyn et al. 2002)
- In this version :
        -TreeStand evaluate in parallel Farquhar model on the base of the big_leaf approach for comparaison, before sun/shade model
        -underGrowth is unchanged

PP23.1.0 - 2014-03-08 
***********************
Energy balance is evaluated in one pass for each layer
- underStorey energy Balance is evaluate by the same process  than TreeStand from pcsEnergyBalance
- Soil energy Balance is evaluate by an specific process from pcsEnergyBalance 
- In consequence for forest inner ELT (treeStand, underStoery and soil) there is now only an hour method called by forest : hour_update


PP23.0.0 - 2014-03-08 
***********************
Ouverture de la branche PP :
 - branche n'ayant plus la contrainte de pouvoir etre compilé par Shedskin.
 - L'optimisation se fera par Pypy --> préfixe PP au numéros de version
 - Changement du formalisme d'écriture des ELT du modèle 'ELT_cpts' à partir de 'ELT dec':
    - les attributs (var,param,...) sont déclarés dans le corps de la classe (et non plus dans __init__) --> permettra l'introspection
    - permet l'héritage
    - ...
    

SK22.0.0 - 2014-03-08 
***********************
- reimplementation de EnergyBalance en tant que process externe mais selon le formalisme 'ELT dec'
    (var, param, elt,eltOut) declarés dans la definition de classe
        version         cpython2.7      pypy
        ELT dec             112.27          57.63
                                111.97           56.64
                                111.94           57.43
    --> le formalisme 'ELT dec':
        - est comparable à mdlELT en python2.7 et semble légèrement plus rapide sous Pypy
        - prive  de la possibilté de compiler avec Shedskin
        - permet une introspection du modèle, l'heritage et la definition de class abstraites
        - est clair
        - rajoute la notion de container '_'
    
- reimplementation de EnergyBalance en tant que process externe mais selon l'ancien formalisme 'mdlELT'
        version         cpython2.7      pypy
        mdlELT             111.87          56.46
                                110.54          58.13
                                112.32          57.62
                                111.97          58.26
    -->  le formalisme 'ELT_nw' 
        - ne fait pas gagner de performances 
        - prive  de la possibilté de compiler avec Shedskin
        - mais permet l'introspection du modèle
    
SK21.0.0 - 2014-03-05 
***********************
- modification profonde du bilan d'energie de treeStand:
    - selon le formalisme ELT_nw introduit dans SK 20.1.3
    - sans iteration pour treeStand --> tout est evalué en debut d'initialisation horaire

--> si le formalisme se retrouve etre plus clair les temps sont peu modifiés
        version         cpython2.7      pypy
        SK20.1.2        112.23          57.28
        SK21.0.0        113.92          57.70
    


SK20.1.3 - 2014-03-04 
***********************
- tentative de reformalisation de l'ecriture des composants du modele avec une nouvelle implémentation 
    de ELT (ELT_new pour le moment) incorporant les paramètres dans l'appel à mise à jour (up).
    Le but est une substitution a terme de l'ancien formalisme
    - Treestand externalisation :
        stomatalConductance
        assimilation

SK20.1.2 - 2014-02-18 
***********************
-TreeStand:
    -Correction d'un bug dans la gestion annuelle des cohortes. Le fait de retirer une cohorte dans la meme boucle que la mise a jour annuelle de son WeightMax entrainé l'oubli d'une cohorte.
    --> gestion successive des deux taches.
    -Les nouvelles cohortes sont désormais insérées en tete de liste (plus lisible) 
    
- reecriture du module  BRAY pour couvrir ce que permettait le module BRAY_validation (commencer une simulation une année donnée.
    - La structure du peuplement est déduite des paramètres de la précédente intervention sylvicole
    
SK20.1.1 - 2014-01-08 : fixe modification before a big modification of photosynthesys approach ...
*****************************************************************************************************
- en cours: test des parametres hydrauliques du sol pour se rapprocher de la réponse du Bray
    - rapprochement de w_FC et w_SAT --> pour augmenter la dynamique de la nappe
    - diminution absolue de w_Fc et w_Sat pour ne pas simuler des contenus en eau trop important (/ceux mesurés)
    - augmentation du drainage si la nappe est en surface (= ruisselement)
    
- in case of an error generate by inadapted meteorological data format, repport the file line number.

SK20.1 - 2013-11-25 : version used for AGU 2013-12 simulations
***************************************************************
-correct the bug of the number of trees after the first thinning in the LowIntensity Practices set in Fast_Manager : 30 --> 830


SK20 - 2013-11-25
*******************
2013-11-22 :
    - FAST_Manager : new sylvicultural scenarii defined by Denis
    - FAST: 
        - take into account of sylvicultural scenarii to initialised treeStand structure and fertility effect via kLUE_N
        - k_wRES : specification of a residual water content ajusted to the other soil water content properties
    - BRAY_Manager : decrease the impact of 'Rouleau_Landais' on soil carbon affected
    - Forest : 
        - partitionnement plus fin de la part du rayonnement reflechi redistribué dans RsUp et RsDif en fonction de la part de RsUp_Int et d'une proportion de 75% repartant dans la direction d'ou vient le rayonnement.
        - ajout de la variable Abedo instantané
    -
2013-11-21 :
    - Soil : now soil has a deph to avoid waterground to shut down very low  when drainage is high
    - FAST : take into account the new soil parameterisation need


SK19.1 - 2013-09-12
*******************
Understorey: annual minimal seeding to autorize new understorey layer development after its death

SK19 - 2013-09-11
*******************
- Soil: correction de la fonction d'évaluation des flux d'eau du sol du fait d'abberrations aux conditions limites
- Tree : encore une nouvelle formulation de la biomasseMax de la cohorte n+1


SK18.1 - 2013-07-10
*******************
Reparamétrage par Denis de certaines propriétés du sol  pour FAST (RothC,...)

SK18 - 2013-07-10
*******************
Fusion of the forks versions (SK15 -> SK15-1 -> SK15 -> SK15-3) with (SK15 -> SK16 -> SK17)

##########################################################################################################################################################

SK17 - 2013-06-6
*****************
Reintegration of introspection capacity of the model, by the module mdlCpt_PY.py only load with python execution.
 

SK16 - 2013-06-6
*****************
CHANGES:
- leaf water potential control of stomata --> :
    -Soil: Add RootLayerWaterPotentiel by a van Genuchten approach
    -TreeStand and underStorey : 
        - estimate the leaf water potential by a simple RC model of soil-plant hydraulic, with empiric estimation of the composantes:
            - decomposition of R in RsoilToRoots and Rxyleme 
                - RsoilToRoots is a function of soil water potential
                - Rxylem is function of trees size
            - C capacitance is function of tree biomass
        - isolate the stomatal conductance estimation in a function (_EstimateStomatalConductance)
        - The ponderation af Gsmax by soil moisture deficit and hydraulic height are replaced by one depending of leaf water potential

USES :
- simulation of sensibility of minimum leaf water potential for ACCAF meeting on tree hydraulic vulnerability (Barsac, 10/06/2013)


##########################################################################################################################################################

SK15-3 - 2013-06-25
*******************
CHANGES:
- Tree : new allocation scheme to the futur needle cohort. Now it is a fraction of dWa and not, as before, allometric linked to Wa and Age.
  --> more coherent principe that show a more important effect of the 'year effect'.
- Understorey. The carbonPool is now shared between compartments. Necessary to avoid aberrant simulations (ex: no leaf growth despit big Cpool on perennial compartment, ...)
- Soil, RothC: dage affect the decomposition flux and not the decomposition constantes to be coherent with the excel sheet of Denis use to paramaterized RothC.
- LANDAIS_Manager : new approach of 'do_rouleau_Landais' : it is now define by an objective of understorey resulting biomass and no more by a decrease ratio of the existing biomass (to avoid derive of managed understorey)

 
DEBUG:
- Tree : change of the allometric function for RootSenescence to avoid to have more senescence than root biomass in the case of very smal root system.
- Understorey.ugPerennial : correct a syntax error on the the parameter k_MortalityDoyRate. --> now take into account.
- TreeStand: correction of the formulation of LeafFall


UPDATE : 
- Soil: update of the RothC  parameters (from Denis evaluation)
- TreeStand: change of the parameters of the relationship between IStress and AllocRoot to have smaller range response more centered on the rate measured on field experiment (Parcell L experiment, shoot-root biomass ratio from Trichet P.).



SK15-2 - 2013-06-5
*******************
the simulate function of FAST.py is more parameterised :
- startYear : initial year of the simulation
- endYear : final year of the simulation
- outFrequency : frequence of integration output (hour:0, day:1,year:2)
- log : print or not the simulation step informations to the screen


DEBUG :
-mdlUnderStorey, _Growth() : correction de l'inversion des coefs d'allocation entre perennial et roots

##########################################################################################################################################################


SK15 - 2013-06-5
*****************
CHANGES:
-Rajout d'un modèle specifique au BRAY : paramétrage et manager cohérent avec le suivi du site atelier du Bray.
-LANDAIS_Manager : reprends une grande partie des practiques type Landais. Base des deux manager pour  BRAY et FAST
-masque les sorties ecran si FAST est compilé avec SHEDSKIN

DEBUG:
- correction of the initialisation of stand structure in FAST


SK14 - 2013-05-31
*****************
- mdlShared est différencié selon que l'on compile ou pas avec SHEDSKIN
    - --> creation du package mdlCpt definissant les types de composant  et reimportant leur definition pour introspection si ce n'est pas une compilation ShedSkin
    - creation d'un package mdlSci regroupant les fonctions scientifiques


SK13 - 2013-05-31
*****************
-FAST:
    - prise en compte du paramétrage des contenus initiaux en carbone des différents compartiments du sol en fonction du type de sol
    - simulation jusqu'en 2100
    - modification de la modalité de management 'semi_dédié' avec exportation des couronnes lors des dernières éclaircies et de la souche lors de la coupe rase.
-Model:
    - UnderStorey: relèvement de la valeur de LAI où les calculs liés à la surface foliaire sont ignorés, pour éviter des erreurs liées à des approximations numérique lors de l'utilisation de exp() pour de tré trés faible valeurs : 0 --> 0.001




SK Versions : SK-1 to SK-11
***************************
Recodage of many technical parts to allow the use of the model with SHEDSKIN to make an compilated program.
No change in the biological model.

Introspection capacity are lossed.

compilation methodology example (in place of python FAST.py):
    shedskin -e FAST
    sudo make
    FAST

'''


