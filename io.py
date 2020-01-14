import os

class FileIO(object):
    def __init__(self,
            demFile=None,
            precipFolder=None,
            evapFolder=None,
        ):
        self.demFile= demFile
        self.precipFolder= precipFolder
        self.evapFolder= evapFolder

    def returnTimePeriod(self):
        pass

    def readPattern(self):
        pass

    def yieldForcing(self):
        pass

    def writeArray(self):
        pass
