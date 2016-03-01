
class Vti:
    def __init__(self, strDef, mdl):
        #separate integration type and var path
        self.type, self.varPath =strDef.strip().split(':')
    
        self.type = self.type.strip().lower()
        if _type not in ('mean', 'sum', 'max',  'min',  'last'):
            raise Exception('Bad integration type (%s)' self.type)
        
        self.varPath = 'mdl.%s' % self.varPath.strip().split('.', 1)[1]
        
        self.obPath, self.varName = self.varPath.strip().rsplit('.', 1)
        self.obShortname = self.obPath.replace('.', '_')
        
        self.object = eval(self.obPath)
        


def Integrater(mdl, varsToIntegrate):
    
    #Extract all vars and  type of integration to do
    VTI = [Vti(strDef) for strDef in varsToIntegrate.strip().split('\n') if strDef] 
    
    
    #Extract the objects
    obj = set([vti.obPath for vti in VTI])
    

    #
    locDict={vti.obShortName: vti.object for vti in VTI}
    code =



'''
class INTEGRATER:
    def __init__(self)
    def integrate(self):
