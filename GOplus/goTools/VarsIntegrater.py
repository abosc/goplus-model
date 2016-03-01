from ..goBases import *

#integration types
Mean,  Sum, Max,  Min,  Last, SumWatt , SumDay= 0, 1,  2, 3,  4, 5, 6


def IntegrateMeanVarsPaths(elt, baseName = 'mdl'):
    'all variables of an object ELT'
    retSTR = ''
    for name, attrDef in elt.__cptDefs__(): 
        if isinstance(attrDef, var):
            retSTR += "Mean: %s.%s\n" % (baseName, name)
        if isinstance(attrDef, eltIn):
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
    def __init__(self, elt, intgVarsPaths=None):
        self._count = 0
        self._elt= elt
        if intgVarsPaths is  None:
            self.intgVarsPaths = IntegrateMeanVarsPaths(elt)
        else :
            self.intgVarsPaths =intgVarsPaths
        self._variablesEvalFunc = _variablesEvalFunc(self.intgVarsPaths)
        
        self.varNames = self.intgVarsPaths.strip().replace('\n', ',')
    
    def integrate(self):
        self._count += 1
        intgVals = self._variablesEvalFunc(self._elt)
        
        if self._count == 1 :
            self._OperVIs = [list(t) for t in zip(intgVals[::2], intgVals[1::2])]
            
        else:
            try:
                for _OperVI, _V in zip(self._OperVIs, intgVals[1::2]):
                    _Oper, VI = _OperVI
                    
                    if _Oper== Mean: #up cumul for mean
                        _OperVI[1] = VI +_V
                    elif _Oper== Sum: #up cumul for sum
                        _OperVI[1] = VI +_V
                    elif _Oper==Max and _V>VI : #new max
                        _OperVI[1] =_V
                    elif _Oper==Min and _V<VI: #new min
                        _OperVI[1] =_V
                    elif _Oper==Last: #last value
                        _OperVI[1] =_V
                    elif _Oper==SumWatt: #sum of Watt (to MJ)
                        _OperVI[1] = VI +_V
                    elif _Oper==SumDay: #sum of daily evaluated var
                        _OperVI[1] = VI +_V
            except: 
                from ELTinfos import variables
                print(variables(self._elt))
                raise Exception('An error is occured during integration')

    
    def put(self):
        for _OperVI in self._OperVIs:
            _Oper, VI = _OperVI
            if _Oper == Mean:
                _OperVI[1] = VI*1.0/self._count
            elif _Oper == SumWatt: #convert a sum of Watt in MJ
                _OperVI[1] = VI*3.6E-3
            elif _Oper == SumDay: 
                _OperVI[1] = VI/24.0     
        
        self ._count = 0
        return [_OperVI[1] for _OperVI in self._OperVIs]
  
    
    def putStr(self):
        _VI = self.put()
        s=''
        for _v in _VI:
            try:
                s += '%G, ' % _v
            except:
                s += '%s, ' % _v
        return s


