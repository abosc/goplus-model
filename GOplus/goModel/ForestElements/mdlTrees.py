from ...goBases import *

class Trees(ELTS):
        '''A list of trees with standard dimensions'''
    
        treesCount = var('trees number', 0)
        DBHmean =  var('Mean diameter at breast height (cm)', 0.)
        DBHsd = var('Standard deviation of diameter at breast height (cm)', 0.)
        DBHquadratic = var('Quadratic mean of diameter at breast height (cm)', 0.)
        HEIGHTmean = var('Mean height (cm)', 0.)
        HEIGHTsd = var('Standard deviation of height (m)', 0.)
        

        def update(self):
            self.treesCount = treesCount = len(self)
            self.DBHmean =  sum(_tree.DBH for _tree in self) / treesCount if treesCount>0 else 0
            self.DBHsd = (sum((_tree.DBH - self.DBHmean)**2 for _tree in self) / treesCount)**0.5 if treesCount>0 else 0
            self.DBHquadratic = (sum(_tree.DBH**2 for _tree in self)/treesCount)**0.5 if treesCount>0 else 0
            self.HEIGHTmean = sum(_tree.Height for _tree in self) / treesCount if treesCount>0 else 0
            self.HEIGHTsd = (sum((_tree.Height - self.HEIGHTmean)**2 for _tree in self) / treesCount)**0.5 if treesCount>0 else 0

        def __delitem__(self, key):
            ELTS.__delitem__(self, key)
            self.update()
        
        def __setitem__(self, key, value):
            ELTS.__delitem__self.update()
        
        
