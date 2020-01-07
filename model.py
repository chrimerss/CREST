import numpy as np

def _core(
        float: W0, float: P, float: EPot, float: WM, float: IM,
        float: B, float: Ksat, float: W, float: ExcS, float: ExcI
    ) -> List:
    '''
    The core function for CREST at pixel-wise to update states

    Args:
    --------------
    :W0 - mm; initial capacity
    :P - mm/step; precipitation
    :EPot - mm/step; calibrated potential evaporation
    :WM - Parameter; mm maximum water depth in bucket WM
    :IM - Parameter
    :B - mm/step; inflow
    :Ksat - Parameter
    :W - mm; state
    :ExcS - mm; depth of infiltrated excess rain
    :ExcI - mm; depth of surface excess rain

    Returns:
    --------------

    '''

    if P>EPot:
        #available precipitation in soil
        PSoil= (P-EPot)*(1.0-IM)
        if W0<WM:
            WMM= WM*(1.0+B)
            A= WMM*(1.0-(1.0-W0/WM))**(1.0/(1.0+B))
            if PSoil+A>=WMM:
                R= PSoil- (WM-W0)
                W= WM
            else:
                R= PSoil-(WM-W0)+WM*(1.0-(A+PSoil)/WMM)**(1.0+B)

                if R<0: R=0;

        else: #soil is full
            R= PSoil
            W= W0

        # amount of water goes to infiltration
        temX= ((W0+W)/2.0)*Ksat/WM
        if (R<=temX): ExcI= R;
        else: ExcI= temX;


