from ..goBases import *

#integration types
Mean,  Sum, Max,  Min,  Last, SumWatt , SumDay= 0, 1,  2, 3,  4, 5, 6


def IntegrateMeanVarsPaths(elt, baseName = 'mdl'):
    'all variables of an object ELT'
    retSTR = ''
    
    for name, attrDef in elt.__cptsDef__(var): 
        retSTR += "Mean: %s.%s\n" % (baseName, name)
    for name, attrDef in elt.__cptsDef__(eltIn): 
        retSTR += IntegrateMeanVarsPaths(getattr(elt, name), "%s.%s" % (baseName, name))
    
    return retSTR


def _variablesEvalFunc (variablesPaths):
    variablesPaths = variablesPaths.strip()
    variablesPaths = variablesPaths.replace(':', ', ')
    variablesPaths = variablesPaths.replace('\n', ',\n')
    
    code= '''
def func(mdl):
    Mean,  Sum, Max,  Min,  Last, SumWatt , SumDay= 0, 1,  2, 3,  4, 5, 6
    return [%s]
    ''' % ( variablesPaths)

    loc = {}
    exec(code, {}, loc)

    return loc['func']    


class Integrater:
    def __init__(self, elt, intgVarsPaths):
        self._reset = True
        self._elt= elt
        self._variablesEvalFunc = _variablesEvalFunc(intgVarsPaths)
        
        self.varNames = intgVarsPaths.strip().replace('\n', ',')
        
    
    def integrate(self):
        intgVals = self._variablesEvalFunc(self._elt)
        if self._reset :
            self._iVrange = range(len(intgVals)//2)
            for  iV in self._iVrange:
                self._intg= [intgVals[iV*2] for iV in self._iVrange]
                self._VI = [intgVals[iV*2+1] for iV in self._iVrange]               

            self._count = 1
            self._reset = False
            
        else:
            self._count += 1
            for  iV in self._iVrange:
                _intgType= intgVals[iV*2]
                _V= intgVals[iV*2+1]           
                
                if _intgType== Mean: #up cumul for mean
                    self._VI[iV]+=_V
                elif _intgType== Sum: #up cumul for sum
                    self._VI[iV]+=_V
                elif _intgType==Max and _V>self._VI[iV] : #new max
                    self._VI[iV]=_V
                elif _intgType==Min and _V<self._VI[iV]: #new min
                    self._VI[iV]=_V
                elif _intgType==Last: #last value
                    self._VI[iV]=_V
                elif _intgType==SumWatt: #sum of Watt (to MJ)
                    self._VI[iV]+=_V
                elif _intgType==SumDay: #sum of daily evaluated var
                    self._VI[iV]+=_V
    
    def put(self):
        _VI=self._VI
        for iV in self._iVrange:
            if self._intg[iV]==Mean:
                _VI[iV]*=1.0/self._count
            elif self._intg[iV]==SumWatt: #convert a sum of Watt in MJ
                _VI[iV]*=3.6E-3
            elif self._intg[iV]==SumDay: 
                _VI[iV]/=24.0
        
        self ._reset =True
        return _VI
    
    
    def putStr(self):
        _VI=self.put()
        s=''
        for _v in _VI:
            s += '%G, ' % _v
        return s


