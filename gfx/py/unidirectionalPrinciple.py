#!/usr/bin/python3
# number of output figures = 1

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.misc

def drawSG(X, L, I, t, ax, pos, size):
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
  drawSG(X, L, I, t, ax, (t * 1.3, 0), (1, 1))
  
  #if t == 0:   text = r"$f(\vec{x}_{\vec{k}})$"
  #elif t == 1: text = r"$y_{\vec{k}}^{(1)}$"
  #else:        text = r"$\alpha_{\vec{k}}$"
  #ax.text(t * 1.3 + 0.06, 0.06, text, ha="left", va="bottom")

ax.set_aspect("equal")
ax.set_xlim(0, 3.8)
ax.set_ylim(0, 1)
ax.set_axis_off()

fig.save()
