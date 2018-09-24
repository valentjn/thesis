#!/usr/bin/python3
# number of output figures = 3
# dependencies = SG++, cpp/applyBiomech2

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

import helperBiomech2



def plot3DTickLabels(ax, xKwargs, yKwargs, zKwargs):
  xKwargs, yKwargs, zKwargs = dict(xKwargs), dict(yKwargs), dict(zKwargs)
  xt = xKwargs.pop("ticks")
  yt = yKwargs.pop("ticks")
  zt = zKwargs.pop("ticks")
  ax.set_xticks(xt)
  ax.set_yticks(yt)
  ax.set_zticks(zt)
  ax.set_xticklabels([])
  ax.set_yticklabels([])
  ax.set_zticklabels([])
  xl, yl, zl = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
  
  xSides = xKwargs.pop("sides", "-ll")
  xm = xKwargs.pop("margin", 0) * (yl[1] - yl[0])
  y = (yl[0]-xm if xSides[1] == "l" else yl[-1]+xm)
  z = (zl[0]    if xSides[2] == "l" else zl[-1])
  for x in xt:
    ax.text(x, y, z, "${}$".format(x), **xKwargs)
  
  ySides = yKwargs.pop("sides", "l-l")
  ym = yKwargs.pop("margin", 0) * (xl[1] - xl[0])
  x = (xl[0]-ym if ySides[0] == "l" else xl[-1]+ym)
  z = (zl[0]    if ySides[2] == "l" else zl[-1])
  for y in yt:
    ax.text(x, y, z, "${}$".format(y), **yKwargs)
  
  zSides = zKwargs.pop("sides", "lu-")
  zm = zKwargs.pop("margin", 0) * (xl[1] - xl[0])
  x = (xl[0]-zm if zSides[0] == "l" else xl[-1]+zm)
  y = (yl[0]    if zSides[1] == "l" else yl[-1])
  for z in zt:
    ax.text(x, y, z, "${}$".format(z), **zKwargs)



def main():
  action = "evaluateForces"
  basisType, p, d, forceLoad = "modifiedBSpline", 3, 2, 22
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((65, 65))
  YY = helperBiomech2.applyBiomech2(
      action, "fullGrid", basisType, p, forceLoad, XX)
  
  for q in range(2):
    curYY = 1e-3*np.reshape(YY[:,q], XX0.shape)
    
    fig = Figure.create(figsize=(3, 3), scale=0.9, preamble=r"""
\usepackage{siunitx}
""")
    ax = fig.gca(projection="3d")
    
    light = mpl.colors.LightSource(60, 45)
    faceColors = light.shade(curYY, cmap=mpl.cm.Spectral,
                             vmin=-1.1, vmax=1.1, blend_mode="soft")
    surf = ax.plot_surface(10+140*XX0, XX1, curYY, facecolors=faceColors)
    helper.plot.removeWhiteLinesInSurfPlot(surf)
    
    if q == 0:
      zl = [-0.1, 1e-3*np.amax(YY[:,q])]
      zt = [0, 0.25, 0.5, 0.75, 1]
    else:
      zl = [-0.8, 0]
      zt = [-0.75, -0.5, -0.25, 0]
    
    ax.view_init(35, -120)
    ax.set_xlim(10, 150)
    ax.set_ylim(0, 1)
    ax.set_zlim(*zl)
    xt = [10, 45, 80, 115, 150]
    yt = [0, 0.25, 0.5, 0.75, 1]
    plot3DTickLabels(ax,
      {"ticks" : xt, "sides" : "-ll", "margin" : 0.1,
       "ha" : "left",  "va" : "top"},
      {"ticks" : yt, "sides" : "l-l", "margin" : 0.1,
       "ha" : "right", "va" : "top"},
      {"ticks" : zt, "sides" : "lu-", "margin" : 0.1,
       "ha" : "right", "va" : "center"})
    ax.text(80, -0.3, zl[0], r"$\elbang$ [${}^{\circ}$]",
            ha="left", va="top")
    ax.text(-35, 0.5, zl[0], (r"$\actT$" if q == 0 else r"$\actB$"),
            ha="right", va="top")
    ax.text(10, 1, zl[1] + 0.1*(zl[1]-zl[0]),
            (r"$\forceTref$" if q == 0 else r"$\forceBref$") +
            r" [\si{\kilo\newton}]", ha="center", va="bottom")
    
    fig.save()
  
  
  
  fig = Figure.create(figsize=(1.2, 2.6), scale=0.9, preamble=r"""
\usepackage{siunitx}
""")
  ax = fig.gca()

  colorMap = mpl.cm.Spectral
  norm = mpl.colors.Normalize(-1.1, 1.1)
  yt = np.linspace(-0.75, 1, 8)
  colorBar = mpl.colorbar.ColorbarBase(
      ax, cmap=colorMap, norm=norm, boundaries=np.linspace(-0.8, 1.1, 101),
      ticks=yt)
  ax.set_yticklabels(["${:g}$".format(y) for y in yt])
  
  fig.save()



if __name__ == "__main__":
  main()
