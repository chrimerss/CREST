import sys
sys.path.append('/Users/allen/Documents/Python')
from Crest.Modules.basic import _core
import numpy as np
from variable import States, Fluxes
from params import Parameters

def balance(P, E, Fluxes, States):
    return P-E+States-Fluxes

if __name__=='__main__':
    print('import ...')
    precip= 1.0
    evap= 0.2
    W0= 0.0;
    WM=50.0;
    IM= 0.2
    B= 0.0;
    Ksat= 1.0
    W= 0.0;
    ExcS= 10.0;
    ExcI= 10.0;
    print(_core(W0,precip,evap, WM, IM, B, Ksat, W, ExcS, ExcI))
