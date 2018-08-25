#!/usr/bin/python3
# number of output figures = 4
# dependencies = cpp/optimizeFuzzy

import functools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperFuzzy



def processParameterCombination(
    gridType, gridGenerationType, N, p, gamma, m, inputIndex,
    parameterCombination):
  (fStr, d, color), n, seed = parameterCombination
  if n == 0: gridGenerationType = "exact"
  return helperFuzzy.optimizeFuzzy(
      fStr, d, gridType, gridGenerationType,
      N, p, gamma, n, m, inputIndex, seed)



def main():
  gridType = "modifiedNotAKnotBSpline"
  gridGenerationType = "regular"
  N = 0
  p = 3
  gamma = 0.9
  m = 100
  inputIndex = 0
  
  fss = [
    [("branin02", 2, "C0"), ("goldsteinPrice", 2, "C1"),
     ("schwefel06", 2, "C2"), ("ackley", 2, "C3"),
     ("alpine02", 2, "C4"), ("schwefel22", 2, "C5")],
    [("ackley", 3, "C3"), ("alpine02", 3, "C4"),
     ("schwefel22", 3, "C5")],
    [("ackley", 4, "C3"), ("alpine02", 4, "C4"),
     ("schwefel22", 4, "C5")],
    [("ackley", 6, "C3"), ("alpine02", 6, "C4"),
     ("schwefel22", 6, "C5")],
    #[("ackley", 8, "C3"), ("alpine02", 8, "C4"),
    # ("schwefel22", 8, "C5")],
  ]
  lineStyles = [".-", "^--", "v:"]
  NMax = 20000
  seeds = [1]
  
  ds = set([d for fs in fss for _, d, _ in fs])
  nMaxs = {d : helperFuzzy.getMaximalRegularLevel(d, gridType, NMax)
           for d in ds}
  parameterCombinations = [[fTuple, n, seed]
                           for fs in fss
                           for fTuple in fs
                           for n in range(nMaxs[fTuple[1]]+1)
                           for seed in seeds]
  print(parameterCombinations)
  
  with multiprocessing.Pool() as pool:
    results = pool.map(functools.partial(
        processParameterCombination,
        gridType, gridGenerationType, N, p, gamma, m, inputIndex),
        parameterCombinations)
  
  
  
  j = 0
  
  for q, fs in enumerate(fss):
    figsize = ((1.83, 2.5) if q == 0 else (1.76, 2.5))
    fig = Figure.create(figsize=figsize)
    ax = fig.gca()
    
    yAll = np.array([])
    
    for fStr, d, color in fs:
      values = []
      xDataExacts, alphaDataExacts = {}, {}
      nMax = nMaxs[d]
      ns = range(nMax+1)
      
      for n in ns:
        curValues = [[], []]
        
        for seed in seeds:
          if n == 0:
            xDataExacts[seed]     = (
                results[j]["objectiveFunction"]["yFuzzyXData"])
            alphaDataExacts[seed] = (
                results[j]["objectiveFunction"]["yFuzzyAlphaData"])
          else:
            for k, s in enumerate(["smoothInterpolant", "linearInterpolant"]):
              xDataAppr     = results[j][s]["yFuzzyXData"]
              alphaDataAppr = results[j][s]["yFuzzyAlphaData"]
              error = helperFuzzy.calculateRelativeL2FuzzyError(
                  xDataExacts[seed], alphaDataExacts[seed],
                  xDataAppr, alphaDataAppr)
              curValues[k].append(error)
          
          j += 1
        
        if n > 0:
          curValues = [np.mean(x) for x in curValues]
          values.append(curValues)
      
      x = ns[1:]
      ys = np.array(list(zip(*values)))
      ys[ys < 1e-16] = 1e-16
      
      for y, lineStyle in zip(ys, lineStyles):
        markerSize = (6 if lineStyle[0] == "." else 3)
        ax.plot(x, y, lineStyle, color=color, ms=markerSize, clip_on=False)
        yAll = np.hstack((yAll, y))
    
    ax.set_yscale("log")
    
    ax.set_xticks([2, 4, 6, 8, 10])
    ax.set_xlim(x[0], x[-1])
    
    ax.set_ylim(np.amin(yAll), np.amax(yAll))
    ytl = ["$10^{{{}}}$".format(int(np.log10(y))) for y in ax.get_yticks()]
    ax.set_yticklabels(ytl, va="center", rotation=60)
    ax.tick_params(axis="y", pad=-5)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.68, 0.02), "$n$", ha="center", va="bottom")
    ax.text(*trafo(0.05, 1.00), r"$e^{\sparse,\ast}$")
    ax.text(*trafo(0.05, 0.04), "$d = {}$".format(d))
    
    fig.save()



if __name__ == "__main__":
  main()
