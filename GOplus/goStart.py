#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Entry point of GO+ load as script'''


#Add the base path of GO+ to import GO+ package
import sys
import importlib
import os

package_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.dirname(package_path)) 
go=importlib.import_module(os.path.basename(package_path))

del sys, importlib,  os,  package_path


#Welcome message
if __name__=='__main__': print("** That's GO+ne ! **")
