#!/usr/bin/python3
# number of output figures = 1
# dependencies = cpp/optimizeUnconstrained

import functools
import itertools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.hpc



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
  (fStr, d), N, seed = parameterCombination
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
  fPairs = [("branin02", 2), ("goldsteinPrice", 2), ("schwefel06", 2)]
  lineStyles = [".-", "^--", "v:"]
  
  Ns = [int(x) for x in 2**np.arange(np.log2(NMin), np.log2(NMax))]
  seeds = list(range(initialSeed, initialSeed + numberOfRepeats))
  
  parameterCombinations = list(itertools.product(fPairs, Ns, seeds))
  print(parameterCombinations)
  
  #results = [processParameterCombination(
  #    p, gamma, grid, gridGen, parameterCombination)
  #    for parameterCombination in parameterCombinations]
  
  with multiprocessing.Pool() as pool:
    results = pool.map(functools.partial(
        processParameterCombination, p, gamma, grid, gridGen),
        parameterCombinations)
  
  
  
  fig = Figure.create(figsize=(3, 3))
  ax = fig.gca()
  
  j = 0
  
  for r, (fStr, d) in enumerate(fPairs):
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
      ax.plot(x, y, lineStyle, color="C{}".format(r))
  
  ax.set_xscale("log")
  ax.set_yscale("log")
  
  fig.save()



if __name__ == "__main__":
  main()
