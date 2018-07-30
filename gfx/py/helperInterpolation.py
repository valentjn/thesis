#!/usr/bin/python3
# dependencies: SG++

import helper.function
import helper.grid
import helper.hpc

import helperInterpolation



#helper.hpc.clearCacheFile()

@helper.hpc.cacheToFile
@helper.hpc.executeRemotely
def getSurplusesRegularSparseGrid(gridStr, fStr, n, d, b, p):
  import helper.function
  import helperInterpolation
  
  sgppGrid = helperInterpolation.getRegularSparseGrid(gridStr, n, d, b, p)
  X, _, _ = sgppGrid.getPoints()
  
  f = helper.function.SGppTestFunction(fStr, d)
  fX = f.evaluate(X)
  
  interpolant = helper.function.SGppInterpolant(sgppGrid.grid, fX)
  aX = interpolant.aX
  return aX

"""
import numpy as np
import helper.misc

@helper.hpc.cacheToFile
def getSurplusesRegularSparseGrid(gridStr, fStr, n, d, b, p):
  aX = getSurplusesRegularSparseGridWrongOrder(gridStr, fStr, n, d, b, p)
  aX2 = getSurplusesRegularSparseGridWrongOrder2(gridStr, fStr, n, d, b, p)
  #sgppGrid = helperInterpolation.getRegularSparseGrid(gridStr, n, d, b, p)
  #X, _, _ = sgppGrid.getPoints()
  #aX[helper.misc.argLexSortRows(X)] = aX
  #aX2[helper.misc.argLexSortRows(X)] = aX2
  print(np.max(np.abs(aX - aX2)))
  
  return aX

#@helper.hpc.executeRemotely
def getSurplusesRegularSparseGridWrongOrder(gridStr, fStr, n, d, b, p):
  import helper.function
  import helperInterpolation
  
  sgppGrid = helperInterpolation.getRegularSparseGrid(gridStr, n, d, b, p)
  X, _, _ = sgppGrid.getPoints()
  
  f = helper.function.SGppTestFunction(fStr, d)
  fX = f.evaluate(X)
  
  interpolant = helper.function.SGppInterpolant(sgppGrid.grid, fX)
  aX = interpolant.aX
  #aX = aX[helper.misc.argLexSortRows(X)]
  
  return aX

getSurplusesRegularSparseGridWrongOrder2 = helper.hpc.executeRemotely(getSurplusesRegularSparseGridWrongOrder)"""

def getRegularSparseGrid(gridStr, n, d, b, p):
  gridArgs = [d, p]
  if isBoundaryGrid(gridStr): gridArgs.append(b)
  sgppGrid = helper.grid.SGppGrid(gridStr, *gridArgs)
  n2 = max((n if isBoundaryGrid(gridStr) else n-d+1), 0)
  sgppGrid.generateRegular(n2)
  return sgppGrid

def isBoundaryGrid(gridStr):
  return ("modified" not in gridStr) and ("NoBoundary" not in gridStr)

def getLevelRegularSparseGrid(gridStr, nMax, NMax, d, b, p):
  sgppGrid, n = None, 0
  
  while True:
    newSGppGrid = getRegularSparseGrid(gridStr, n+1, d, b, p)
    if (NMax is not None) and (newSGppGrid.grid.getSize() > NMax): break
    sgppGrid, n = newSGppGrid, n + 1
    if (nMax is not None) and (n >= nMax): break
  
  return n
