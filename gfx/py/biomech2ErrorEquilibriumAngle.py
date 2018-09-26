#!/usr/bin/python3
# number of output figures = 4
# dependencies = SG++, cpp/applyBiomech2

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperBiomech2



def main():
  action = "evaluateEquilibriumElbowAngle"
  basisTypes = ["modifiedClenshawCurtisBSpline"]
  p, forceLoads = 3, [22, -60, 180]
  
  nn = (65, 65)
  XX0, XX1, XX = helper.grid.generateMeshGrid(nn)
  v = np.linspace(-3, 0.2, 17)
  xt = [0, 0.25, 0.5, 0.75, 1]
  xtl = ["$0$", "", "", "", "$1$"]
  
  for forceLoad in forceLoads:
    YYfg = helperBiomech2.applyBiomech2MeshGrid(
        action, "fullGrid", basisTypes[0], p, forceLoad, nn)
    
    for basisType in basisTypes:
      YYsg = helperBiomech2.applyBiomech2MeshGrid(
          action, "sparseGrid", basisType, p, forceLoad, nn)
      
      fig = Figure.create(figsize=(3, 3), scale=0.72)
      ax = fig.gca()
      
      K = np.logical_not(np.logical_or(np.isinf(YYfg), np.isinf(YYsg)))
      errorK = np.abs(YYfg[K] - YYsg[K])
      errorK[errorK <= 10**v[0]]  = 10**-100
      errorK[errorK >= 10**v[-1]] = 10**v[-1]
      error = np.full(YYfg.shape, np.nan)
      error[K] = errorK
      error = np.log10(np.reshape(error, XX0.shape))
      
      contour = ax.contourf(XX0, XX1, error, v, extend="min")
      for c in contour.collections: c.set_edgecolor("face")
      
      ax.set_xlim(0, 1)
      ax.set_ylim(0, 1)
      ax.set_xticks(xt)
      ax.set_yticks(xt)
      ax.set_xticklabels(xtl)
      ax.set_yticklabels(xtl)
      
      trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
      ax.text(*trafo(0.5, -0.07), r"$\actT$", ha="center", va="top")
      ax.text(*trafo(-0.05, 0.5), r"$\actB$", ha="right", va="center")
      
      fig.save()
  
  
  
  fig = Figure.create(figsize=(5, 2), preamble=r"""
\usepackage{siunitx}
""")
  ax = fig.gca()
  colorBar = fig.colorbar(contour, orientation="horizontal", fraction=1,
                          extend="min", ticks=[-3, -2, -1, 0])
  colorBar.ax.set_xticklabels([
      r"$0.001^{\circ}$", r"$0.01^{\circ}$",
      r"$0.1^{\circ}$", r"$1^{\circ}$"])
  ax.set_axis_off()
  fig.save()
  
  
  
  NN = 10000
  XX = helperBiomech2.getMonteCarloPoints(NN)
  
  basisTypes = [
    "modifiedBSpline",
    "modifiedClenshawCurtisBSpline",
    "modifiedNotAKnotBSpline",
  ]
  forceLoad = 22
  
  for p in [1, 3, 5]:
    for basisType in basisTypes:
      YYfg = helperBiomech2.applyBiomech2MonteCarlo(
          action, "fullGrid", basisType, p, forceLoad, NN)
      YYsg = helperBiomech2.applyBiomech2MonteCarlo(
          action, "sparseGrid", basisType, p, forceLoad, NN)
      error = helperBiomech2.computeRelativeL2Error(YYfg, YYsg)
      print("p = {}, basisType = {}: error = {}".format(p, basisType, error))
  
  
  
  basisType, p = "modifiedClenshawCurtisBSpline", 3
  
  YYfg = helperBiomech2.applyBiomech2MonteCarlo(
      action, "fullGrid", basisType, p, forceLoad, NN)
  YYsg = helperBiomech2.applyBiomech2MonteCarlo(
      action, "sparseGrid", basisType, p, forceLoad, NN)
  
  print("")
  print("p = {}, basisType = {}:".format(p, basisType))
  print("Absolute L^inf error = {}".format(
      np.amax(np.abs(YYfg - YYsg))))
  K = np.all(np.logical_and((XX >= [0.15, 0.15]),
                            (XX <= [0.85, 0.85])), axis=1)
  print("Absolute L^inf error in sub-domain = {}".format(
      np.amax(np.abs(YYfg[K] - YYsg[K]))))



if __name__ == "__main__":
  main()
