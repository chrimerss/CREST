
class Parameters(Parameter):
    def __init__(self):
        super(Parameters, self).__init__()
        pass

    def __len__(self):
        return len()

    def __str__(self):
        return ''

    @property
    def df(self):
        return self._df

    @property
    def data(self):
        return self._data


class Parameter(object):
    def __init__(self, x):
        self.param= x

    def __str__(self):
        return ''
