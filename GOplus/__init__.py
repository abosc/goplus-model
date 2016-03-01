# -*- coding: utf-8 -*-
'''Entry point of GO+ package'''

__all__ = ['version', 'authors', 'Model', 'Integrater', 'infos', 'historic']


version = {'rolling': True , 'serie':'PCS', 'major' : 26, 'minor': 0, 'rev': 0, 'date' : '2016-02-29'}
authors = u'Alexandre BOSC, Denis Loustau, Delphine Picart, Virginie Moreau, Annabel Porté'

#import all core objects of GOplus
from .goModel.mdlModel import Model
from .goTools.VarsIntegrater import Integrater
from .goTools import ELTinfos as infos

# HISTORIC OF GOplus versions (newer in top)
historic = open(__file__.rsplit('/',1)[0]+'/goHistoric.txt').read()

