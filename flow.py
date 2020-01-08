from osgeo import gdal
from pysheds.grid import Grid


class Flow(object):
    def __init__(self, outlet, demFilePath=None):
        '''
        This object create grids for storing catchment features

        Args:
        ---------------------
        :outlet - (x, y); outlet point
        :demFilePath - str
        '''
        self.demFilePath= demFilePath
        print('geospatial preprocessing starts...')
        dirmap= (64,128,1,2,4,8,16,32)
        if demFilePath.endswith('.tif'):
            self.grid= Grid.from_raster(demFilePath, data_name='dem')
        elif demFilePath.endswith('.asc'):
            self.grid= Grid.from_ascii(demFilePath, data_name='dem')
        #fill depressions
        self.grid.fill_depressions(data='dem', out_name='flooded_dem')
        #correct flats
        self.grid.resolve_flats(data='flooded_dem', out_name='inlfated_dem')
        #create flow direction
        self.grid.flowdir(data='inlfated_dem', out_name='dir', dirmap=dirmap)
        #create flow accumulation
        self.grid.accumulation(data='dir', out_name='acc', dirmap=dirmap)
        #delineate catchment
        self.grid.catchment(data='dir', x=outlet[0], y= outlet[1], dirmap=dirmap,
                             out_name='catchment', recursionlimit=15000, xytyple='label')
        self.grid.clip_to('catch')
        #create flow distance
        self.grid.flow_distance(data='catchment', x=outlet[0], y=outlet[1], dirmap=dirmap,
                            out_name='dist', xytype='label')
        #extract river network
        self.grid.extract_river_network(fdir= 'catch', acc= 'acc',
                                     threshold=50, dirmap= dirmap)

        self.grid.set_nodata('catch', -9999.)
        self.grid.set_nodata('acc', -9999.)
        self.grid.set_nodata('dir', -9999.)
        self.grid.set_nodata('dist', -9999.)

    def flowSpeed(self, cell):
        speedVegLocal= 0.5
        if isinCatchment(cell.nextCell):
            speedVegNext= 0.5
        else:
            speedVegNext= speedVegLocal
        speed= cell.params['coeM']*((speedVegLocal+
            speedVegNext)/2.0)*cell.slope**cell.params['expM']
        if self.grid.

    def flowToCell(self, cell):
        pass


    @property
    def flowAcc(self):
        return self.grid.view('acc')

    @property
    def flowDir(self):
        return self.grid.view('dir')

    @property
    def catchment(self):
        return self.grid.view('catchemnt')

    @property
    def flowDist(self):
        return self.grid.view('dist')

    @property
    def flowDist(self):
        return self.grid.view('dist')

    @property
    def mask(self):
        return self.grid.mask

    @property
    def coords(self):
        return self.grid.catchment.coords

    @property
    def extent(self):
        return self.grid.catchment.extent

    @property
    def cellSize(self):
        return self.grid.catchment.cellSize

    @property
    def crs(self):
        return self.grid.crs

    @property
    def affine(self):
        return self.grid.affine

    @property
    def shape(self):
        return self.grid.shape







