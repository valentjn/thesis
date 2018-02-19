#!/usr/bin/python3
# number of output figures = 1

import numpy as np

from helper.figure import Figure
import helper.grid

topMargin = 0.15
margin = 0.1
textMarginX = 0.05
textMarginY = 0.03
n = 4

fig = Figure.create(figsize=(4, 2), scale=1.3)
ax = fig.gca()

yTop = n * margin + topMargin

for l in range(n + 1):
  y = (n - l) * margin
  hInv = 2**l
  I = helper.grid.getHierarchicalIndices1D(l)
  X = helper.grid.getCoordinates(l, I)
  for x in X: ax.plot([x, x], [y, yTop], "-", color=3*[0.8])

hInv = 2**n
I = list(range(hInv + 1))
X = helper.grid.getCoordinates(n, I)
ax.plot([0, 1], 2 * [yTop], "k-", clip_on=False)
ax.plot(X, yTop * np.ones_like(X), "k.", clip_on=False)
ax.text(1 + textMarginX, yTop, r"$\ell = {}$".format(n), ha="left", va="center")

for l in range(n + 1):
  y = (n - l) * margin
  hInv = 2**l
  I = helper.grid.getHierarchicalIndices1D(l)
  X = helper.grid.getCoordinates(l, I)
  ax.plot([0, 1], 2 * [y], "k-", clip_on=False)
  ax.plot(X, y * np.ones_like(X), "k.", clip_on=False)
  ax.text(1 + textMarginX, y, r"$\ell' = {}$".format(l), ha="left", va="center")
  x = (2**(n-1)+1)/2**n
  #if l > 0: ax.text(x, y + margin/2, r"$\dot{\cup}$", ha="center", va="center")
  #else:     ax.text(x, y + topMargin/2, r"\rotatebox{90}{$=$}", ha="center", va="center")
  
  for i, x in zip(I, X):
    ax.text(x, y - textMarginY, r"$x_{{{},{}}}$".format(l, i), ha="center", va="top")

ax.set_axis_off()

fig.save(tightLayout={"pad" : 2.2})
