#!/usr/bin/python3
# number of output figures = 2

import numpy as np

import helper.basis
from helper.figure import Figure
import helper.grid

l = 3
p = 1
b = helper.basis.HierarchicalBSpline(p)



fig = Figure.create(figsize=(3.3, 1.6))
ax = fig.gca()
hInv = 2**l
h = 1 / hInv
X = helper.grid.getCoordinates(l, list(range(hInv + 1)))
xtl = ["$x_{{{},{}}}$".format(l, i) for i in range(hInv + 1)]

for i in range(0, hInv + 1):
  color = "C{}".format(i)
  xx = np.linspace(*b.getSupport(l, i), 200)
  yy = b.evaluate(l, i, xx)
  ax.plot(xx, yy, "-", color=color, clip_on=False)
  
  j = np.argmax(yy)
  x, y = xx[j], yy[j] * 1.05
  ax.text(x, y, r"$\varphi_{{{},{}}}^{{{}}}$".format(l, i, p),
          color=color, ha="center", va="bottom")

ax.plot(X, np.zeros_like(X), "k.", clip_on=False)

ax.set_xticks(X)
ax.set_xticklabels(xtl)
ax.set_yticks([0, 1])

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

fig.save(tightLayout={"pad" : 2})



fig = Figure.create(figsize=(3.3, 2.0))
ax = fig.gca()
c = [0.3, 0.8, 0.7, 0.7, 0.5, 0.9, 0.8, 0.7, 0.2]

for i in range(0, hInv + 1):
  color = "C{}".format(i)
  xx = np.linspace(*b.getSupport(l, i), 200)
  yy = c[i] * b.evaluate(l, i, xx)
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
