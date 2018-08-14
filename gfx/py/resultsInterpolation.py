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
    } for lSum in range(n+1) if np.any(LSum == lSum)
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
    stats[n] = {
      order : normFcns[order](fXX - fsXX) / fNorms[order]
      for order in normFcns
    }
  
  return stats



def plotOverlapMarkers(ax, x, y, lineStyles):
  margins = [0.4, 0.6]
  
  for lineStyle in lineStyles:
    lineStyle2 = dict(lineStyle)
    lineStyle2["ms"] = (4.5 if lineStyle["ls"][0] == "." else 2.5)
    lineStyle2["ls"] = lineStyle["ls"][1:]
    ax.plot([x - margins[0], x + margins[0]], [y, y], clip_on=False,
            **lineStyle2)
    lineStyle2["marker"] = lineStyle["ls"][0]
    ax.plot([x, x], [y, y], clip_on=False, **lineStyle2)
    y *= margins[1]



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
    nMax, NMax, b = None, 20000, 0
  elif q == 1:
    functionTypes = [("ackley", 2), ("alpine02", 2), ("schwefel22", 2)]
    nMax, NMax, b = None, 20000, 0
  elif q == 2:
    functionTypes = [("ackley", 3), ("alpine02", 3), ("schwefel22", 3)]
    nMax, NMax, b = None, 50000, 0
  elif q == 3:
    functionTypes = [("ackley", 4), ("alpine02", 4), ("schwefel22", 4)]
    nMax, NMax, b = None, 50000, 0
  else:
    lineStyles = {1 : ".-", 3 : "^--", 5 : "v:"}
    gridTypes = [[
      ("bSpline", p, lineStyles[p], "C0"),
      ("notAKnotBSpline", p, lineStyles[p], "C1"),
      ("modifiedBSpline", p, lineStyles[p], "C2"),
      ("modifiedNotAKnotBSpline", p, lineStyles[p], "C3"),
      ("fundamentalSpline", p, lineStyles[p], "C4"),
      ("fundamentalNotAKnotSpline", p, lineStyles[p], "C5"),
      ("weaklyFundamentalSpline", p, lineStyles[p], "C6"),
      ("weaklyFundamentalNotAKnotSpline", p, lineStyles[p], "C7"),
    ] for p in [1, 3, 5]]
    gridTypes = [y for x in gridTypes for y in x]
    functionTypes = [("alpine02", 2)]
    nMax, NMax, b = 11, 20000, 0
  
  figsize = ((3.1, 2.6) if q < 4 else (4.3, 3.2))
  
  fig1 = Figure.create(figsize=figsize)
  ax1 = fig1.gca()
  
  fig2 = Figure.create(figsize=figsize)
  ax2 = fig2.gca()
  
  xs1, xs2 = [], []
  overlapCounter = []
  
  for gridStr, p, ls, color in gridTypes:
    for r, (fStr, d) in enumerate(functionTypes):
      currentColor = (color if color is not None else
                      "C{}".format(r+(3 if q > 0 else 0)))
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
      clipOn = (((q == 0) and (fStr == "goldsteinPrice") and (p in [3, 5])) or
                ((q == 1) and (fStr == "alpine02") and (p == 5)) or
                ((q == 4) and ("notaknot" in gridStr.lower()) and
                 ("modified" not in gridStr.lower()) and (p in [3, 5])))
      
      if q == 4:
        distances = [np.linalg.norm(np.array(np.log10(y[-5:-2])) -
            np.array(np.log10(y2[-5:-2]))) for y2, _ in overlapCounter]
        j = (np.argmin(distances) if len(distances) > 0 else None)
        
        if (j is not None) and (distances[j] < 1e-3):
          overlapCounter[j][1].append((gridStr, p))
        else:
          overlapCounter.append([y, [(gridStr, p)]])
      
      ax2.plot(x, y, ls, clip_on=clipOn, color=currentColor, ms=markerSize)
  
  if q == 4:
    import pprint
    pprint.pprint([gridStrList for _, gridStrList in overlapCounter])
  
  if q == 4:
    plotOverlapMarkers(ax2, 8.5, 6.3e-1, [
      {"ls" : gridTypes[j][2], "color" : gridTypes[j][3]}
      for j in [2, 3]
    ])
    ax2.plot([8.5, 8.5], [2.5e-1, 1.3e-2], "k-")
    
    plotOverlapMarkers(ax2, 10, 5e0, [
      {"ls" : gridTypes[j][2], "color" : gridTypes[j][3]}
      for j in [0, 1, 4, 5, 6, 7]
    ])
    ax2.plot([10, 10], [2.5e-1, 8e-4], "k-")
    
    plotOverlapMarkers(ax2, 5, 1e-5, [
      {"ls" : gridTypes[j][2], "color" : gridTypes[j][3]}
      for j in [9, 13, 15]
    ])
    ax2.plot([5.5, 8.3], [3.5e-6, 3.5e-6], "k-")
    
    plotOverlapMarkers(ax2, 5, 1e-6, [
      {"ls" : gridTypes[j][2], "color" : gridTypes[j][3]}
      for j in [17, 21, 23]
    ])
    ax2.plot([5.5, 8.0], [3.5e-7, 3.5e-7], "k-")
  
  for ax, xs in [(ax1, xs1), (ax2, xs2)]:
    x = np.array(sorted(list(set().union(*xs))))
    ax.set_xlim(x[0], x[-1] + (1 if ax == ax1 else 0))
    ax.set_yscale("log")
    
    xt = np.arange(0, 11, (1 if x[-1] - x[0] <= 6 else 2))
    xt = xt[np.logical_and((xt >= x[0]), (xt <= x[-1]))]
    ax.set_xticks(xt)
  
  ax1.set_ylabel("Mean absolute value of surpluses")
  ax2.set_ylabel("Relative $\Ltwo$ interp. error")
  
  if q == 0:
    yl = [1e-10, 5e0]
    yt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]
  elif q == 1:
    yl = [1e-10, 5e0]
    yt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]
  elif q == 2:
    yl = [1e-5, 5e0]
    yt = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0]
  elif q == 3:
    yl = [5e-3, 5e0]
    yt = [1e-2, 1e-1, 1e0]
  else:
    yl = [1e-8, 5e0]
    #yt = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0]
    yt = [1e-8, 1e-6, 1e-4, 1e-2, 1e0]
  
  ax2.set_yticks(yt)
  ax2.set_ylim(yl)
  
  if q == 0:
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-2, 2, tx=9.9, ty=2e-2)
    helper.plot.plotConvergenceLine(
        ax2, 10, 2e-8, 4, tx=7.9, ty=1e-5)
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-12, 6, tx=7.9, ty=1e-8)
  elif q == 1:
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-2, 2, tx=9.9, ty=2e-2)
    helper.plot.plotConvergenceLine(
        ax2, 10.5, 2e-8, 4, tx=8.4, ty=1e-5)
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-12, 6, tx=7.9, ty=1e-8)
  elif q == 2:
    helper.plot.plotConvergenceLine(
        ax2, 10, 7e-2, 2, tx=9, ty=4e-1)
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-5, 4, tx=9, ty=1e-4, ha="right", va="top")
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-9, 6, tx=7, ty=1e-4, ha="right", va="top")
  elif q == 3:
    helper.plot.plotConvergenceLine(
        ax2, 8, 5e-2, 1, tx=6, ty=2.5e-1)
    helper.plot.plotConvergenceLine(
        ax2, 8, 1e-4, 2, tx=3.4, ty=7e-2)
  else:
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-2, 2, tx=6.9, ty=1e0)
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-6, 4, tx=10.1, ty=1e-6)
    helper.plot.plotConvergenceLine(
        ax2, 10, 1e-12, 6, tx=5.85, ty=5e-5)
  
  if q in [0, 1]:
    if q == 0:
      yl = [1e-12, 1e4]
    elif q == 1:
      yl = [1e-10, 1e3]
    
    ax1.set_ylim(yl)
  
  if q == 0:
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e1, 2, tx=10.4, ty=1e1)
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e-5, 4, tx=10.2, ty=1e-5)
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e-9, 6, tx=10.2, ty=1e-9)
  elif q == 1:
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e-2, 2, tx=10.4, ty=1e-2)
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e-5, 4, tx=10.2, ty=1e-5)
    helper.plot.plotConvergenceLine(
        ax1, 10, 1e-10, 6, tx=9.6, ty=1e-9)
  
  functionNames = {
    "branin02"       : "Bra02",
    "goldsteinPrice" : "GoP",
    "schwefel06"     : "Sch06",
    "ackley"         : "Ack",
    "alpine02"       : "Alp02",
    "schwefel22"     : "Sch22",
  }
  
  for ax in [ax1, ax2]:
    trafo = (lambda x: ax.transData.inverted().transform(
        ax.transAxes.transform(x)))
    if q < 4: ax.text(*trafo([0.05, 0.05]), "$d = {}$".format(d))
    x = (1.03 if ax == ax1 else (1 if q in [0, 1, 4] else 0.92))
    text = (r"$\normone{l}$" if ax == ax1 else "$n$")
    ax.text(*trafo([x, -0.03]), text, ha="right", va="top")
  
  fig1.save(graphicsNumber=2*q+1)
  fig2.save(graphicsNumber=2*q+2)



def main():
  #for q in range(5): generatePlot(q)
  with multiprocessing.Pool() as pool:
    pool.map(generatePlot, range(5))



if __name__ == "__main__":
  main()
