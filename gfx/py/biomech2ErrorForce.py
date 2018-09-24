#!/usr/bin/python3
# number of output figures = 5
# dependencies = SG++, cpp/applyBiomech2

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperBiomech2



def main():
  action = "evaluateForces"
  basisTypes = ["modifiedBSpline", "modifiedClenshawCurtisBSpline"]
  p, d, forceLoad = 3, 2, 22
  n = 5
  
  v = np.linspace(-2, 1.2, 17)
  
  for basisType in basisTypes:
    XX0, XX1, XX = helper.grid.generateMeshGrid((65, 65))
    YYfg = helperBiomech2.applyBiomech2(
        action, "fullGrid", basisType, p, forceLoad, XX)
    YYsg = helperBiomech2.applyBiomech2(
        action, "sparseGrid", basisType, p, forceLoad, XX)
    XX0 = 10 + 140 * XX0
    
    distribution = ("clenshawCurtis"
        if "clenshawcurtis" in basisType.lower() else "uniform")
    _, L, I = helper.grid.RegularSparse(n, d).generate()
    X = helper.grid.getCoordinates(L, I, distribution)
    X[:,0] = 10 + 140 * X[:,0]
    
    for r in range(2):
      fig = Figure.create(figsize=(3, 3), scale=0.58)
      ax = fig.gca()
      
      error = np.reshape(np.abs(YYfg[:,r] - YYsg[:,r]), XX0.shape)
      error[error <= 10**v[0]] = 10**-100
      error[error >= 10**v[-1]] = 10**v[-1]
      error = np.log10(error)
      contour = ax.contourf(XX0, XX1, error, v, extend="min")
      for c in contour.collections: c.set_edgecolor("face")
      ax.plot(*X.T, "k.", mec="w", mew=0.8, ms=7, clip_on=False)
      
      ax.set_xlim(10, 150)
      ax.set_ylim(0, 1)
      ax.set_xticks([10, 150])
      ax.set_yticks([0, 1])
      
      trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
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
  
  
  
  NN = 10000
  np.random.seed(342)
  XX = np.random.rand(NN, d)
  
  for p in [1, 3, 5]:
    for basisType in basisTypes + ["modifiedNotAKnotBSpline"]:
      YYfg = helperBiomech2.applyBiomech2(
          action, "fullGrid", basisType, p, forceLoad, XX)
      YYsg = helperBiomech2.applyBiomech2(
          action, "sparseGrid", basisType, p, forceLoad, XX)
      error = helperBiomech2.computeRelativeL2Error(YYfg, YYsg)
      print("p = {}, basisType = {}: error = {}".format(p, basisType, error))



if __name__ == "__main__":
  main()
