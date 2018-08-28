#!/usr/bin/python3
# number of output figures = 3
# dependencies = cpp/optimizeFuzzy

import functools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperFuzzy



def processParameterCombination(
    gridType, p, gamma, m, inputIndex, parameterCombination):
  (fStr, d, color), gridGenerationType, N, n, seed = parameterCombination
  if (N == 0) and (n == 0): gridGenerationType = "exact"
  return helperFuzzy.optimizeFuzzy(
      fStr, d, gridType, gridGenerationType,
      N, p, gamma, n, m, inputIndex, seed)



def main():
  gridType = "modifiedNotAKnotBSpline"
  p = 3
  gamma = 0.9
  m = 100
  inputIndex = 0
  
  NMin = 64
  NMax = 20000
  fss = [
    #[("branin02", 2, "C0"), ("goldsteinPrice", 2, "C1"),
    # ("schwefel06", 2, "C2"), ("ackley", 2, "C3"),
    # ("alpine02", 2, "C4"), ("schwefel22", 2, "C5")],
    [("ackley", 3, "C3"), ("alpine02", 3, "C4"),
     ("schwefel22", 3, "C5")],
    [("ackley", 4, "C3"), ("alpine02", 4, "C4"),
     ("schwefel22", 4, "C5")],
    [("ackley", 6, "C3"), ("alpine02", 6, "C4"),
     ("schwefel22", 6, "C5")],
  ]
  lineStyles = [".-", "^--"]
  seeds = [1]
  
  Ns = [0] + [int(x) for x in 2**np.arange(np.log2(NMin), np.log2(NMax))]
  parameterCombinationsAdaptive = [[fTuple, "ritterNovak", N, 0, seed]
                                   for fs in fss
                                   for fTuple in fs
                                   for N in Ns
                                   for seed in seeds]
  
  ds = set([d for fs in fss for _, d, _ in fs])
  nMaxs = {d : helperFuzzy.getMaximalRegularLevel(d, gridType, NMax)
           for d in ds}
  parameterCombinationsRegular = [[fTuple, "regular", 0, n, seed]
      for fs in fss
      for fTuple in fs
      for n in ([0] + list(range(1, nMaxs[fTuple[1]]+1)))
      for seed in seeds]
  
  parameterCombinations = (parameterCombinationsAdaptive +
                           parameterCombinationsRegular)
  print(parameterCombinations)
  
  with multiprocessing.Pool() as pool:
    results = pool.map(functools.partial(
        processParameterCombination,
        gridType, p, gamma, m, inputIndex),
        parameterCombinations)
  
  resultsAdaptive = results[:len(parameterCombinationsAdaptive)]
  resultsRegular  = results[len(parameterCombinationsAdaptive):]
  
  
  
  j, k = 0, 0
  
  for q, fs in enumerate(fss):
    figsize = ((2.25, 2.45) if q == 0 else (2.23, 2.45))
    fig = Figure.create(figsize=figsize)
    ax = fig.gca()
    
    yAll = np.array([])
    
    for fStr, d, colorAdaptive in fs:
      valuesAdaptive, valuesRegular = [], []
      colorRegular = helper.plot.mixColors(
          colorAdaptive, 0.5, helper.plot.mixColors("mittelblau", 0.1))
      xDataExacts, alphaDataExacts = {}, {}
      
      nMax = nMaxs[d]
      ns = [0] + list(range(1, nMax+1))
      
      for n in ns:
        curValues = [[], []]
        
        for seed in seeds:
          if n == 0:
            xDataExacts[seed]     = (
                resultsRegular[k]["objectiveFunction"]["yFuzzyXData"])
            alphaDataExacts[seed] = (
                resultsRegular[k]["objectiveFunction"]["yFuzzyAlphaData"])
          else:
            for i, s in enumerate(["smoothInterpolant", "linearInterpolant"]):
              xDataAppr     = resultsRegular[k][s]["yFuzzyXData"]
              alphaDataAppr = resultsRegular[k][s]["yFuzzyAlphaData"]
              error = helperFuzzy.calculateRelativeL2FuzzyError(
                  xDataExacts[seed], alphaDataExacts[seed],
                  xDataAppr, alphaDataAppr)
              curValues[i].append(error)
          
          k += 1
        
        if n > 0:
          curValues = [np.mean(x) for x in curValues]
          valuesRegular.append(curValues)
      
      xRegular = [helperFuzzy.getGridSize(d, gridType, n) for n in ns[1:]]
      ysRegular = np.array(list(zip(*valuesRegular)))
      ysRegular[ysRegular < 1e-16] = 1e-16
      print(d, fStr, xRegular, ysRegular)
      
      for yRegular, lineStyle in zip(ysRegular, lineStyles):
        markerSize = (6 if lineStyle[0] == "." else 3)
        ax.plot(xRegular, yRegular, lineStyle,
                ms=2*markerSize, mfc="none", color=colorRegular)
    
    
    
    for fStr, d, colorAdaptive in fs:
      valuesAdaptive, valuesRegular = [], []
      colorRegular = helper.plot.mixColors(colorAdaptive, 0.5)
      xDataExacts, alphaDataExacts = {}, {}
      
      for N in Ns:
        curValues = [[], []]
        
        for seed in seeds:
          if N == 0:
            xDataExacts[seed]     = (
                resultsAdaptive[j]["objectiveFunction"]["yFuzzyXData"])
            alphaDataExacts[seed] = (
                resultsAdaptive[j]["objectiveFunction"]["yFuzzyAlphaData"])
          else:
            for i, s in enumerate(["smoothInterpolant", "linearInterpolant"]):
              xDataAppr     = resultsAdaptive[j][s]["yFuzzyXData"]
              alphaDataAppr = resultsAdaptive[j][s]["yFuzzyAlphaData"]
              error = helperFuzzy.calculateRelativeL2FuzzyError(
                  xDataExacts[seed], alphaDataExacts[seed],
                  xDataAppr, alphaDataAppr)
              curValues[i].append(error)
          
          j += 1
        
        if N > 0:
          curValues = [np.mean(x) for x in curValues]
          valuesAdaptive.append(curValues)
      
      xAdaptive = Ns[1:]
      ysAdaptive = np.array(list(zip(*valuesAdaptive)))
      ysAdaptive[ysAdaptive < 1e-16] = 1e-16
      print(d, fStr, xAdaptive, ysAdaptive)
      
      for yAdaptive, lineStyle in zip(ysAdaptive, lineStyles):
        markerSize = (6 if lineStyle[0] == "." else 3)
        ax.plot(xAdaptive, yAdaptive, lineStyle,
                clip_on=((d == 3) and (fStr == "alpine02") and
                         (lineStyle == ".-")),
                ms=markerSize, color=colorAdaptive)
        yAll = np.hstack((yAll, yAdaptive))
    
    
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    
    ax.set_xticks([1e2, 1e3, 1e4])
    #x = np.hstack((xAdaptive, xRegular))
    x = xAdaptive
    ax.set_xlim(np.amin(x), np.amax(x))
    
    ax.set_ylim(max(np.amin(yAll), 1e-10), np.amax(yAll))
    ytl = ["$10^{{{}}}$".format(int(np.log10(y))) for y in ax.get_yticks()]
    ax.set_yticklabels(ytl, va="center", rotation=60)
    ax.tick_params(axis="y", pad=-5)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.71, -0.03), r"$\ngpMax$", ha="center", va="top")
    ax.text(*trafo(0.05, 1.00), r"$e^{\sparse,\ast}$")
    ax.text(*trafo(0.05, 0.04), "$d = {}$".format(d))
    
    fig.save()



if __name__ == "__main__":
  main()
