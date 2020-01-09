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
        self.nrows, self.ncols= mask.shape
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
        timeStamps= self.io.returnTimePeriod()
        for i, (precip, evap) in enumerate(self.io.yieldForcing()):
            timestamp= timeStamps[i]
            #Update forcing for each cell


    def step(self):
        pass

    @staticmethod
    @jit(nopython=True)
    def updateForcing(precip, evap, gridsList):
        precip= precip.reshape(-1,1)
        evap= evap.reshape(-1,1)

    @staticmethod
    @jit(nopython=True)
    def _routeTreat(nrows, ncols, nextTime, timestep,
                     flow_dir, mask):
        '''
        This function computes two information of two consecutive cells
        :oneRowA - the row that current cell flows to within the timestep
        :oneColA - the column ...
        :onePerA - the time takes to the next cell within timestep
        :oneRowB - flows to final cell
        :oneColB - see above
        :onePerB - see above
        '''
        @jit(nopython=True)
        def _dir_matching(self, int i, int j, int fdir) -> int:
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

        toRowA= np.zeros((nrows, ncols))
        toRowA= np.zeros((nrows, ncols))
        toRowB= np.zeros((nrows, ncols))
        toColB= np.zeros((nrows, ncols))
        toPerA= = np.zeros((nrows, ncols))
        toPerB= = np.zeros((nrows, ncols))

        for i in range(nrows):
            for j in range(ncols):
                toRowA[i,j]= i
                toColA[i,j]= j
                while toPerB[i,j]<timestep:
                    toRowA[i,j]= toRowB[i,j]
                    toColA[i,j]= toColB[i,j]
                    toPerA[i,j]= toPerB[i,j]
                    if toRowA[i,j]>=0:
                        if mask[i,j]:
                            toRowB[i,j], toColB[i,j]= _dir_matching(i,j,dir[i,j])
                            toPerB[i,j]= toPerB[i,j]+ nextTime[toRowA[i,j], toColA[i,j]]
                        else:
                            toPerB[i,j]= -9999.
                            toRowB[i,j]= -9999.
                            toColB[i,j]= -9999.
                    else:
                        toPerB[i,j]= -9999.
                        toRowB[i,j]= -9999.
                        toColB[i,j]= -9999.
                toPerB[i,j]= (timestep- toPerA[i,j])/(toPerB[i,j]-toPerA[i,j])
                toPerA[i,j]= 1.0- toPerB

        return toRowA, toColA, toPerA, toRowB, toColB, toPerB


if __name__=='__main__':
    main()
