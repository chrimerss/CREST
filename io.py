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

    def create_flow_dir(self, dst):
        os.system('gdaldem aspect -trigonometric %s %s'%(self.demFile, dst))

    def create_slope(self, dst):
        os.system('gdaldem slope %s %s'%(self.demFile, dst))
