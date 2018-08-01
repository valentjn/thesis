#!/usr/bin/python3
# number of output figures = 10
# dependencies = SG++

import multiprocessing

import numpy as np

import pysgpp

from helper.figure import Figure
import helper.function
import helper.grid
import helper.hpc
import helper.plot

import helperInterpolation



@helper.hpc.cacheToFile
def getSurplusStats(gridStr, fStr, nMax, NMax, d, b, p):
  n = helperInterpolation.getLevelRegularSparseGrid(
      gridStr, nMax, NMax, d, b, p)
  aX = helperInterpolation.getSurplusesRegularSparseGrid(
      gridStr, fStr, n, d, b, p)
  
  sgppGrid = helperInterpolation.getRegularSparseGrid(
      gridStr, n, d, b, p)
  _, L, _ = sgppGrid.getPoints()
  #if L.shape[0] == 0: continue
  LSum = np.sum(L, axis=1)
  assert np.amax(LSum) == n
  
  stats = {lSum :
    {
      "max" :  np.max(np.abs(aX[LSum == lSum])),
      "mean" : np.mean(np.abs(aX[LSum == lSum])),
      "std" :  np.std(np.abs(aX[LSum == lSum])),
    } for lSum in range(n) if np.any(LSum == lSum)
  }
  
  return stats

@helper.hpc.cacheToFile
def getInterpolationStats(gridStr, fStr, nMax, NMax, d, b, p, NN):
  nMax2 = helperInterpolation.getLevelRegularSparseGrid(
      gridStr, nMax, NMax, d, b, p)
  np.random.seed(342)
  XX = np.random.rand(NN, d)
  
  f = helper.function.SGppTestFunction(fStr, d)
  fXX = f.evaluate(XX)
  normFcns = {
    2      : (lambda Y: np.sqrt(np.sum(Y**2) / NN)),
    np.inf : (lambda Y: np.max(np.abs(Y))),
  }
  fNorms = {order : normFcns[order](fXX) for order in normFcns}
  stats = {}
  
  for n in range(nMax2+1):
    aX = helperInterpolation.getSurplusesRegularSparseGrid(
        gridStr, fStr, n, d, b, p)
    sgppGrid = helperInterpolation.getRegularSparseGrid(
        gridStr, n, d, b, p)
    interpolant = helper.function.SGppInterpolant(sgppGrid.grid, None, aX=aX)
    fsXX = interpolant.evaluate(XX)
    stats[sgppGrid.grid.getSize()] = {
      order : normFcns[order](fXX - fsXX) / fNorms[order]
      for order in normFcns
    }
  
  return stats



def generatePlot(q):
  pysgpp.omp_set_num_threads(multiprocessing.cpu_count())
  pysgpp.OptPrinter.getInstance().setVerbosity(2)
  
  NN = 10000
  
  gridTypes = [
    ("bSpline", 1, "--", None),
    ("notAKnotBSpline", 3, "-", None),
    ("notAKnotBSpline", 5, ":", None),
  ]
  
  if q == 0:
    functionTypes = [("branin02", 2), ("eggHolder", 2), ("schwefel06", 2)]
    nMax, NMax, b = None, 10000, 0
  elif q == 1:
    functionTypes = [("ackley", 2), ("alpine02", 2), ("schwefel22", 2)]
    nMax, NMax, b = None, 10000, 0
  elif q == 2:
    functionTypes = [("ackley", 3), ("alpine02", 3), ("schwefel22", 3)]
    nMax, NMax, b = None, 20000, 0
  elif q == 3:
    functionTypes = [("ackley", 4), ("alpine02", 4), ("schwefel22", 4)]
    nMax, NMax, b = None, 20000, 0
  elif q == 4:
    p = 3
    gridTypes = [
      ("notAKnotBSpline", p, "-", "C0"),
      ("modifiedNotAKnotBSpline", p, ":", "C0"),
      ("bSpline", 1, "-", "C1"),
      ("modifiedBSpline", 1, ":", "C1"),
      ("bSplineNoBoundary", 1, "--", "C1"),
      ("bSpline", p, "-", "C2"),
      ("modifiedBSpline", p, ":", "C2"),
      ("bSplineNoBoundary", p, "--", "C2"),
    ]
    functionTypes = [("alpine02", 2)]
    nMax, NMax, b = None, 10000, 0
  
  fig1 = Figure.create(figsize=(3, 3))
  ax1 = fig1.gca()
  
  fig2 = Figure.create(figsize=(3, 3))
  ax2 = fig2.gca()
  
  xs1, xs2 = [], []
  
  for gridStr, p, ls, color in gridTypes:
    for r, (fStr, d) in enumerate(functionTypes):
      currentColor = (color if color is not None else "C{}".format(r))
      
      stats = getSurplusStats(gridStr, fStr, nMax, NMax, d, b, p)
      x = sorted(list(stats.keys()))
      xs1.append(x)
      y = [stats[lSum]["mean"] for lSum in x]
      ax1.plot(x, y, ls, clip_on=False, color=currentColor)
      
      stats = getInterpolationStats(gridStr, fStr, nMax, NMax, d, b, p, NN)
      x = sorted(list(stats.keys()))
      x = [N for N in x if N > 0]
      xs2.append(x)
      y = [stats[N][2] for N in x]
      ax2.plot(x, y, ls, clip_on=False, color=currentColor)
      print(x)
      print(y)
  
  for ax, xs in [(ax1, xs1), (ax2, xs2)]:
    x = np.array(sorted(list(set().union(*xs))))
    print(x)
    ax.set_xlim(x[0], x[-1])
    ax.set_yscale("log")
    
    #helper.plot.plotConvergenceTriangle(ax, 5.5, 1e-2, 2, -2)
    #helper.plot.plotConvergenceTriangle(ax, 5, 1e1, 2.5, -1, side="upper")
  
  ax2.set_xscale("log")
  
  fig1.save(graphicsNumber=2*q+1)
  fig2.save(graphicsNumber=2*q+2)



def main():
  #for q in range(5):
  #  generatePlot(q)
  
  with multiprocessing.Pool() as pool:
    pool.map(generatePlot, range(5))



if __name__ == "__main__":
  main()
