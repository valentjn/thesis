#!/usr/bin/python3
# number of output figures = 2

import numpy as np

import helper.basis
from helper.figure import Figure
import helper.grid



n = 3
p = 1
c = [0.3, 0.8, 0.6, 0.7, 0.4, 0.9, 0.8, 0.75, 0.2]
basis = helper.basis.HierarchicalBSpline(p)

hInv = 2**n
X = helper.grid.getCoordinates(n, list(range(hInv + 1)))
xtl = ["$x_{{{},{}}}$".format(n, i) for i in range(hInv + 1)]



fig = Figure.create(figsize=(3.3, 2.0))
ax = fig.gca()

for i in range(0, hInv + 1):
  color = "C{}".format(i)
  xx = np.linspace(*basis.getSupport(n, i), 200)
  yy = c[i] * basis.evaluate(n, i, xx)
  ax.plot(xx, yy, "-", color=color, clip_on=False)

line, = ax.plot(X, c, "k.-", clip_on=False)
line.set_dashes([3, 3])
ax.text(0.85, 0.85, r"$f_3^1$", color="k", ha="center", va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0, 0.9)
ax.set_xticks(X)
ax.set_xticklabels(xtl)
ax.set_yticks([0])

fig.save(tightLayout={"pad" : 2})



fig = Figure.create(figsize=(3.3, 2.0), scale=1.0)
ax = fig.gca()

for l in range(n+1):
  I = helper.grid.getHierarchicalIndices1D(l)
  
  for i in I:
    k = i * 2**(n-l)
    kl = (i-1) * 2**(n-l)
    kr = (i+1) * 2**(n-l)
    color = "C{}".format(k % 9)
    
    if l > 0:
      x = [X[kl], X[k], X[kr]]
      y = [c[kl], c[k], c[kr]]
    else:
      if i == 1: continue
      x = [X[0], X[-1]]
      y = [c[0], c[-1]]
    
    ax.plot(x, y, "-", color=color, clip_on=False)

line, = ax.plot(X, c, "k.--", clip_on=False)
line.set_dashes([3, 3])
ax.text(0.85, 0.85, r"$f_3$", color="k", ha="center", va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0, 0.9)
ax.set_xticks(X)
ax.set_xticklabels(xtl)
ax.set_yticks([0])

fig.save(tightLayout={"pad" : 2})
