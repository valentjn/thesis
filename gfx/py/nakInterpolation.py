#!/usr/bin/python3
# number of output figures = 2

import numpy as np

import helper.basis
from helper.figure import Figure

f = lambda x: -10.2 * x**3 + 14.7 * x**2 - 5 * x + 0.7
n = 3
d = 1
b = 0
p = 3

basis = helper.basis.HierarchicalBSpline(p)
xtl = [r"$x_{{{},{}}}$".format(n, i) for i in range(2**n + 1)]



fig = Figure.create(figsize=(3, 2.5))
ax = fig.gca()

xx = np.linspace(0, 1, 513)
yy = f(xx)
ax.plot(xx, yy, "-", clip_on=False, color="C0")
ax.text(0.95, 0.6, r"$f$", ha="left", va="bottom", color="C0")

grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()
interpolant = helper.basis.Interpolant(basis, X, L, I)
fX = f(X)
aX = interpolant.getSurpluses(fX)
yy2 = interpolant.evaluate(aX, xx)
ax.plot(xx, yy2, "--", clip_on=False, color="C1")
ax.text(0.91, 0.5, r"$\tilde{f}$", ha="right", va="top", color="C1")

ax.plot(X, fX, "k.", clip_on=False)

D = [2**(-n) * (p-1)/2, 1 - 2**(-n) * (p-1)/2]
ax.plot(D, [0, 0], "k-", clip_on=False, lw=2, solid_capstyle="butt")
ax.text(0.5, 0.05, r"$D_{{{}}}^{{{}}}$".format(n, "p"), ha="center", va="bottom")

ax.set_xlim(0, 1)
ax.set_xticks(np.sort(X.flatten()))
ax.set_xticklabels(xtl)

ax.set_ylim(0, 1)
ax.set_yticks([0, 1])

fig.save()



fig = Figure.create(figsize=(3, 2.5))
ax = fig.gca()
yMin = 1e-5

err = np.abs((yy - yy2) / yy)
print(yy[28])
print(yy2[28])
print(err[28])
err = np.maximum(err, yMin)
ax.plot(xx, err, "k-", clip_on=False)

ax.set_xlim(0, 1)
ax.set_xticks(np.sort(X.flatten()))
ax.set_xticklabels(xtl)

ax.set_yscale("log")
ax.set_ylim([yMin, 1e0])

fig.save()
