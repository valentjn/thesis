#!/usr/bin/python3
# number of output figures = 8
# dependencies = SG++

import multiprocessing

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.function
import helper.grid
import helper.plot

import pysgpp



def plotUnconstrainedProblem(params):
  d = 2
  q, (fStr, xOpt, bounds, contourOnTop, contourExponent, \
      lightOrigin, cameraPosition) = params
  
  f = helper.function.SGppTestFunction(fStr, d)
  
  fig = Figure.create(figsize=(3.3, 2.9))
  ax = fig.add_subplot(111, projection="3d")
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((65, 65))
  YY = np.reshape(f.evaluate(XX), XX0.shape)
  
  XX = bounds[0] + XX * (bounds[1] - bounds[0])
  XX0, XX1 = np.reshape(XX[:,0], XX0.shape), np.reshape(XX[:,1], XX1.shape)
  
  fOpt = f.evaluate((xOpt-bounds[0])/(bounds[1]-bounds[0]))
  
  YYMin, YYMax = min(np.amin(YY), fOpt), np.amax(YY)
  if fStr == "goldsteinPrice": YYMax += 10
  v = np.linspace(0, 1, 20)
  if fStr == "eggHolder":
    v = -2*v**3 + 3*v**2
  else:
    v = v**contourExponent
  
  v = YYMin + (YYMax - YYMin) * v
  contourOffset = (YYMax if contourOnTop else YYMin)
  ax.contour(XX0, XX1, YY, v, offset=contourOffset)
  
  if lightOrigin is None: lightOrigin = (315, 45)
  light = mpl.colors.LightSource(*lightOrigin)
  faceColors = light.shade(YY, cmap=mpl.cm.viridis, blend_mode="soft")
  surface = ax.plot_surface(XX0, XX1, YY, facecolors=faceColors)
  
  backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
  
  ax.plot(2*[xOpt[0]], 2*[xOpt[1]], ".", zs=[fOpt, contourOffset],
          mec=backgroundColor, mfc="C1", ms=10, mew=1, zorder=1000)
  
  ax.set_xlim3d(bounds[:,0])
  ax.set_ylim3d(bounds[:,1])
  ax.set_zlim3d(YYMin, YYMax)
  
  ax.set_xticks(np.linspace(*bounds[:,0], 5))
  ax.set_yticks(np.linspace(*bounds[:,1], 5))
  
  xtl, ytl = 5 * [""], 5 * [""]
  xtl[0], xtl[-1] = "${}$".format(bounds[0,0]), "${}$".format(bounds[1,0])
  ytl[0], ytl[-1] = "${}$".format(bounds[0,1]), "${}$".format(bounds[1,1])
  
  ax.set_xticklabels(xtl, ha="right")
  ax.set_yticklabels(ytl, ha="left")
  
  ax.tick_params(axis="x", pad=-5)
  ax.tick_params(axis="y", pad=-5)
  ax.tick_params(axis="z", pad=2)
  
  ax.set_xlabel(r"$\xscaled[1]$", labelpad=-13)
  ax.set_ylabel(r"$\xscaled[2]$", labelpad=-10)
  
  ax.xaxis.set_rotate_label(False)
  ax.yaxis.set_rotate_label(False)
  
  if cameraPosition is not None: ax.view_init(*cameraPosition[::-1])
  
  fig.save(graphicsNumber=q+1)



def plotConstrainedProblem(q):
  fig = Figure.create(figsize=(3, 3), preamble=r"""
\definecolor{{contourblau}}{{rgb}}{{{},{},{}}}
""".format(*helper.plot.mixColors("mittelblau", 0.7)))
  ax = fig.gca()
  
  if q == 0:
    f = pysgpp.OptG08Objective()
    g = pysgpp.OptG08InequalityConstraint()
    h = pysgpp.OptG08EqualityConstraint()
    bounds = np.array([[0.5, 3], [2.5, 6]])
    xOpt = np.array([1.2280, 4.2454])
    T = [0, 1]
  else:
    f = pysgpp.OptG04SquaredObjective()
    g = pysgpp.OptG04SquaredInequalityConstraint()
    h = pysgpp.OptG04SquaredEqualityConstraint()
    bounds = np.array([[78,  33, 27, 27, 27],
                       [102, 45, 45, 45, 45]])
    xOpt = np.array([78, 33, 29.995256025682, 45, 36.775812905788])
    T = [2, 4]
  
  d = xOpt.size
  f = helper.function.SGppScalarFunction(f)
  g = helper.function.SGppVectorFunction(g)
  h = helper.function.SGppVectorFunction(h)
  fOpt = f.evaluate((xOpt-bounds[0])/(bounds[1]-bounds[0]))
  notT = np.setdiff1d(list(range(d)), T)
  
  XX0, XX1, XX = helper.grid.generateMeshGrid((129, 129))
  
  XXOld = XX
  XX = np.zeros((XX.shape[0], d))
  XX[:,T]    = XXOld
  XX[:,notT] = np.reshape((xOpt[notT]     - bounds[0,notT])/
                          (bounds[1,notT] - bounds[0,notT]), (1, len(notT)))
  
  YY = f.evaluate(XX)
  gXX = g.evaluate(XX)
  hXX = h.evaluate(XX)
  
  XX = bounds[0] + XX * (bounds[1] - bounds[0])
  XX0 = np.reshape(XX[:,T[0]], XX0.shape)
  XX1 = np.reshape(XX[:,T[1]], XX1.shape)
  
  if q == 0:
    K = np.all(gXX <= 0, axis=1)
    triangulation = mpl.tri.Triangulation(XX[K,T[0]], XX[K,T[1]])
    #v = np.arange(-1.05, 1.05, 0.1)
    v = 20
    ax.tricontour(triangulation, YY[K], v)
  else:
    K = np.all(gXX <= [-1e-2, 0, 0, 0, 0, 0], axis=1)
    triangulation = mpl.tri.Triangulation(XX[K,T[0]], XX[K,T[1]])
    YYMin, YYMax = min(np.amin(YY), fOpt), np.amax(YY)
    v = np.linspace(0, 1, 20)**2
    v = YYMin + (YYMax - YYMin) * v
    ax.tricontour(triangulation, YY[K], v)
  
  if q == 0:
    color = helper.plot.mixColors("mittelblau", 0.3)
    colormap = helper.plot.createLinearColormap("conMap", color, color)
    
    for j in range(g.m):
      YY = np.reshape(gXX[:,j], XX0.shape)
      ax.contourf(XX0, XX1, YY, [0, 1e-12], extend="min", cmap=colormap)
      ax.contour(XX0, XX1, YY, [0], colors="C0")
    
    color = helper.plot.mixColors("mittelblau", 0.5)
    colormap = helper.plot.createLinearColormap("conMap2", color, color)
    gXXBoth = np.sum(gXX, axis=1) + np.sqrt(np.sum(gXX**2, axis=1))
    YY = np.reshape(gXXBoth, XX0.shape)
    ax.contourf(XX0, XX1, YY, [0, 1e-12], extend="min", cmap=colormap)
    
    ax.text(2.0,  5.5, r"$\ineqconfunscaled[1] \le 0$",
            color="k", ha="center", va="center", rotation=70)
    ax.text(2.25, 4.9, r"$\ineqconfunscaled[2] \le 0$",
            color="k", ha="center", va="center", rotation=15)
  else:
    color = helper.plot.mixColors("mittelblau", 0.3)
    colormap = helper.plot.createLinearColormap("conMap", color, color)
    
    for j in [0, 4, 5]:
      YY = np.reshape(gXX[:,j], XX0.shape)
      ax.contourf(XX0, XX1, YY, [0, 1e-12], extend="min", cmap=colormap)
      ax.contour(XX0, XX1, YY, [0], colors="C0")
    
    color = helper.plot.mixColors("mittelblau", 0.5)
    colormap = helper.plot.createLinearColormap("conMap2", color, color)
    
    for I in [(0, 4), (0, 5), (4, 5)]:
      gXXBoth = (np.sum(gXX[:,I], axis=1) +
                 np.sqrt(np.sum(gXX[:,I]**2, axis=1)))
      YY = np.reshape(gXXBoth, XX0.shape)
      ax.contourf(XX0, XX1, YY, [0, 1e-12], extend="min", cmap=colormap)
    
    color = helper.plot.mixColors("mittelblau", 0.7)
    colormap = helper.plot.createLinearColormap("conMap3", color, color)
    gXXAll = gXXBoth + gXX[:,0] + np.sqrt(gXXBoth**2 + gXX[:,0]**2)
    YY = np.reshape(gXXAll, XX0.shape)
    ax.contourf(XX0, XX1, YY, [0, 1e-12], extend="min", cmap=colormap)
    
    ax.text(28.7, 34.8,
            r"$\ineqconfunscaled[1] \le 0$",
            color="k", ha="center", va="center", rotation=30)
    ax.text(42.3, 38,
            r"\contour{contourblau}{$\ineqconfunscaled[5] \le 0$}",
            color="k", ha="center", va="center", rotation=-62)
    ax.text(33,   32,
            r"\contour{contourblau}{$\ineqconfunscaled[6] \le 0$}",
            color="k", ha="center", va="center", rotation=-70)
  
  backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
  
  ax.plot(xOpt[T[0]], xOpt[T[1]], ".",
          mec=backgroundColor, mfc="C1", ms=10, mew=1)
  
  ax.set_xlim(bounds[:,T[0]])
  ax.set_ylim(bounds[:,T[1]])
  
  ax.set_xlabel(r"$\xscaled[{}]$".format(T[0]+1), labelpad=-7)
  ax.set_ylabel(r"$\xscaled[{}]$".format(T[1]+1),
                labelpad=(-2 if q == 0 else -8))
  
  ax.set_xticks(np.linspace(*bounds[:,T[0]], 5))
  ax.set_yticks(np.linspace(*bounds[:,T[1]], 5))
  
  xtl, ytl = 5 * [""], 5 * [""]
  xtl[0]  = "${:g}$".format(bounds[0,T[0]])
  xtl[-1] = "${:g}$".format(bounds[1,T[0]])
  ytl[0]  = "${:g}$".format(bounds[0,T[1]])
  ytl[-1] = "${:g}$".format(bounds[1,T[1]])
  
  ax.set_xticklabels(xtl)
  ax.set_yticklabels(ytl)
  
  fig.save(graphicsNumber=q+7)



def main():
  fStrs = ["branin02", "goldsteinPrice", "schwefel06",
           "ackley", "alpine02", "schwefel22"]
  xOpts = np.array([
    [-3.1970, 12.5263],
    [0, -1],
    [1, 3],
    [1.9745, 1.9745],
    [7.9171, 7.9171],
    [0, 0],
  ])
  boundss = [
    np.array([[-5, -5], [15, 15]]),
    np.array([[-2, -2], [2, 2]]),
    np.array([[-6, -6], [4, 4]]),
    np.array([[1.5, 1.5], [6.5, 6.5]]),
    np.array([[2, 2], [10, 10]]),
    np.array([[-3, -3], [7, 7]]),
  ]
  contourOnTops = [True, True, False, False, False, True]
  contourExponents = [2.5, 4, 1, 1, 1, 2]
  lightOrigins = [(90, -45), None, (225, -85), None, None, None]
  cameraPositions = [None, None, (120, 30), None, None, None]
  
  params = zip(fStrs, xOpts, boundss, contourOnTops, contourExponents,
               lightOrigins, cameraPositions)
  
  with multiprocessing.Pool() as pool:
    pool.map(plotUnconstrainedProblem, enumerate(params))
  
  with multiprocessing.Pool() as pool:
    pool.map(plotConstrainedProblem, range(2))



if __name__ == "__main__":
  main()



## some failed attempts to count local minima...
#
#nns = 1000 * np.ones((d,), dtype=int)
#XX = helper.grid.generateMeshGrid(nns)[-1]
#YY = np.reshape(f.evaluate(XX), nns)
#YYDerivs = np.gradient(YY, *(1/(nns-1)))
#YYDeriv = np.stack(YYDerivs, axis=-1)
#print(np.sum(np.all(abs(YYDeriv) < 1e-1, axis=-1)))
#signChange = np.ones(nns, dtype=bool)
#
#for t in range(d):
#  diff = np.diff(np.sign(YYDeriv), axis=t)
#  print(diff.shape)
#  nnsMod = np.hstack((np.array(nns), d))
#  nnsMod[t] = 1
#  print(np.ones(nnsMod).shape)
#  diff = np.concatenate((diff, np.ones(nnsMod)), axis=t)
#  print(diff.shape)
#  signChange = np.logical_and(signChange, np.all((diff != 0), axis=-1))
#
#print(np.sum(signChange))
#import sys
#sys.exit(0)
#
#
#
#nns = d * [6000]
#XX = helper.grid.generateMeshGrid(nns)[-1]
#YY = np.reshape(f.evaluate(XX), nns)
#
#i1s = np.unravel_index(list(range(YY.size)), YY.shape)
#js = np.unravel_index(list(range(3**d)), d*[3])
#xOpts = []
#
#for k, i1 in enumerate(zip(*i1s)):
#  isMinimum = True
#  
#  for j in zip(*js):
#    i2 = tuple(min(max(i1[t]+j[t]-1, 0), YY.shape[t]-1) for t in range(d))
#    if YY[i1] > YY[i2]:
#      isMinimum = False
#      break
#  
#  if isMinimum:
#    print(k, XX[k,:], YY[i1])
#    xOpts.append(XX[k,:])
#
#xOpts = np.vstack(xOpts)
#xOpts = xOpts[np.lexsort(xOpts.T[::-1])]
#print(xOpts)
#print(xOpts.shape[0])
#
#import sys
#sys.exit(0)
