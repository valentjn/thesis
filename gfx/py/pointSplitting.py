#!/usr/bin/python3
# number of output figures = 2

import numpy as np

from helper.figure import Figure
import helper.grid

topMargin = 0.15
margin = 0.1
textMarginX = 0.05
circleColor = 3 * [0.6]
n = 4

for q in range(2):
  if q == 0:
    scale = 1.3
    textMarginY = 0.03
  else:
    scale = 2.1
    textMarginY = 0.02
  
  fig = Figure.create(figsize=(4, 2), scale=scale)
  ax = fig.gca()
  
  yTop = n * margin + topMargin
  superscript = (r"\mathrm{cc}" if q == 1 else "")
  distribution = ("clenshawCurtis" if q == 1 else "uniform")
  
  if q == 1:
    radius = 0.5
    center = [0.5, yTop]
    circle = lambda t: (center[0] + radius * np.cos(t), center[1] - radius * np.sin(t))
    t = np.linspace(-np.pi, 0, 2**n + 1)

    for i in range(1, 2**n):
      ax.plot(*list(zip(center, circle(t[i]))), "-", clip_on=False, color=circleColor)

    for i in range(1, 2**n):
      x, y = circle(t[i])
      ax.plot([x, x], [y, center[1]], "--", clip_on=False, color=circleColor)

    tt = np.linspace(-np.pi, 0, 200)
    ax.plot(*circle(tt), "-", clip_on=False, color=circleColor)

    ax.plot(*circle(t), ".", clip_on=False, color=circleColor)
  
  for l in range(n + 1):
    y = (n - l) * margin
    hInv = 2**l
    I = helper.grid.getHierarchicalIndices(l)
    X = helper.grid.getCoordinates(l, I, distribution=distribution)
    for x in X: ax.plot([x, x], [y, yTop], "-", color=circleColor)
  
  hInv = 2**n
  I = list(range(hInv + 1))
  X = helper.grid.getCoordinates(n, I, distribution=distribution)
  ax.plot([0, 1], 2 * [yTop], "k-", clip_on=False)
  ax.plot(X, yTop * np.ones_like(X), "k.", clip_on=False)
  ax.text(1 + textMarginX, yTop, r"$\ell = {}$".format(n), ha="left", va="center")
  
  for l in range(n + 1):
    y = (n - l) * margin
    hInv = 2**l
    I = helper.grid.getHierarchicalIndices(l)
    X = helper.grid.getCoordinates(l, I, distribution=distribution)
    ax.plot([0, 1], 2 * [y], "k-", clip_on=False)
    ax.plot(X, y * np.ones_like(X), "k.", clip_on=False)
    ax.text(1 + textMarginX, y, r"$\ell' = {}$".format(l), ha="left", va="center")
    x = (2**(n-1)+1)/2**n
    #if l > 0: ax.text(x, y + margin/2, r"$\dot{\cup}$", ha="center", va="center")
    #else:     ax.text(x, y + topMargin/2, r"\rotatebox{90}{$=$}", ha="center", va="center")
    
    for i, x in zip(I, X):
      if (q == 1) and (l == 4):
        if i == 3:  x += 0.02
        if i == 13: x -= 0.02
        if i == 15: x += 0.02
      ax.text(x, y - textMarginY, r"$x_{{{},{}}}^{{{}}}$".format(l, i, superscript),
              ha="center", va="top")
  
  ax.set_axis_off()
  ax.set_aspect("equal")
  
  fig.save(tightLayout={"pad" : 2.2})
