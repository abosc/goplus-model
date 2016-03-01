from ..goBases.goELT import *
 
'''set of functions for model introspection
'''

def structure(elt, baseName = ''):
    retSTR = ''
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, eltIn):
            longName = baseName + '.' + name
            retSTR += '%s\n' % longName
            retSTR += structure(getattr(elt, name), longName)
    
    return retSTR

def variables(elt, baseName = ''):
    'all variables of an object ELT'
    retSTR = ''
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, var):
            longName = baseName + '.' + name
            retSTR += "%s = %s #%s\n" % (longName, getattr(elt, name), attrDef.doc)
        if isinstance(attrDef, eltIn):
            longName = baseName + '.' + name
            retSTR += variables(getattr(elt, name), longName)
    
    return retSTR


def varsPath(elt, baseName = ''):
    'all variables path string of an object ELT'
    ret = []
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, var):
            ret += ['%s.%s' % (baseName, name)]
        if isinstance(attrDef, eltIn):
            ret += varsPath(getattr(elt, name), '%s.%s' % (baseName, name))
    
    return ret

def parameters(elt, baseName = ''):
    'all parameters of an object ELT'
    retSTR = ''
    for name, attrDef in  elt.__cptDefs__(): 
        if isinstance(attrDef, param):
            longName = baseName + '.' + name
            retSTR += "%s = %s #%s\n" % (longName, getattr(elt, name), attrDef.doc)
        if isinstance(attrDef, eltIn) or isinstance(attrDef, pcs):
            longName = baseName + '.' + name
            retSTR += parameters(getattr(elt, name), longName)
    
    return retSTR

def parametersReset(elt, baseName = ''):
    'all parameters of an object ELT that have a different value than the default'
    retSTR = ''
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, param):
            if attrDef.valDef != getattr(elt, name):
                longName = baseName + '.' + name
                retSTR += "%s =%s #param(%s, %s)\n" % (longName, getattr(elt, name),attrDef.doc,  attrDef.valDef)
        if isinstance(attrDef, eltIn) or isinstance(attrDef, pcs):
            longName = baseName + '.' + name
            retSTR += parametersReset(getattr(elt, name), longName)
    
    return retSTR

def variablesUnchanged(elt, baseName = ''):
    'all variables of an object ELT that have not a different value than the default'
    retSTR = ''
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, var):
            if attrDef.valDef == getattr(elt, name):
                longName = baseName + '.' + name
                retSTR += "%s = %s #%s\n" % (longName, getattr(elt, name), attrDef.doc)
        if isinstance(attrDef, eltIn):
            longName = baseName + '.' + name
            retSTR += variablesUnchanged(getattr(elt, name), longName)
    
    return retSTR



def processes(elt, baseName = ''):
    'all processes of an object ELT'
    retSTR = ''
    for name, attrDef in  elt.__cptDefs__(): 
        if isinstance(attrDef, pcs):
            longName = baseName + '.' + name
            retSTR += "%s\n" % (longName)
        if isinstance(attrDef, eltIn):
            longName = baseName + '.' + name
            retSTR += processes(getattr(elt, name), longName)
    
    return retSTR
