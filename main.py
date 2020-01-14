import os
from flow import Flow
from variable import Cell
from logs import logger
import time
from Modules.basic import _core, make_grids, init_params
from Modules.route import downstream_routing
from io import FileIO
from multiprocessing import Pool
from functools import partial


class Controler(object):
    """docstring for Controler"""
    def __init__(self, numCores, precipFolder, evapFolder, dem='test/data/dem/global_elevation.tif'):
        '''
        initializing flow characteristics, watershed parameters
        '''
        self.numCores= numCores
        #----------IO-----------#
        #TODO
        self.io= FileIO(dem, precipFolder, evapFolder)
        self.timestep= 1 #unit according to the timestamp e.g. /h, /min, /day
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
        # self.grids= np.arange(0, self.nrows*self.ncols).reshape(self.nrows, self.ncols)
        self.grids= make_grids(self.nrows, self.ncols)
        self.grids.init_params()
        self.grids['area']= self.flow.area
        #------Routing Pretreat------#
        nextTime= self._createTimeArray()
        self.oneRowA, self.oneColA, self.onePerA, self.oneRowB, self.oneColB, self.onePerB= \
                                _routeTreat(self.nrows, self.ncols,
                                                             nextTime, self.timestep, self.flow.dir, self.mask)
        nextTime= np.divide(nextTime, self.grids['coeS'], where= self.grids['coeS']!=0)
        self.twoRowA, self.twoColA, self.twoPerA, self.twoRowB, self.twoColB, self.twoPerB= \
                                _routeTreat(self.nrows, self.ncols,
                                                             nextTime, self.timestep, self.flow.dir, self.mask)
        logger.warning('initialize costs %.2f minutes!'%((end-start)/60.))

    def main(self):
        '''
        controls the whole process including hydrologic evaluation and downstream routing
        '''
        timeStamps= self.io.returnTimePeriod()
        for i, (precip, evap) in enumerate(self.io.yieldForcing()):
            if i>1:
                break
            timestamp= timeStamps[i]
            #Update forcing for each cell
            logger.warning('Evaluating time: %s'%(timestamp))
            rows, cols= np.where(mask>0)
            args= [(precip[i,j], evap[i,j], self.grids[i,j]) for (i,j) in zip(rows, cols)]
            #-------------hydrologic model-----------#
            with Pool(self.numCores) as pool:
                results= pool.map(model, args)
            #-------------update states and fluxes-----#
            with Pool(self.numCores) as pool:
                pool.map(self.step, zip(rows, cols, results))
            print(grids[100,100])
            #-----------Routing-----------#
            self.grids= downstreamRounting(
                                        self.nrows, self.ncols, self.oneRowA, self.oneColA,
                                        self.onePerA, self.oneRowB, self.oneColB, self.onePerB,
                                        self.twoRowA, self.twoColA, self.twoPerA, self.twoRowB,
                                        self.twoColB, self.twoPerB, self.grids
                                            )



    @staticmethod
    def model(*args):
        '''shortcut for calling core module'''
        #TODO: be compatible to other modules

        return _core(*args)

    @staticmethod
    @jit(nopython=True)
    def downstreamRounting(*args):
        nrows, ncols= args[:2]
        oneRowA, oneColA, onePerA, oneRowB, oneColB, onePerB= args[2:8]
        twoRowA, twoColA, twoPerA, twoRowB, twoColB, twoPerB= args[8:14]
        grids= args[15]

        for m in range(nrows):
            for n in range(ncols):
                if mask[m,n]>0: #mask out no data
                    mm= oneRowA[m,n]
                    nn= oneColA[m,n]

                    grids['SS0'][mm,nn]+= grids['RS'][m,n]*onePerA[m,n]*\
                                        grids['area'][m,n]/grids['area'][mm,nn]
                    mm= oneRowB[m,n]
                    nn= oneColB[m,n]
                    grids['SS0'][mm,nn]+= grids['RS'][m,n]*onePerB[m,n]*\
                                        grids['area'][m,n]/grids['area'][mm,nn]

                    mm= twoRowA[m,n]
                    nn= twoColA[m,n]

                    grids['SI0'][mm,nn]+= grids['RI'][m,n]*twoPerA[m,n]*\
                                        grids['area'][m,n]/grids['area'][mm,nn]
                    mm= twoRowB[m,n]
                    nn= twoColB[m,n]
                    grids['SI0'][mm,nn]+= grids['RI'][m,n]*twoPerB[m,n]*\
                                        grids['area'][m,n]/grids['area'][mm,nn]

        return grids

    @jit(nopython=True)
    def _createTimeArray(self):
        '''create a field of travelling time for each cell as a part of flow initialization'''
        if not hasattr(self, grids):
            raise ValueError('grids not yet initialized!')
        else:
            corPairs= [(i,j,coeM, expM, coeR) for (i,j,coeM, expM, coeR) in zip(self.nrows, self.ncols,
                                                                         self.grids['coeM'], self.grids['expM'],
                                                                         self.grids['coeR'])]
            nextTime= np.vectorize(self.flow.flowTime)(corPairs).reshape(self.nrows, self.ncols)

        return nextTime

    def _step(self, i,j,results):
        '''update states and fluxes'''
        for result in results:
            self.grids[i,j][:5]= result

    def init_params(self):
        '''initialize parameters'''
        self.grids= init_params(self.grids)

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


    @staticmethod
    @jit(nopython=True)
    def _dir_matching(self, int i, int j, int fdir) -> int:
        '''compute the downstream neighboting cell accoring to the flow direction'''
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





if __name__=='__main__':
    main()
