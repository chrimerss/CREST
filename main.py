from flow import Flow
from variable import Cell
from logs import logger
import time
from Modules.basic import _core
from Modules.route import downstream_routing
from io import FileIO


class Controler(object):
    """docstring for Controler"""
    def __init__(self, precipFolder, evapFolder, dem='test/data/dem/global_elevation.tif'):
        #----------IO-----------#
        #TODO
        self.io= FileIO(dem, precipFolder, evapFolder)
        #----------Flow---------#
        self.flow= Flow(outlet= (23,30), demFilePath= dem)
        coords= flow.coords
        self.affine= flow.affine
        X, Y= coords[:,0], coords[:,1]
        # nrows, ncols= X.shape
        self.mask= flow.basin.mask
        # logger.warning('nrows:  %d; ncols:   %d'%(nrows, ncols))
        nrows, ncols= mask.shape
        #------Assign cells-----#
        self.grids= {}
        ID=0;
        start= time.time()
        for i in range(nrows):
            for j in range(ncols):
                if self.mask[i,j]>0:
                    x,y = self.affine*(i,j)
                    print(x, y)
                    cell= Cell(i,j,x,y)

                    _dem= self.flow.dem[i,j]
                    _area= self/flow.cellArea[i,j]
                    # _dist= flow.dist[i,j]
                    _dir= self.flow.dir[i,j]
                    _slope= self.flow.slope[i,j]
                    _stream= self.flow.stream[i,j]
                    cell.update({
                        'dem': _dem,
                        'area': _area,
                        # 'dist': _dist,
                        'dir': _dir,
                        'slope': _slope,
                        'stream': _stream,
                        }, 'flow')
                    nextIndices= self.flow.flowToCell(cell)
                    cell.nextCell= nextIndices
                    _speed= self.flow.flowSpeed(cell)
                    _time= self.flow.flowTime(cell)
                    cell.update({
                        'speed': _speed,
                        'time': _time,
                        })
                    # print(cell)
                    self.grids[str(ID)]= cell
                    ID+=1
        end= time.time()
        logger.warning('initialize costs %.2f minutes!'%((end-start)/60.))

    def main():


    def step():



def main():

def step(grids, t):
    '''
    Update cell values based on the timestamp
    Args:
    -------------------------
    '''
    logger.warning('processing timestamp: %s'%str(t))




def thread(cell):
    _core()


if __name__=='__main__':
    main()
