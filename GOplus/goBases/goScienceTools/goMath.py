'''Usual mathematic functions for model'''


#common mathematic functions imported from math module
#from math import pi, exp, log, cos, sin, tan, atan, sqrt

from math import pi,  log, cos, sin, tan, atan, sqrt, exp

#from fmath import fexp as exp


import sys
##DEBUG ##if sys.subversion[0] =='PyPy':
if 'PyPy' in sys.version:

    def max(a, b, *args):
        if a>b:
            return max(a, args[0], *args[1:]) if args else a
        else:
            return max(b, args[0], *args[1:]) if args else b

    
    def min(a, b, *args):
        if a<b:
            return min(a, args[0], *args[1:]) if args else a
        else:
            return min(b, args[0], *args[1:]) if args else b


#some other practical mathematic functions
def bound(vmin=0.0,  value =0.5,  vmax=1.0):
    if value <vmin : 
        return vmin
    elif value>vmax:
        return vmax
    else:
        return value

def Sigmoide(x=1.0, length=2.0, xref=1.0, vref=1.0):
    kp = 2 * log(1.0 / vref - 1) / length
    ks = xref + 0.5 * length
    return  1 / (1 + exp(-kp * (x - ks)))


def dSigmoide(x=1.0, length=2.0, xref=1.0, vref=1.0):
    if xref == 9999 :
        return 0
    else :
        kp = 2 * log(1.0 / vref - 1) / length
        s = Sigmoide(x, length, xref, vref)
        return  kp * s * (1 - s)

def rootsEquation2degree(a=1.0,b=2.0,c=1.0):
    """ Return the two roots of a 2nd degree polynomial equation : a*X**2 + b*X + c = 0"""
    sqrt_delta = sqrt(b**2 - 4.0*a*c)

    return (-b - sqrt_delta)/(2*a) , (-b + sqrt_delta)/(2*a)

