#!/usr/bin/python3
# number of output figures = 1

import numpy as np

import helper.basis
from helper.figure import Figure

p = 3
xi = [0, 1, 3, 4, 7, 9, 10, 11, 14, 16, 17]
c = [0.3, 0.2, -0.1, 0.1, 0.3, -0.2, 0.4]
splineScale = 1
splineShift = 0.9
yMax = 1.15

m = len(xi) - p - 1
D = [xi[p], xi[m]]

fig = Figure.create(figsize=(6, 2.5))
ax = fig.gca()

for k in range(m):
  color = "C{}".format(k % 9)
  b = helper.basis.NonUniformBSpline(p, xi, k)
  lb, ub = xi[k], xi[k+p+1]
  xx = np.linspace(lb, ub, 200)
  yy = b.evaluate(xx)
  ax.plot(xx, yy, "-", color=color, clip_on=False)
  
  q = np.argmax(yy)
  ax.text(xx[q], yy[q] + 0.02, r"$b_{{{},\ß\xi}}^p$".format(k),
          color=color, ha="center", va="bottom")

xx = np.linspace(*D, 200)
yy = np.zeros_like(xx)

for k in range(m):
  b = helper.basis.NonUniformBSpline(p, xi, k)
  yy += c[k] * b.evaluate(xx)

yy = splineShift + splineScale * yy
ax.plot(xx, yy, "k-", clip_on=False, solid_capstyle="butt")
ax.text(8, 1, r"$s$", color="k", ha="center", va="bottom")

ax.plot(D, 2*[-0.01], "k-", clip_on=False, lw=2, solid_capstyle="butt")
ax.text(sum(D) / 2, -0.08, r"$D_\ß\xi^p$", color="k", ha="center", va="top")

for x in D:
  ax.plot([x, x], [0, yMax], "k--", clip_on=False)

xtl = len(xi) * [""]
xtl[0] = r"$\xi_0$"
xtl[p] = r"$\xi_p$"
xtl[m] = r"$\xi_m$"
xtl[m+p] = r"$\xi_{m+p}$"

h = 0.05 * (xi[-1] - xi[0])
ax.set_xlim(xi[0] - h, xi[-1] + h)
ax.set_xticks(xi)
ax.set_xticklabels(xtl)
ax.tick_params(axis="x", length=6)

ax.set_ylim(0, yMax)
ax.set_yticks([0, 1])

fig.save()
