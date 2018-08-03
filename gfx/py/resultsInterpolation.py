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
    ("bSpline", 1, ".-", None),
    ("notAKnotBSpline", 3, "^--", None),
    ("notAKnotBSpline", 5, "v:", None),
  ]
  
  if q == 0:
    functionTypes = [("branin02", 2), ("goldsteinPrice", 2),
                     ("schwefel06", 2)]
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
      ("bSpline", 1, ".-", "C0"),
      ("modifiedBSpline", 1, ".-", "C1"),
      ("bSplineNoBoundary", 1, ".-", "C2"),
      ("bSpline", p, "^--", "C0"),
      ("notAKnotBSpline", p, "v--", "C0"),
      ("modifiedBSpline", p, "^--", "C1"),
      ("modifiedNotAKnotBSpline", p, "v--", "C1"),
      ("bSplineNoBoundary", p, "^--", "C2"),
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
      markerSize = (4.5 if ls[0] == "." else 2.5)
      
      stats = getSurplusStats(gridStr, fStr, nMax, NMax, d, b, p)
      x = sorted(list(stats.keys()))
      xs1.append(x)
      y = [stats[lSum]["mean"] for lSum in x]
      ax1.plot(x, y, ls, clip_on=False, color=currentColor, ms=markerSize)
      
      stats = getInterpolationStats(gridStr, fStr, nMax, NMax, d, b, p, NN)
      x = sorted(list(stats.keys()))
      x = [N for N in x if N > 0]
      xs2.append(x)
      y = [stats[N][2] for N in x]
      clipOn = ((fStr == "goldsteinPrice") and (p == 5))
      ax2.plot(x, y, ls, clip_on=clipOn, color=currentColor, ms=markerSize)
      print(x)
      print(y)
  
  for ax, xs in [(ax1, xs1), (ax2, xs2)]:
    x = np.array(sorted(list(set().union(*xs))))
    print(x)
    ax.set_xlim(x[0], x[-1])
    ax.set_yscale("log")
  
  ax2.set_xscale("log")
  
  ax1.set_xlabel("$N$")
  ax1.set_ylabel("Mean absolute value of surpluses")
  ax2.set_xlabel("$N$")
  ax2.set_ylabel("Relative $\Ltwo$ interp. error")
  
  if q == 0:
    yl = [1e-10, 5e0]
    yt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]
  elif q == 1:
    yl = [1e-10, 5e0]
    yt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]
  elif q == 2:
    yl = [1e-3, 1e1]
    yt = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
  elif q == 3:
    yl = [1e-2, 1e1]
    yt = [1e-2, 1e-1, 1e0, 1e1]
  elif q == 4:
    yl = [1e-5, 1e1]
    yt = [1e-5, 1e-3, 1e-1, 1e1]
  
  ax2.set_yticks(yt)
  ax2.set_ylim(yl)
  
  if q == 0:
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 1e-2, 2, tx=4e3, ty=1e-1)
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 2e-8, 4, tx=1.8e3, ty=2e-5)
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 1e-12, 6, tx=1.3e3, ty=1e-7, ha="right", va="top")
  elif q == 1:
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 1e-2, 2, tx=4e3, ty=1e-1)
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 5e-7, 4, tx=1.8e3, ty=2e-5)
    helper.plot.plotConvergenceLine(
        ax2, 1e4, 1e-12, 6, tx=1.3e3, ty=1e-7, ha="right", va="top")
  
  functionNames = {
    "branin02"       : "Bra02",
    "goldsteinPrice" : "GoP",
    "schwefel06"     : "Sch06",
    "ackley"         : "Ack",
    "alpine02"       : "Alp02",
    "schwefel22"     : "Sch22",
  }
  
  if q < 4:
    helper.plot.addCustomLegend(ax, (
      [{
        "label"  : functionNames[functionTypes[r][0]],
        "ls"     : "-",
        "color"  : "C{}".format(r),
      } for r in range(len(functionTypes))] +
      [{
        "label"  : "$p = {}$".format(x[1]),
        "marker" : {1 : ".", 3 : "^", 5 : "v"}[x[1]],
        "ms"     : (4.5 if x[1] == 1 else 2.5),
        "ls"     : x[2][1:],
        "color"  : "k",
      } for x in gridTypes]
    ), ncol=3, loc="upper center", outside=True, shift=(-0.1, 0))
  else:
    pass
  
  fig1.save(graphicsNumber=2*q+1)
  fig2.save(graphicsNumber=2*q+2)



def main():
  #for q in range(5):
  #  generatePlot(q)
  
  with multiprocessing.Pool() as pool:
    pool.map(generatePlot, range(5))



if __name__ == "__main__":
  main()
