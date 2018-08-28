#!/usr/bin/python3
# number of output figures = 2
# dependencies = cpp/optimizeConstrained

import functools
import itertools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.hpc
import helper.plot



@helper.hpc.cacheToFile
@helper.hpc.executeRemotely
def optimizeConstrained(fStr, d, gridType, gridGenerationType,
                          N, p, gamma, seed):
  import json
  import os
  import subprocess
  
  program = os.path.join(
      os.environ["BUILD_DIR"], "..", "cpp", "optimizeConstrained")
  args = [program, "f={}".format(fStr), "d={}".format(d),
          "grid={}".format(gridType), "gridGen={}".format(gridGenerationType),
          "N={}".format(N), "p={}".format(p), "gamma={}".format(gamma),
          "seed={}".format(seed)]
  process = subprocess.run(
      args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
  result = json.loads(process.stdout.decode())
  
  return result

def processParameterCombination(p, gamma, grid, gridGen, parameterCombination):
  (fStr, d, color1), N, seed = parameterCombination
  return optimizeConstrained(fStr, d, grid, gridGen, N, p, gamma, seed)

def getConstraintViolation(gx):
  return np.amax(np.clip(gx, 0, None))

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
    [("g08", 2, "C0")], [("g04Squared", 5, "C1")],
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
  
  
  
  j = 0
  
  for q, fs in enumerate(fss):
    fig = Figure.create(figsize=(3.1, 2.45))
    ax1 = fig.gca()
    ax2 = ax1.twinx()
    ax1.set_zorder(100)
    
    for fStr, d, color1 in fs:
      values1, values2 = [], []
      
      for N in Ns:
        curValues1, curValues2 = [[], [], []], [[], [], []]
        
        for seed in seeds:
          fxOpt = results[j]["realOptimum"]["fxOpt"]
          curValues1[0].append(
              results[j]["smoothInterpolant"]["fxOpt"] - fxOpt)
          curValues1[1].append(
              results[j]["linearInterpolant"]["fxOpt"] - fxOpt)
          curValues1[2].append(
              results[j]["objectiveFunction"]["fxOpt"] - fxOpt)
          curValues2[0].append(getConstraintViolation(
              results[j]["smoothInterpolant"]["gxOpt"]))
          curValues2[1].append(getConstraintViolation(
              results[j]["linearInterpolant"]["gxOpt"]))
          curValues2[2].append(getConstraintViolation(
              results[j]["objectiveFunction"]["gxOpt"]))
          j += 1
        
        curValues1 = [np.mean(x) for x in curValues1]
        values1.append(curValues1)
        
        curValues2 = [np.mean(x) for x in curValues2]
        values2.append(curValues2)
        
        #if (fStr == "g08") and (N == Ns[-1]):
        #  print(curValues1)
        #  print(curValues2)
        #  import pprint
        #  pprint.pprint(results[j-1])
      
      x = Ns
      ys1 = np.array(list(zip(*values1)))
      ys2 = np.array(list(zip(*values2)))
      ys1[ys1 < 1e-16] = 1e-16
      ys2[ys2 < 1e-16] = 1e-16
      color2 = helper.plot.mixColors(
          color1, 0.55, helper.plot.mixColors("mittelblau", 0.1))
      
      for y1, y2, lineStyle in zip(ys1, ys2, lineStyles):
        markerSize = (6 if lineStyle[0] == "." else 3)
        ax1.plot(x, y1, lineStyle, color=color1, ms=markerSize)
        ax2.plot(x, y2, lineStyle, color=color2, ms=markerSize)
    
    ax2.set_ylim(1e-1, 1e0)
    
    for ax in [ax1, ax2]:
      ax.set_xscale("log")
      ax.set_yscale("log")
      ax.spines["top"].set_visible(False)
    
    ax1.spines["left"].set_color(color1)
    ax1.spines["right"].set_visible(False)
    ax1.yaxis.label.set_color(color1)
    ax1.tick_params(axis="y", colors=color1)
    
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_color(color2)
    ax2.spines["bottom"].set_visible(False)
    ax2.yaxis.label.set_color(color2)
    ax2.tick_params(axis="y", colors=color2)
    
    if q == 0:
      ax1.set_ylim(1e-12, 2e-1)
      ax2.set_ylim(1e-17, 1e0)
    else:
      ax1.set_ylim(1e-2, 1e8)
      ax2.set_ylim(1e-17, 1e0)
    
    ax1.yaxis.labelpad = (-1 if q == 0 else 3)
    ax2.yaxis.labelpad = -1
    
    ax1.set_ylabel(r"$\objfun(\xoptappr) - \objfun(\xopt)$")
    ax2.set_ylabel(r"$\norm[\infty]{\nonnegpart{\ineqconfun(\xoptappr)}}$")
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax1)
    ax1.text(*trafo(0.68, -0.05), r"$\ngpMax$", ha="center", va="top")
    ax1.text(*trafo(0.05, 0.1), "$d = {}$".format(d))
    
    fig.save(hideSpines=False)



if __name__ == "__main__":
  main()
