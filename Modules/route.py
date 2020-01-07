
def continuousLR(i,j,toRowA, toColA, toPerB, nextR,
                nextC, mask, gridArea, runoff, nrows, ncols,
                noValues, Roff_tmp):
    '''
    Dynamic programming to determine the accumulated runoff
    '''
    iii= nextR(j,i)
    jjj= nextC(j,i)

    if not (_isinbasin(iii, jjj, ncros, ncols) or
            iii!= toRowA[j,i] or jjj!= toColA[j,i]):
        return runoff

    else:
        runoff[jjj,iii]+= Roff_tmp/gridArea[jjj,iii]
        return continuousLR(iii,jjj, toColA, toPerB,
            nextR, nextC, mask, gridArea, runoff, nrows,
            ncols, noValues, Roff_tmp)
