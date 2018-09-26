#!/usr/bin/python3
# number of output figures = 4
# dependencies = SG++, cpp/applyBiomech2

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperBiomech2



def main():
  action = "evaluateEquilibriumElbowAngle"
  basisType, p, forceLoads = "modifiedBSpline", 3, [22, -60, 180]
  
  nn = (129, 129)
  XX0, XX1, XX = helper.grid.generateMeshGrid(nn)
  v = np.arange(10, 151, 5)
  xt = [0, 0.25, 0.5, 0.75, 1]
  xtl = ["$0$", "", "", "", "$1$"]
  
  for forceLoad in forceLoads:
    fig = Figure.create(figsize=(3, 3), scale=0.72)
    ax = fig.gca()
    
    YY = helperBiomech2.applyBiomech2MeshGrid(
        action, "fullGrid", basisType, p, forceLoad, nn)
    contour = ax.contourf(XX0, XX1, np.reshape(YY, XX0.shape), 20,
                          vmin=10, vmax=150)
    for c in contour.collections: c.set_edgecolor("face")
    
    YYContour = np.reshape(YY, XX0.shape)
    YYContour[np.isinf(YYContour)] = (151 if forceLoad < 0 else 9)
    contour = ax.contour(XX0, XX1, YYContour, v, linewidths=3,
                         colors=[helper.plot.mixColors("mittelblau", 0.1)])
    ax.clabel(contour, fmt=r"$%u^{\circ}$")
    contour = ax.contour(XX0, XX1, YYContour, v, colors="k")
    cLabels = ax.clabel(contour, fmt=r"$%u^{\circ}$")
    
    for cLabel in cLabels:
      cLabel.set_text(r"\contour{{mittelblau!10}}{{{}}}".format(
          cLabel.get_text()))
    
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
  
  
  
  fig = Figure.create(figsize=(4, 0.75))
  ax = fig.gca()
  
  colorMap = mpl.cm.viridis
  norm = mpl.colors.Normalize(10, 150)
  xt = np.arange(10, 151, 20)
  colorBar = mpl.colorbar.ColorbarBase(
      ax, cmap=colorMap, norm=norm, ticks=xt, orientation="horizontal")
  ax.set_xticklabels([r"${:g}^{{\circ}}$".format(x) for x in xt])
  
  fig.save()



if __name__ == "__main__":
  main()
