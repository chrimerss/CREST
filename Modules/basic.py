import numpy as np
from numba import jit
import numba


@jit(nopython=True)
def _precipInt(P, RainFact):
    '''
    This function translates precipitation to effective precipitation

    Args:
    ---------------
    :P - Float; forcing precipitation data for one cell
    :RainFact - Parameter;

    Returns:
    ---------------
    :PInt - Float; translated precipitation
    '''
    return P*RainFact

@jit(nopython=True)
def _potEvap(E, EFact):
    '''
    This function converts evaporation to potential evaporation
    '''

    return E*EFact

@jit(nopython=True)
def _evapAct(W0, P, EPot, W):
    '''
    This function converts evaporation to actual evaporation

    Args:
    ----------------
    :W0 - Float; initial capacity
    :P - Float; precipitation
    :EPot - Float; Potential evaporation
    :W - Float
    '''
    if P>EPot: EAct= EPot;
    else: EAct= W0-W;

    return EAct

@jit(nopython=True)
def _runoff(
        W0, P, EPot, WM, IM,
        B, Ksat
    ):
    '''
    The runoff generation function for CREST

    Args:
    --------------
    :W0 - mm; initial capacity
    :P - mm/step; precipitation
    :EPot - mm/step; calibrated potential evaporation
    :WM - Parameter; mm maximum water depth in bucket WM
    :IM - Parameter;
    :B - Parameter;
    :Ksat - Parameter;

    Returns:
    --------------
    :W - mm; state
    :ExcS - mm; depth of infiltrated excess rain
    :ExcI - mm; depth of surface excess rain
    '''

    if P>EPot:
        #available precipitation in soil
        PSoil= (P-EPot)*(1.0-IM)
        if W0<WM:
            WMM= WM*(1.0+B)
            A= WMM*(1.0-(1.0-W0/WM)**(1.0/(1.0+B)))
            if PSoil+A>=WMM:
                R= PSoil- (WM-W0)
                W= WM
            else:
                R= PSoil-(WM-W0)+WM*(1.0-(A+PSoil)/WMM)**(1.0+B)

                if R<0: R=0.0;
                W= W0+PSoil-R

        else: #soil is full
            R= PSoil
            W= W0

        # amount of water goes to infiltration
        temX= ((W0+W)/2.0)*Ksat/WM
        if (R<=temX): ExcI= R;
        else: ExcI= temX;

        ExcS= R-ExcI+(P-EPot)*IM

        if ExcS<0: ExcS=0.0;

    else:
        ExcS= 0.0
        ExcI=0.0
        temX= (EPot-P)*W0/WM
        if temX<W0: W= W0-temX;
        else: W=0.0;

#     print(P+W0-EPot-W-ExcS-ExcI) water balanced

    return [W, ExcS, ExcI]

def _core(cell, nextCell, timestep=1, routingType='CLR'):
    '''
    this function controls all processes

    Args:
    -----------------
    :cell - Cell object that contains Parameters, Forcing, States, Fluxes
    :nextCell -Cell object
    :timestep - int;
    :routingType

    Returns:
    -----------------
    :cell - Cell object; updated by states and fluxes
    '''

    #---------Forcing data---------#
    Rain= cell.forcing['P']*timestep
    PET= cell.forcing['PET']*timestep

    #---------States---------------#
    W0= cell.states['W0']
    SI0= cell.states['SI0']
    SS0= cell.states['SS0']

    #---------Fluxes---------------#
    RS= cell.fluxes['RS']
    RI= cell.fluxes['RI']

    #---------Parameter------------#
    RainFact= cell.params['RainFact']
    KE= cell.params['KE']
    B= cell.params['B']
    KS= cell.params['KS']
    KI= cell.params['KI']
    WM= cell.params['WM']
    IM= cell.params['IM']
    Ksat= cell.params['Ksat']

    #----------Modelling------------#
    Rain= _precipInt(Rain, RainFact)
    EPot= _potEvap(PET, KE)

    W, ExcS, ExcI= _runoff(W0, Rain, EPot, WM, IM, B,
     Ksat*timestep)

    EAct= _evapAct(W0, Rain, EPot, W)

    SS0+= ExcS
    RS= SS0*KS
    SS0= SS0*(1.0-KS)

    SI0+= ExcI
    RI= SI0*KI
    SI0= SI0*(1.0-KI)

    W0= W

    runoff= ((RS+RI)/timestep)*cell.area

    states= {
    'W0': W0,
    'SI0': SI0,
    'SS0': SS0
    }
    fluxes= {
    'runoff': runoff,
    }

    cell.update(states, 'states')
    cell.update(fluxes, 'fluxes')
#     print(Rain-EAct-RI-RS-SS0-SI0-W0) water balanced
#     assert Rain-EAct-RI-RS+SS0+SI0+W0>1e-5, Rain-EAct-RI-RS+SS0+SI0+W0

    #downstream routing
    if nextCell is not None:
        SS0= nextCell.states['SS0']
        SI0= nextCell.states['SI0']

        SS0+= RS*

    return None
