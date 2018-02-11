#!/usr/bin/python3
# number of output figures = 1

import numpy as np

from helper.figure import Figure
import helper.grid

margin = 0.1
circleMargin = 0
textMargin = 0.03
circleColor = "C0"
n = 4

fig = Figure.create(figsize=(4, 4), scale=1.3)
ax = fig.gca()

radius = 0.5
center = [0.5, -circleMargin]
circle = lambda t: (center[0] + radius * np.cos(t), center[1] - radius * np.sin(t))
t = np.linspace(0, np.pi, 2**n + 1)

for i in range(1, 2**n):
  ax.plot(*list(zip(center, circle(t[i]))), "-", clip_on=False, color=circleColor)

for i in range(1, 2**n):
  x, y = circle(t[i])
  ax.plot([x, x], [y, center[1]], "--", clip_on=False, color=circleColor)

tt = np.linspace(0, np.pi, 200)
ax.plot(*circle(tt), "-", clip_on=False, color=circleColor)

ax.plot(*circle(t), ".", clip_on=False, color=circleColor)

for l in range(n + 1):
  y = (n - l) * margin
  hInv = 2**l
  I = list(range(hInv + 1))
  L = (hInv + 1) * [l]
  X = helper.grid.getCoordinates(L, I, distribution="clenshawCurtis")
  ax.plot([0, 1], 2 * [y], "k-", clip_on=False)
  ax.plot(X, y * np.ones_like(X), "k.", clip_on=False)
  ax.text(1 + textMargin, y, r"$\ell = {}$".format(l), ha="left", va="center")

ax.set_axis_off()
ax.set_aspect("equal")

fig.save(tightLayout={"pad" : 2})
