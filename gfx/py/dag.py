#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot



def isParent1D(l1, i1, l2, i2):
  if l1 + 1 == l2:
    if l1 == 0:
      if i2 == 1: return True
    else:
      if i2 in [2*i1-1, 2*i1+1]: return True
  return False

def getParentDimension(l1, i1, l2, i2):
  t = l1.shape[0]
  parentDimension = None
  
  for t in range(d):
    if isParent1D(l1[t], i1[t], l2[t], i2[t]):
      if parentDimension is not None: return None
      parentDimension = t
    else:
      if (l1[t] != l2[t]) or (i1[t] != i2[t]): return None
  
  return parentDimension

def plotLine(ax, xx, yy, l, n):
  #ax.plot(xx, yy, "k-")
  N = xx.shape[0]
  segments = [np.array([[xx[k], yy[k]], [xx[k+1], yy[k+1]]])
              for k in range(N - 1)]
  lineCollection = mpl.collections.LineCollection(
    segments, cmap="viridis", norm=mpl.colors.Normalize(0, 1))
  t = np.linspace(0, 1, n+1)
  tt = np.linspace(t[l], t[l+1], N)
  lineCollection.set_array(tt)
  ax.add_collection(lineCollection)



n = 4
d = 2
b = 1

grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()
K = np.lexsort((*L.T, np.sum(L, axis=1)))
X, L, I = X[K,:], L[K,:], I[K,:]
N = X.shape[0]



fig = Figure.create(figsize=(3, 3), scale=1.5)
ax = fig.gca()

angle = 35 / 180 * np.pi
colormap = mpl.cm.get_cmap("viridis")

for k1 in range(N):
  for k2 in range(N):
    parentDimension = getParentDimension(L[k1,:], I[k1,:], L[k2,:], I[k2,:])
    
    if parentDimension is not None:
      l = L[k1,parentDimension]
      nn = int(125 * np.linalg.norm(X[k2,:] - X[k1,:]))
      tt = np.linspace(0, 1, nn)
      XX = helper.plot.getQuadraticBezierCurveViaAngle(X[k1,:], X[k2,:], angle, tt)
      XX = XX[:-2,:]
      curPlotLine = (lambda ax, xx, yy: plotLine(ax, xx, yy, np.sum(L[k1,:]), n))
      levelSum = np.sum(L[k2,:])
      headColor = colormap(levelSum / n)
      helper.plot.plotArrowPolygon(
        ax, XX[:,0], XX[:,1], curPlotLine, scaleHead=0.5, virtualHeadLength=0.015,
        ec=headColor, fc=headColor, zorder=levelSum, cutOff=1)

ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k-", clip_on=False)

#for k in range(N):
#  color = colormap(np.sum(L[k,:]) / n)
#  ax.plot(X[k,0], X[k,1], ".", clip_on=False, color=color)

ax.scatter(X[:,0], X[:,1], c=np.sum(L, axis=1)/n, edgecolors="k", zorder=100)

ax.set_axis_off()
ax.set_aspect("equal")
ax.set_xlim(-0.1, 1.1)
ax.set_ylim(-0.1, 1.1)

P = ax.get_position().get_points()
pos = [P[0,0], P[0,1], P[1,0] - P[0,0], P[1,1] - P[0,1]]

xShift = -0.15
pos = [pos[0] + xShift * pos[2], pos[1], pos[2], pos[3]]
ax.set_position(pos)

xShift = 0.0
xScale = 0.07
yScale = 0.835
pos = [pos[0] + pos[2] + xShift,
       pos[1] + (1-yScale)/2 * pos[3],
       xScale * pos[2],
       yScale * pos[3]]

cax = fig.add_axes(pos)
h = 1/n
bounds = n * np.linspace(-h/2, 1+h/2, n+2)
ticks = n * np.linspace(0, 1, n+1)
norm = mpl.colors.Normalize(0, n)
colorbar = mpl.colorbar.ColorbarBase(
  cax, cmap=colormap, boundaries=bounds, ticks=ticks, norm=norm)
cax.set_position(pos)
cax.text(0.55, 1.02, r"$\lVert\vec{\ell}\rVert_1$", ha="center", va="bottom")

fig.save(tightLayout=False)
