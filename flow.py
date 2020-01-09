from pysheds.grid import Grid
import numpy as np
from vincenty import vincenty
import time
import logging
logger = logging.getLogger('CREST')

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
        logger.warning('geospatial preprocessing starts...')
        start= time.time()
        dirmap= (64,128,1,2,4,8,16,32)
        if demFilePath.endswith('.tif'):
            self.grid= Grid.from_raster(demFilePath, data_name='dem')
        elif demFilePath.endswith('.asc'):
            self.grid= Grid.from_ascii(demFilePath, data_name='dem')
        #fill depressions
        logger.warning('fill depressions...')
        self.grid.fill_depressions(data='dem', out_name='flooded_dem')
        logger.warning('done!')
        #correct flats
        # logger.warning('correct flats...')
        # self.grid.resolve_flats(data='flooded_dem', out_name='inflated_dem')
        # logger.warning('done!')
        #create flow direction
        logger.warning('create flow direction...')
        self.grid.flowdir(data='flooded_dem', out_name='dir', dirmap=dirmap)
        logger.warning('done!')
        #create slope
        logger.warning('create slope...')
        self.grid.cell_slopes('dir','dem', out_name='slope')
        logger.warning('done!')
        #compute cell area
        logger.warning('compute cell area...')
        self.grid.cell_area(out_name='area')
        logger.warning('done!')
        #compute cell distances to the nearest downstream cell
        logger.warning('compute cell distance to its downstream...')
        self.grid.cell_distances('dir',out_name='cellDist')
        logger.warning('done!')
        #create flow accumulation
        logger.warning('compute flow accumulation...')
        self.grid.accumulation(data='dir', out_name='acc', dirmap=dirmap)
        logger.warning('done!')
        #delineate catchment
        logger.warning('delineate catchment...')
        self.grid.catchment(data='dir', x=outlet[0], y= outlet[1], dirmap=dirmap,
                             out_name='basin', recursionlimit=15000, xytyple='label')
        logger.warning('done!')
        self.grid.clip_to('basin')
        #create flow distance
        # logger.warning('create flow distances...')
        # self.grid.flow_distance(data='basin', x=outlet[0], y=outlet[1], dirmap=dirmap,
        #                     out_name='dist', xytype='label')
        # logger.warning('done!')
        #extract river network
        logger.warning('extract river network...')
        self.stream= self.grid.acc.copy()
        self.stream[self.stream>100]=1
        self.stream[self.stream<=100]= 0
        logger.warning('done!')

        logger.warning('set none data to -9999.')
        self.grid.set_nodata('basin', -9999.)
        self.grid.set_nodata('acc', -9999.)
        self.grid.set_nodata('dir', -9999.)
        # self.grid.set_nodata('dist', -9999.)
        self.grid.set_nodata('area', -9999.)
        self.grid.set_nodata('cellDist', -9999.)
        self.grid.set_nodata('slope', -9999.)
        logger.warning('done!')

        end= time.time()
        logger.warning('preprocessing costs: %.2f seconds!'%(end-start))

    def flowSpeed(self, cell):
        i,j= cell.row, cell.col
        speedVegLocal= 0.5
        if not np.isnan(np.array(cell.nextCell)).any():
            if self._isinCatchment(cell.nextCell):
                speedVegNext= 0.5
            else:
                speedVegNext= speedVegLocal
        else:
            #TODO is the next speed rational?
            speedVegNext= speedVegLocal
        if cell.flow['slope']>=0:
            speed= cell.params['coeM']*((speedVegLocal+
            speedVegNext)/2.0)*cell.flow['slope']**cell.params['expM']
        else:
            speed= -9999
        if self.stream[i,j]:
            speed= speed*cell.params['coeR']

        return speed

    def flowTime(self, cell):
        speed= self.flowSpeed(cell) #in degree/unit time
        if speed>=0:
            time= self.grid.cellDist[cell.row, cell.col]/speed #unit time
        else: time=-9999.

        return time

    def flowToCell(self, cell):
        if cell.flow['dir']>=0:
            nextCellIndices= self._dir_matching(cell.row, cell.col, cell.flow['dir'])
        else:
            nextCellIndices= (np.nan, np.nan)

        return nextCellIndices



    def _dir_matching(self, i, j, fdir):
        if fdir==1:
            return (i, j-1)
        elif fdir==2:
            return (i+1, j+1)
        elif fdir==4:
            return (i+1, j)
        elif fdir==8:
            return (i+1, j-1)
        elif fdir==16:
            return (i, j-1)
        elif fdir==32:
            return (i-1, j-1)
        elif fdir==64:
            return (i-1, j)
        elif fdir==128:
            return (i-1,j+1)
        elif fdir==0:
            return (np.nan, np.nan)


    def _isinCatchment(self, indices):
        '''Justify the grid is in the extent of catchment'''
        i,j= indices
        xmin, xmax, ymin, ymax= self.grid.extent
        if self.grid.basin[i,j]>=0:
            return True
        else:
            return False

    @property
    def dem(self):
        return self.grid.dem

    @property
    def cellArea(self):
        return self.grid.area

    @property
    def acc(self):
        return self.grid.acc

    @property
    def dir(self):
        return self.grid.dir

    @property
    def slope(self):
        return self.grid.slope

    @property
    def basin(self):
        return self.grid.basin

    @property
    def dist(self):
        return self.grid.dist

    # @property
    # def stream(self):
    #     return self.grid.stream

    @property
    def mask(self):
        return self.grid.mask

    @property
    def coords(self):
        return self.grid.basin.coords

    @property
    def extent(self):
        return self.grid.basin.extent

    @property
    def cellSize(self):
        return self.grid.basin.cellSize

    @property
    def crs(self):
        return self.grid.crs

    @property
    def affine(self):
        return self.grid.affine

    @property
    def shape(self):
        return self.grid.shape







