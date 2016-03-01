from itertools import count
from types import FunctionType

__all__ = ('ELT','ELTS', 'eltIn', 'eltOut', 'var', 'param', 'private', 'pcs')


####################################
## COMPONENTS TYPE USED TO CONSTRUCT ELT TYPE  ##
####################################

#index set to cptDef object use to order in same order as in code 
_cptDefId =count(0) 


class _cptDef(object):
    
    def __new__(cls, *args, **kvargs):
        obj = object.__new__(cls)
        obj.id = next(_cptDefId)
        return obj

    def newObjCpt(self, elt):
        ''' Return an specific component for an object instance.
            Must be overwrite for specific _cptDef subclasses
        '''
        return None


class eltIn(_cptDef):
    def __init__(self, ELTtype):
        assert ELT in ELTtype.__mro__, Exception('%s is not ELT type  and can not set as eltIn' % str(ELTtype))
        self.ELTtype = ELTtype
        self.doc = ELTtype.__doc__

    def newObjCpt(self, elt):
        return self.ELTtype(elt)


class eltOut(_cptDef):
    def __init__(self, doc):
        self.doc=doc


class num(_cptDef):
    def __init__(self, doc, valDef=None):
        self.valDef = valDef
        self.doc=doc
    
    def newObjCpt(self, elt):
        return self.valDef
    
    def __repr__(self):
        return "%s('%s', %s)"%(type(self).__name__, self.doc, self.valDef)


class var(num):
    pass


class param(num):
    pass
    
class cptUndef(_cptDef):
    pass
    
#TODO : VERIFY THE NECESSITY
class private(num): 
    pass
    

class pcs(_cptDef):
    '''pcs is used to define particular method  "process method" that are instance object specifically parameterized
    '''
    def __init__(self, pcsFunc, **kvparams):        
        self.__code__ = pcsFunc.__code__
        self.__globals__= pcsFunc.__globals__
        
        argCount = self.__code__.co_argcount 
        assert argCount >0, Exception('pcs function must have one or more argument')
        
        argNames = self.__code__.co_varnames[:argCount]
        
        #construct the defaults arguments from those inherited from pcsFunc 
        if pcsFunc.__defaults__ == None:
            self.__defaults__ = [cptUndef()]*argCount
        else:
            self.__defaults__ = [cptUndef()]*(argCount -  len(pcsFunc.__defaults__) ) + list(pcsFunc.__defaults__)
        
        #upgrade the defaults arguments from those send as key-value argument
        for name, value in kvparams.items():
            self.__defaults__[argNames.index(name)] = value



    def newObjCpt(self, elt):
        
        argNames = self.__code__.co_varnames[:self.__code__.co_argcount]
        argValues = [elt] 

        wfunc = FunctionType(self.__code__, self.__globals__)

        class Process(object):
            __call__ = staticmethod(wfunc)

            def __setattr__(s, name, value):
                argValues[argNames.index(name)] = value
                wfunc.__defaults__ = tuple(argValues)
            
            def __getattr__(s, name):
                return argValues[argNames.index(name)]
            
            @classmethod
            def __cptDefs__(cls):
                cpts= {name : cpt for (name, cpt) in zip( argNames, self.__defaults__) if isinstance(cpt, _cptDef)}
                return  sorted(cpts.items(),key =lambda item:item[1].id)
            
        process = Process()
        
        argValues += [p.newObjCpt(process) for p in   self.__defaults__[1:]]
        
        wfunc.__defaults__ = tuple(argValues)        
        return process
    



####################################
## ELT TYPE ############################
####################################


class ELT(object):
    def __init__(self, container = None):
        object.__setattr__(self, 'container', container)
        
        #associate the instance components  as instance attribute
        for name, cptDef in self.__cptDefs__():
            object.__setattr__(self, name, cptDef.newObjCpt(self))

    @classmethod
    def __cptDefs__(cls):
        cpts= {}
        for base in cls.__mro__[-1::-1]:
            cpts.update( {name : cpt for (name, cpt) in base.__dict__.items() if isinstance(cpt, _cptDef)})

        return  sorted(cpts.items(),key =lambda item:item[1].id)



class ELTS(list, ELT):
    __init__ = ELT.__init__
