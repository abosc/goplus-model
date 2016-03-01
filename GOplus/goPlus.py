#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Entry point of GO+ used as main script'''

#verify that the file is used as main script
if __name__ != '__main__' : raise Exception('This file must be run as main script')
    
#Add the base path of GO+ to import GO+ package
import sys
import importlib
import os

package_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.dirname(package_path))
go = importlib.import_module(os.path.basename(package_path))

del sys, importlib,  os,  package_path


#Welcome message
print("** That's GO+ne ! **")
