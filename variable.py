import pandas as pd
import numpy as np
from flow import Flow


class Forcing(object):
    def __init__(self):
        self.forcing= {
            'P': 10.0,
            'PET': 0.2
        }

    def __str__(self):
        return str(['%s: %.4f'%(key, value) for key, value in self.forcing.items()])


class Fluxes(object):
    def __init__(self, module='basic'):
        if module=='basic':
            self.init_basic_fluxes()

    def __str__(self):
        return str(['%s: %.4f'%(key, value) for key, value in self.fluxes.items()])

    @property
    def df(self):
        self._df= pd.DataFrame(self.fluxes)
        return self._df

    def init_basic_fluxes(self):
        self.fluxes= {
            'runoff' : 0.0,
        }

class States(object):
    def __init__(self, module='basic'):
        if module=='basic':
            self.init_basic_states()

    def __str__(self):
        return str(['%s: %.4f'%(key, value) for key, value in self.states.items()])

    @property
    def df(self):
        self._df= pd.DataFrame(self.states)
        return self._df

    def init_basic_states(self):
        self.states= {
            'W0' : 0.0,
            'SI0' : 0.0,
            'SS0' : 0.0,
        }


class Parameters(object):
    def __init__(self, module='basic'):
        if module=='basic':
            self.init_basic_params()

    def __str__(self):
        if self.params is None:
            raise ValueError('not initialize parameters')
        else:
            return str(['%s: %.4f'%(key, value) for key, value in self.params.items()])

    def init_basic_params(self):
        self.params= {
            'RainFact': 0.5,
            'Ksat'    : 0.1,
            'WM'      : 0.6,
            'B'       : 0.4,
            'IM'      : 0.6,
            'KE'      : 0.1,
            'coeM'    : 0.1,
            'expM'    : 0.1,
            'coeR'    : 0.1,
            'coeS'    : 0.1,
            'KS'      : 0.9,
            'KI'      : 0.8,
        }
specs= (
        'params', Dict,
        'forcing', Dict,
        'row', int,
        'col', int,
        'states', Dict,
        'fluxes',Dict
    )

class Cell(States, Fluxes, Parameters, Forcing):
    def __init__(self, i, j,lon,lat,area=1):
        super(Cell, self).__init__()
        Parameters.__init__(self)
        States.__init__(self)
        Fluxes.__init__(self)
        Forcing.__init__(self)
        self.row= i
        self.col= j
        self.lon= lon
        self.lat= lat
        self._area= area

    def __str__(self):
        return 'row: %d; col: %d\nForcing: %s\nParameters: %s\nFluxes: %s\nStates: %s'%(
            self.row, self.col, self.forcing, self.params, self.fluxes, self.states)

    def update(self, kwargs, type='states'):
        if type=='states':
            self.states.update(kwargs)
        elif type=='fluxes':
            self.fluxes.update(kwargs)

    @property
    def area(self):
        return self._area

    @nextCellI.setter
    def nextCellI(self, I):
        self.nextCellI= I

    @property
    def nextCellI(self):
        return self._nextCellI

    @nextCellS.setter
    def nextCellS(self, S):
        self.nextCellS= S

    @property
    def nextCellS(self):
        return self._nextCellS





