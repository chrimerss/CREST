import numpy as np

def _core(
        float: W0, float: precip, float: EPot, float: WM, float: IM,
        float: B, float: Ksat, float: W, float: ExcS, float: ExcI
    ) -> List:
    '''
    The core function for CREST at pixel-wise to update states

    Args:
    --------------
    :W0
    :precip
    :EPot
    :WM
    :IM
    :B
    :Ksat
    :W
    :ExcS
    :ExcI

    Returns:
    --------------

    '''

    # Initialize some states
    PSoil= np.zeros(precip.shape, dtype=np.float32)
    WMM= np.zeros(WM.shape, dtype=np.float32)
    A= np.zeros(B.shape, dtype=np.float32)

    PSoil[precip>EPot]= (precip[precip>EPot]-EPot[precip>EPot])*(1.0-IM[precip>EPot])
    WMM[W0<WM]= WM[W0<WM]*(1.0+B[W0<WM])
    A[W0<WM]= WMM[W0<WM]*(1.0-
                        (1.0-
                            np.divide(W0[W0<WM],WM[W0<WM])**(1.0/(1.0+B[W0<WM])) #TODO: WM=0
                                ))


