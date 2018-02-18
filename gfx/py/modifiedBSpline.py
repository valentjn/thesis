#!/usr/bin/python3
# number of output figures = 1

import numpy as np

import helper.basis
from helper.figure import Figure

p = 3
l = 3
b = helper.basis.HierarchicalBSpline(p)

fig = Figure.create(figsize=(3, 2))
ax = fig.gca()
h = 2**(-l)

for i in range(1 - (p+1)//2, 2):
  color = "C{}".format(i % 9)
  x = i*h
  lb, ub = x - (p+1)/2 * h, x + (p+1)/2 * h
  xx = np.linspace(lb, ub, 200)
  yy = (2 - i) * b.evaluate(l, i, xx)
  ax.plot(xx, yy, "-", color=color, clip_on=False)
  ax.text(x, max(yy)+0.05,
          r"${} \varphi_{{{},{}}}^{{{}}}$".format(2-i, r"\ell'", i, "p"),
          ha="center", va="bottom", color=color)

i = 1
b = helper.basis.ModifiedHierarchicalBSpline(p)
xx = np.linspace(*b.getSupport(l, i), 200)
yy = b.evaluate(l, i, xx)
ax.plot(xx, yy, "k--", clip_on=False)
ax.text(i*h-0.02, 1.2,
        r"$\varphi_{{{},{}}}^{{{}}}$".format(r"\ell'", 1, r"p,\mathrm{mod}"),
        ha="left", va="bottom", color="k")

maxY = 2.1
ax.plot([0, 0], [0, maxY], "k-", clip_on=False)

I = np.arange(-3, 2+(p+1)//2)
ax.set_xticks(h * I)
ax.set_xticklabels([r"$x_{{{},{}}}$".format(r"\ell'", i) for i in I])

ax.set_ylim(0, maxY)
ax.set_yticks([0, 1, 2])

fig.save()
