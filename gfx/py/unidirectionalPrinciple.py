#!/usr/bin/python3
# number of output figures = 1

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.misc
import helper.plot

def plotSG(X, L, I, t, ax, pos, size):
  s = lambda x, y: (pos[0] + size[0] * x, pos[1] + size[1] * y)
  
  xSquare, ySquare = np.array([0, 1, 1, 0, 0]), np.array([0, 0, 1, 1, 0])
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  
  N = X.shape[0]
  K = np.ones((N,), dtype=bool)
  color = "k"
  
  
  if t < d:
    isEquivalent = lambda x, y: (np.all(x[:t] == y[:t]) and
                                 np.all(x[t+1:] == y[t+1:]))
    equivalenceClasses = helper.misc.getEquivalenceClasses(X, isEquivalent)
    equivalenceClasses.sort(key=lambda x: x[0][1-t])
    
    for j, equivalenceClass in enumerate(equivalenceClasses):
      color = "C{}".format(j % 9)
      XClass = np.vstack(equivalenceClass)
      ax.plot(*s(XClass[:,0], XClass[:,1]), ".", clip_on=False, color=color)
  else:
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
  
  if t == 0:   text = r"$\vec{u} = \vec{y}^{(0)}$"
  elif t == 1: text = r"$\vec{y}^{(1)}$"
  else:        text = r"$\vec{y}^{(2)} = \vec{y}$"
  ax.text(t * 1.3 + 0.5, -0.06, text, ha="center", va="top")

arrowProperties = {"head_width" : 0.03, "head_length" : 0.03, "overhang" : 0.3,
                   "length_includes_head" : True, "fc" : "k", "clip_on" : False,
                   "lw" : 0.9}
helper.plot.plotArrow(ax, (0.74, -0.12), (1.66, -0.12))
ax.text(1.2, -0.15, r"$\mathfrak{L}_1$", ha="center", va="top")
helper.plot.plotArrow(ax, (1.94, -0.12), (2.86, -0.12))
ax.text(2.4, -0.15, r"$\mathfrak{L}_2$", ha="center", va="top")
helper.plot.plotArrowPolygon(
  ax, [0.5, 0.5, 3.1, 3.1], [-0.21, -0.4, -0.4, -0.21], "k-", cutOff=1)
ax.text(1.8, -0.37, r"$\mathfrak{L}$", ha="center", va="bottom")

ax.set_aspect("equal")
ax.set_xlim(0, 3.8)
ax.set_ylim(-0.4, 1)
ax.set_axis_off()

fig.save()
