from .flow import Flow
from .variable import Cell

def main():
    #----------IO-----------#
    dem=
    #----------Flow---------#
    flow= Flow(demFilePath)
    catchment= flow.catchment
    mask= flow.mask
    coords= flow.coords
    affine= flow.affine
    nrows, ncols= flow.shape

    #------Assign cells-----#
    grids= {}
    for i in range(nrows):
        for j in range(ncols):
            if mask[i,j]>0:
                x,y = affine*(i,j)
                cell= Cell(i,j,x,y)
                nextCellI, nextCellS= flow.flowToCell(cell)
                cell.nextCellI(nextCellI)
                cell.nextCellS(nextCellS)
                grids['(%d,%d)'%(i,j)]= cell

def thread(grids):
    pass
