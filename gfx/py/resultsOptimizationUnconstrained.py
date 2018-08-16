#!/usr/bin/python3
# number of output figures = 1
# dependencies = cpp/optimizeUnconstrained

import functools
import itertools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.hpc
import helper.plot



@helper.hpc.cacheToFile
@helper.hpc.executeRemotely
def optimizeUnconstrained(fStr, d, gridType, gridGenerationType,
                          N, p, gamma, seed):
  import json
  import os
  import subprocess
  
  program = os.path.join(
      os.environ["BUILD_DIR"], "..", "cpp", "optimizeUnconstrained")
  args = [program, "f={}".format(fStr), "d={}".format(d),
          "grid={}".format(gridType), "gridGen={}".format(gridGenerationType),
          "N={}".format(N), "p={}".format(p), "gamma={}".format(gamma),
          "seed={}".format(seed)]
  process = subprocess.run(
      args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
  result = json.loads(process.stdout.decode())
  
  return result

def processParameterCombination(p, gamma, grid, gridGen, parameterCombination):
  (fStr, d, color), N, seed = parameterCombination
  return optimizeUnconstrained(fStr, d, grid, gridGen, N, p, gamma, seed)

def main():
  p = 3
  gamma = 0.85
  gridGen = "ritterNovak"
  grid = "modifiedNotAKnotBSpline"
  
  NMin = 64
  NMax = 20000
  initialSeed = 342
  numberOfRepeats = 5
  fss = [
    [("branin02", 2, "C0"), ("goldsteinPrice", 2, "C1"),
     ("schwefel06", 2, "C2")],
    [("ackley", 2, "C3"), ("alpine02", 2, "C4"),
     ("schwefel22", 2, "C5")],
    [("ackley", 3, "C3"), ("alpine02", 3, "C4"),
     ("schwefel22", 3, "C5")],
    [("ackley", 4, "C3"), ("alpine02", 4, "C4"),
     ("schwefel22", 4, "C5")],
    [("ackley", 6, "C3"), ("alpine02", 6, "C4"),
     ("schwefel22", 6, "C5")],
    [("ackley", 8, "C3"), ("alpine02", 8, "C4"),
     ("schwefel22", 8, "C5")],
  ]
  lineStyles = [".-", "^--", "v:"]
  
  Ns = [int(x) for x in 2**np.arange(np.log2(NMin), np.log2(NMax))]
  seeds = list(range(initialSeed, initialSeed + numberOfRepeats))
  
  parameterCombinations = [
    list(itertools.product(fs, Ns, seeds)) for fs in fss]
  parameterCombinations = [y for x in parameterCombinations for y in x]
  print(parameterCombinations)
  
  #results = [processParameterCombination(
  #    p, gamma, grid, gridGen, parameterCombination)
  #    for parameterCombination in parameterCombinations]
  
  with multiprocessing.Pool() as pool:
    results = pool.map(functools.partial(
        processParameterCombination, p, gamma, grid, gridGen),
        parameterCombinations)
  
  
  
  for fs in fss:
    fig = Figure.create(figsize=(3.1, 2.5))
    ax = fig.gca()
    
    j = 0
    
    for fStr, d, color in fs:
      values = []
      
      for N in Ns:
        curValues = [[], [], []]
        
        for seed in seeds:
          fxOpt = results[j]["realOptimum"]["fxOpt"]
          curValues[0].append(results[j]["smoothInterpolant"]["fxOpt"] - fxOpt)
          curValues[1].append(results[j]["linearInterpolant"]["fxOpt"] - fxOpt)
          curValues[2].append(results[j]["objectiveFunction"]["fxOpt"] - fxOpt)
          j += 1
        
        curValues = [np.mean(x) for x in curValues]
        values.append(curValues)
      
      x = Ns
      ys = list(zip(*values))
      
      for y, lineStyle in zip(ys, lineStyles):
        markerSize = (4.5 if lineStyle[0] == "." else 2.5)
        ax.plot(x, y, lineStyle, color=color, ms=markerSize)
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    
    ax.set_ylim(5e-12, 1e1)
    
    ax.set_ylabel(r"$\objfun(\xoptappr) - \objfun(\xopt)$")
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.68, -0.05), r"$\ngpMax$", ha="center", va="top")
    ax.text(*trafo(0.05, 0.05), "$d = {}$".format(d))
    
    fig.save()



if __name__ == "__main__":
  main()
