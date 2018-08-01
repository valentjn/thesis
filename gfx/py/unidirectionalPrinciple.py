#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.misc
import helper.plot

def plotSG(X, L, I, t, ax, pos, size):
  s = lambda x, y: (pos[0] + size[0] * x, pos[1] + size[1] * y)
  
  xSquare, ySquare = np.array([0, 1, 1, 0, 0]), np.array([0, 0, 1, 1, 0])
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  
  #if t < d:
  #  isEquivalent = lambda x, y: (np.all(x[:t] == y[:t]) and
  #                               np.all(x[t+1:] == y[t+1:]))
  #  equivalenceClasses = helper.misc.getEquivalenceClasses(X, isEquivalent)
  #  equivalenceClasses.sort(key=lambda x: x[0][1-t])
  #  
  #  for j, equivalenceClass in enumerate(equivalenceClasses):
  #    color = "C{}".format(j % 9)
  #    XClass = np.vstack(equivalenceClass)
  #    ax.plot(*s(XClass[:,0], XClass[:,1]), ".", clip_on=False, color=color)
  #else:
  #  ax.plot(*s(X[:,0], X[:,1]), "k.", clip_on=False)
  
  if t < d:
    h = 1 / 2**np.max(L)
    hMargin = 0.05
    brightness = 0.3
    X1D = np.unique(X[:,1-t])
    
    for x1D in X1D:
      x, y, width, height = -hMargin, x1D-h*0.4, 1+2*hMargin, 0.8*h
      if t == 1: x, y, width, height = y, x, height, width
      color = helper.plot.mixColors("C{}".format(int(8*x1D) % 9), 1-brightness)
      width, height = width * size[0], height * size[1]
      ax.add_patch(mpl.patches.Rectangle(s(x, y), width, height, color=color))
  
  ax.plot(*s(X[:,0], X[:,1]), "k.", clip_on=False)



n = 4
d = 2
b = 1

grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()

fig = Figure.create(figsize=(2, 2), scale=3)
ax = fig.gca()

for t in range(d+1):
  plotSG(X, L, I, t, ax, (t * 1.3, 0), (1, 1))
  
  if t == 0:   text = r"$\vlinin = \vlinout[(0)]$"
  elif t == 1: text = r"$\vlinout[(1)]$"
  else:        text = r"$\vlinout[(2)] = \vlinout$"
  ax.text(t * 1.3 + 0.5, -0.08, text, ha="center", va="top")

helper.plot.plotArrow(ax, (0.74, -0.14), (1.66, -0.14))
ax.text(1.2, -0.17, r"$\upopuv{1}{\lisetpole}$",
        ha="center", va="top")
helper.plot.plotArrow(ax, (1.94, -0.14), (2.86, -0.14))
ax.text(2.4, -0.17, r"$\upopuv{2}{\lisetpole}$",
        ha="center", va="top")
helper.plot.plotArrowPolygon(
  ax, [0.5, 0.5, 3.1, 3.1], [-0.23, -0.42, -0.42, -0.23], "k-", cutOff=1)
ax.text(1.8, -0.37, r"$\linop$", ha="center", va="bottom")

ax.set_aspect("equal")
ax.set_xlim(-0.05, 3.8)
ax.set_ylim(-0.44, 1.05)
ax.set_axis_off()

fig.save()
