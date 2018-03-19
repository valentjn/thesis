#!/usr/bin/python3
# number of output figures = 1

import matplotlib.patches as patches
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot

def plotNodalSpace(X, ax, pos, size, K=None, KColor="r", notKColor="b"):
  xSquare = np.array([0, 1, 1, 0, 0])
  ySquare = np.array([0, 0, 1, 1, 0])
  s = lambda x, y: (pos[0] + size * np.array(x), pos[1] + size * np.array(y))
  
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  ax.text(*s(0.5, 0.02),
          r"$V_{{({},{})}}$".format(*l), ha="center", va="bottom")
  
  N = X.shape[0]
  if K is None: K = np.zeros((N,), dtype=bool)
  
  ax.plot(*s(X[K,0], X[K,1]), ".", clip_on=False, color=KColor)
  
  K = np.logical_not(K)
  ax.plot(*s(X[K,0], X[K,1]), ".", clip_on=False, color=notKColor)

def plotSG(n, d, b, ax, pos, size):
  xSquare = np.array([0, 1, 1, 0, 0])
  ySquare = np.array([0, 0, 1, 1, 0])
  s = lambda x, y: (pos[0] + size * np.array(x), pos[1] + size * np.array(y))
  
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  ax.text(*s(0.5, 0.03), r"$V_{n,d}^{\mathrm{s}}$",
          ha="center", va="bottom")
  
  grid = helper.grid.RegularSparseBoundary(n, d, b)
  X, L, I = grid.generate()
  ax.plot(*s(X[:,0], X[:,1]), "k.", clip_on=False)



n = 3
d = 2
b = 0

subspaceSize = 1
subspaceMargin = 0.2
sgSize = 1.5
arrowMargin = 0.1
startEndArrowLength = 0.5

L = [(i, n-i) for i in range(n+1)]




brightness = 0.4
schemeSize = (n + 1) * (subspaceSize + subspaceMargin) - subspaceMargin
xOffsetGlobal = 0
yOffsetGlobal = schemeSize

Xs = [helper.grid.getCoordinates(l, helper.grid.getNodalIndices(l))
      for l in L]

figureScale = 1.4
fig = Figure.create(figsize=(3, 3), scale=figureScale, facecolor="none")
ax = fig.gca()

for q in range(len(L)):
  l, X = L[q], Xs[q]
  xOffset = xOffsetGlobal + l[0] * (subspaceSize + subspaceMargin)
  yOffset = yOffsetGlobal - l[1] * (subspaceSize + subspaceMargin) - subspaceSize
  
  XUnion = (np.unique(np.vstack(Xs[q+1:]), axis=0) if q < len(L) - 1 else
            np.zeros((0, d)))
  N = X.shape[0]
  K = np.zeros((N,), dtype=bool)
  for k in range(N): K[k] = not (XUnion == X[k,:]).all(axis=1).any()
  
  plotNodalSpace(X, ax, (xOffset, yOffset), subspaceSize,
                 K=K, KColor="C0", notKColor="C1")
  
  if q == 0:
    arrowEnd = (xOffset + subspaceSize / 2, yOffset + subspaceSize + arrowMargin)
    arrowStart = (arrowEnd[0], arrowEnd[1] + startEndArrowLength)
    helper.plot.plotArrow(ax, arrowStart, arrowEnd)
    ax.text(
      arrowStart[0], arrowStart[1] + 0.56,
      r"$y^{{({})}}_{{\vec{{\ell}},\vec{{i}}}} = 0,$".format(0),
      ha="center", va="bottom")
    ax.text(
      arrowStart[0], arrowStart[1] + 0.28,
      r"$r^{{({})}}(\vec{{x}}_{{\vec{{\ell}},\vec{{i}}}})\hspace{{5mm}}$".format(0),
      ha="center", va="bottom")
    ax.text(
      arrowStart[0], arrowStart[1] + 0.04,
      r"$\hspace{{5mm}}{{}}= f(\vec{{x}}_{{\vec{{\ell}},\vec{{i}}}})$".format(),
      ha="center", va="bottom")
  elif q == len(L) - 1:
    arrowStart = (xOffset + subspaceSize / 2, yOffset - arrowMargin)
    arrowEnd = (arrowStart[0], arrowStart[1] - startEndArrowLength)
    helper.plot.plotArrow(ax, arrowStart, arrowEnd)
    ax.text(
      arrowEnd[0], arrowEnd[1] - 0.04,
      r"$y^{{({})}}_{{\vec{{\ell}},\vec{{i}}}} = "
      r"\alpha_{{\vec{{\ell}},\vec{{i}}}},$".format(q+1),
      ha="center", va="top")
    ax.text(
      arrowEnd[0], arrowEnd[1] - 0.36,
      r"$r^{{({})}}(\vec{{x}}_{{\vec{{\ell}},\vec{{i}}}}) = 0$".format(q+1),
      ha="center", va="top")
  
  if q < len(L) - 1:
    t = np.linspace(-np.pi/2, 0, 200)
    r = subspaceSize / 2 + subspaceMargin - arrowMargin
    center = (xOffset + subspaceSize + arrowMargin,
              yOffset + subspaceSize + subspaceMargin - arrowMargin)
    swap = (q == len(L) - 2)
    if swap: center, t = center[::-1], np.pi/2 - t
    circle = lambda t: (center[0] + r * np.cos(t), center[1] + r * np.sin(t))
    helper.plot.plotArrowPolygon(ax, *circle(t), "k-")
    ax.text(
      *circle(-np.pi/4 + (np.pi if swap else 0)),
      r"$y^{{({})}}_{{\vec{{\ell}},\vec{{i}}}},\, "
      r"r^{{({})}}(\vec{{x}}_{{\vec{{\ell}},\vec{{i}}}})$".format(q+1, q+1),
      ha=("right" if swap else "left"), va=("bottom" if swap else "top"))

plotSG(n, d, b, ax, (0, yOffsetGlobal - sgSize), sgSize)

ax.set_xlim([0, xOffsetGlobal + schemeSize])
ax.set_ylim([0, yOffsetGlobal])
ax.set_axis_off()

fig.save()
