#!/usr/bin/python3
# number of output figures = 8
# dependencies = SG++, cpp/applyBiomech2

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperBiomech2



def main():
  action = "evaluateForces"
  basisTypes = ["modifiedBSpline", "modifiedClenshawCurtisBSpline"]
  p, forceLoad = 3, 22
  n, d = 5, 2
  
  nn = (65, 65)
  v = np.linspace(-2, 1.2, 17)
  
  LAdaptive = np.array([
      [1, 1], [2, 1], [2, 1], [3, 1], [3, 1], [3, 1], [3, 1], [4, 1],
      [4, 1], [4, 1], [1, 2], [1, 2], [1, 3], [2, 2], [2, 2], [2, 3],
      [2, 3], [2, 2], [2, 2], [2, 3], [3, 2], [3, 2], [3, 2], [3, 2],
      [3, 2], [3, 2], [3, 2], [3, 2]])
  IAdaptive = np.array([
      [1, 1], [1, 1], [3, 1], [1, 1], [3, 1], [5, 1], [7, 1], [1, 1],
      [3, 1], [15, 1], [1, 1], [1, 3], [1, 1], [1, 1], [1, 3], [1, 1],
      [1, 3], [3, 1], [3, 3], [3, 1], [1, 1], [1, 3], [3, 1], [3, 3],
      [5, 1], [5, 3], [7, 1], [7, 3]])
  
  backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
  
  for adaptive in [False, True]:
    for basisType in basisTypes:
      if adaptive:
        if basisType != "modifiedClenshawCurtisBSpline": continue
        surplusThresholdPercentT, surplusThresholdPercentB = 0.01, 0.01
        scale = 0.72
      else:
        surplusThresholdPercentT, surplusThresholdPercentB = -1, -1
        scale = 0.58
      
      XX0, XX1, XX = helper.grid.generateMeshGrid(nn)
      YYfg = helperBiomech2.applyBiomech2MeshGrid(
          action, "fullGrid", basisType, p, forceLoad, nn,
          surplusThresholdPercentT=surplusThresholdPercentT,
          surplusThresholdPercentB=surplusThresholdPercentB)
      YYsg = helperBiomech2.applyBiomech2MeshGrid(
          action, "sparseGrid", basisType, p, forceLoad, nn,
          surplusThresholdPercentT=surplusThresholdPercentT,
          surplusThresholdPercentB=surplusThresholdPercentB)
      XX0 = 10 + 140 * XX0
      
      distribution = ("clenshawCurtis"
          if "clenshawcurtis" in basisType.lower() else "uniform")
      
      if adaptive:
        curL, curI = LAdaptive, IAdaptive
      else:
        _, curL, curI = helper.grid.RegularSparse(n, d).generate()
      
      X = helper.grid.getCoordinates(curL, curI, distribution)
      X[:,0] = 10 + 140 * X[:,0]
      
      for r in range(2):
        fig = Figure.create(figsize=(3, 3), scale=scale)
        ax = fig.gca()
        
        error = np.reshape(np.abs(YYfg[:,r] - YYsg[:,r]), XX0.shape)
        error[error <= 10**v[0]] = 10**-100
        error[error >= 10**v[-1]] = 10**v[-1]
        error = np.log10(error)
        contour = ax.contourf(XX0, XX1, error, v, extend="min")
        helper.plot.removeWhiteLines(contour)
        ax.plot(*X.T, "k.", mec=backgroundColor, mew=0.8, ms=7, clip_on=False)
        
        ax.set_xlim(10, 150)
        ax.set_ylim(0, 1)
        trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
        
        if adaptive:
          ax.set_xticks([10, 45, 80, 115, 150])
          ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
          ax.set_xticklabels([r"$10^{\circ}$", "", "", "", r"$150^{\circ}$"])
          ax.set_yticklabels([r"$0$", "", "", "", r"$1$"])
          ax.text(*trafo(0.5, -0.07), r"$\elbang$", ha="center", va="top")
          ax.text(*trafo(-0.05, 0.5), r"$\act{}$".format(["T", "B"][r]),
                  ha="right", va="center")
        else:
          ax.set_xticks([10, 150])
          ax.set_yticks([0, 1])
          ax.set_xticklabels([r"$10^{\circ}$", r"$150^{\circ}$"])
          ax.set_yticklabels([r"$0$", r"$1$"])
          ax.text(*trafo(0.5, -0.05), r"$\elbang$", ha="center", va="top")
          ax.text(*trafo(-0.02, 0.5), r"$\act{}$".format(["T", "B"][r]),
                  ha="right", va="center")
        
        fig.save()
  
  
  
  fig = Figure.create(figsize=(5, 2), preamble=r"""
\usepackage{siunitx}
""")
  ax = fig.gca()
  colorBar = fig.colorbar(contour, orientation="horizontal", fraction=1,
                          extend="min", ticks=[-2, -1, 0, 1])
  colorBar.ax.set_xticklabels([
      r"$\SI{0.01}{\newton}$", r"$\SI{0.1}{\newton}$",
      r"$\SI{1}{\newton}$", r"$\SI{10}{\newton}$"])
  ax.set_axis_off()
  fig.save()
  
  
  
  fig = Figure.create(figsize=(4, 2.3), preamble=r"""
\usepackage{siunitx}
""")
  ax = fig.gca()
  colorBar = fig.colorbar(contour, orientation="horizontal", fraction=1,
                          extend="min", ticks=[-2, -1, 0, 1])
  colorBar.ax.set_xticklabels([
      r"$\SI{0.01}{\newton}$", r"$\SI{0.1}{\newton}$",
      r"$\SI{1}{\newton}$", r"$\SI{10}{\newton}$"])
  ax.set_axis_off()
  fig.save()
  
  
  
  NN = 10000
  XX = helperBiomech2.getMonteCarloPoints(NN)
  
  for adaptive in [False, True]:
    print("")
    print("Relative L^2 errors:")
    
    for p in [1, 3, 5]:
      for basisType in basisTypes + ["modifiedNotAKnotBSpline"]:
        if adaptive:
          if p != 3: continue
          if basisType != "modifiedClenshawCurtisBSpline": continue
          surplusThresholdPercentT, surplusThresholdPercentB = 0.01, 0.01
        else:
          surplusThresholdPercentT, surplusThresholdPercentB = -1, -1
        
        YYfg = helperBiomech2.applyBiomech2MonteCarlo(
            action, "fullGrid", basisType, p, forceLoad, NN)
        YYsg = helperBiomech2.applyBiomech2MonteCarlo(
            action, "sparseGrid", basisType, p, forceLoad, NN,
            surplusThresholdPercentT=surplusThresholdPercentT,
            surplusThresholdPercentB=surplusThresholdPercentB)
        error = helperBiomech2.computeRelativeL2Error(YYfg, YYsg)
        print("adaptive = {}, p = {}, basisType = {}: error = {}".format(
            adaptive, p, basisType, error))
    
    
    
    if adaptive:
      surplusThresholdPercentT, surplusThresholdPercentB = 0.01, 0.01
    else:
      surplusThresholdPercentT, surplusThresholdPercentB = -1, -1
    
    basisType, p = "modifiedClenshawCurtisBSpline", 3
    
    YYfg = helperBiomech2.applyBiomech2MonteCarlo(
        action, "fullGrid", basisType, p, forceLoad, NN)
    YYsg = helperBiomech2.applyBiomech2MonteCarlo(
        action, "sparseGrid", basisType, p, forceLoad, NN,
        surplusThresholdPercentT=surplusThresholdPercentT,
        surplusThresholdPercentB=surplusThresholdPercentB)
    
    print("")
    print("adaptive = {}, p = {}, basisType = {}:".format(
        adaptive, p, basisType))
    print("Absolute L^inf error = {}".format(
        np.amax(np.abs(YYfg - YYsg), axis=0)))
    K = np.all(np.logical_and((XX >= [0.15, 0.15]),
                              (XX <= [0.85, 0.85])), axis=1)
    print("Absolute L^inf error in sub-domain = {}".format(
        np.amax(np.abs(YYfg[K,:] - YYsg[K,:]), axis=0)))



if __name__ == "__main__":
  main()
