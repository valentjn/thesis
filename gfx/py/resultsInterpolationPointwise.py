#!/usr/bin/python3
# number of output figures = 4
# dependencies = SG++

import matplotlib as mpl
import numpy as np

import pysgpp

from helper.figure import Figure
import helper.grid
import helper.plot

import helperInterpolation




gridStrs = ["bSpline", "notAKnotBSpline", "modifiedBSpline"]
fStr = "goldsteinPrice"
n, d, b = 7, 2, 0
p = 3

v = np.linspace(-8, 1, 16)

for gridStr in gridStrs:
  fig = Figure.create(figsize=(2.25, 2.25))
  ax = fig.gca()
  
  f = helper.function.SGppTestFunction(fStr, d)
  aX = helperInterpolation.getSurplusesRegularSparseGrid(
      gridStr, fStr, n, d, b, p)
  sgppGrid = helperInterpolation.getRegularSparseGrid(gridStr, n, d, b, p)
  X, L, I = sgppGrid.getPoints()
  interpolant = helper.function.SGppInterpolant(sgppGrid.grid, None, aX=aX)
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((65, 65))
  fXX = f.evaluate(XX)
  fsXX = interpolant.evaluate(XX)
  
  error = np.reshape(np.abs(fXX - fsXX), XX0.shape)
  error[error <= 10**v[0]] = 10**-100
  error = np.log10(error)
  contour = ax.contourf(XX0, XX1, error, v, extend="min")
  #ax.plot(X[:,0], X[:,1], "k.", clip_on=False)
  
  helper.plot.removeWhiteLines(contour)
  
  ax.set_aspect("equal")
  ax.set_xlim(0, 1)
  ax.set_ylim(0, 1)
  ax.set_xticks([0, 1])
  ax.set_yticks([0, 1])
  
  ax.text(0.5, -0.05, "$x_1$", ha="center", va="top")
  ax.text(-0.03, 0.5, "$x_2$", ha="right", va="center")
  
  fig.save()



fig = Figure.create(figsize=(5, 2))
ax = fig.gca()
fig.colorbar(contour, orientation="horizontal", fraction=1, extend="min",
             ticks=np.arange(v[0], v[-1]+0.01, 1), format="$10^{%u}$")
ax.set_axis_off()
fig.save()
