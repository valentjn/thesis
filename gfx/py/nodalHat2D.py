#!/usr/bin/python3
# number of output figures = 1

import numpy as np

import helper.basis
from   helper.figure import Figure
import helper.grid
import helper.plot



l = [2, 1]
i = [1, 1]
p = 1
d = 2
b1D = helper.basis.HierarchicalBSpline(p)
b = helper.basis.TensorProduct(b1D, d)

I = helper.grid.getNodalIndices(l)
X = helper.grid.getCoordinates(l, I)



fig = Figure.create(figsize=(3, 3))
ax = fig.add_subplot(111, projection="3d")

for t in range(d):
  xx = np.linspace(*b1D.getSupport(l[t], i[t]), 33)
  yy = b1D.evaluate(l[t], i[t], xx)
  ax.plot(*((xx, np.ones_like(xx)) if t == 0 else
            (np.zeros_like(xx), xx)), "k-", zs=yy, zorder=-1, clip_on=False)

xx0 = np.linspace(0, 1, 33)
xx1 = np.linspace(0, 1, 33)
XX0, XX1 = np.meshgrid(xx0, xx1)
XX = np.column_stack((XX0.flatten(), XX1.flatten()))
YY = b.evaluate(l, i, XX)
YY = np.reshape(YY, XX0.shape)
helper.plot.removeWhiteLines(ax.plot_surface(XX0, XX1, YY))

K = list(range(X.shape[0]))
for k in [5, 4, 2, 1]: del K[k]
ax.plot(X[K,0], X[K,1], "k.", zs=np.zeros_like(X[K,0]), clip_on=False)
x = helper.grid.getCoordinates(l, i)
ax.plot([x[0]], [x[1]], "k.", zs=[1], clip_on=False)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)

ax.set_xticks(np.unique(X[:,0]))
ax.set_yticks(np.unique(X[:,1]))
ax.set_zticks([0, 1])

ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

eps = 0.15
ax.text(0, -eps, 0, r"$0$", ha="center", va="top")
ax.text(1, -eps, 0, r"$1$", ha="center", va="top")

eps = 0.1
ax.text(1+eps, 0, 0, r"$0$", ha="left", va="top")
ax.text(1+eps, 0.95, 0, r"$1$", ha="left", va="top")

eps = 0.1
ax.text(1+eps, 1, 0.02, r"$0$", ha="left", va="bottom")
ax.text(1+eps, 1, 1, r"$1$", ha="left", va="center")

ax.text(0.5, -0.2, 0, r"$x_1$", ha="center", va="top")
ax.text(1.1, 0.5, 0, r"$x_2$", ha="left", va="top")

ax.grid(False)

fig.save()
