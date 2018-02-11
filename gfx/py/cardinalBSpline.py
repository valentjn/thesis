#!/usr/bin/python3
# number of output figures = 1

import numpy as np

import helper.basis
from helper.figure import Figure

n = 3
pMax = 5



fig = Figure.create(figsize=(pMax+1, 1), scale=1.5)
ax = fig.gca()

for p in range(pMax + 1):
  color = "C{}".format(p)
  
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 200)
  if p == 0: xx = xx[1:-1]
  yy = b.evaluate(xx)
  ax.plot(xx, yy, "-", color=color, clip_on=False)
  
  if p == 0:
    ax.plot(1, 1, "o", fillstyle="none", ms=4, color=color, clip_on=False)
    ax.plot(1, 0, ".", ms=8, color=color, clip_on=False)
  
  if   p == 0: x, y = 0.5,     1
  elif p == 1: x, y = 1.23,    0.85
  else:        x, y = (p+1)/2, max(yy)
  y += 0.05
  ax.text(x, y, "$b^{}$".format(p), color=color, ha="center")

ax.set_xlim((0, pMax+1))
ax.set_ylim((0, 1))
ax.set_yticks([0, 1])
ax.set_aspect("equal")

fig.save()
