#!/usr/bin/python3
# number of output figures = 3

import numpy as np

import helper.basis
from helper.figure import Figure

p = 3

for q in range(3):
  if q == 0:
    xi = [0, 1, 3, 4, 7, 9, 10, 11, 14, 16, 17]
    c = [0.3, 0.2, -0.1, 0.1, 0.3, -0.2, 0.4]
    splineScale = 1
    splineShift = 0.9
    yMax = 1.15
    figsize = (6, 2.5)
  else:
    n = 3
    yMax = 0.9
    figsize = (6, 2.2)
    xi = (helper.basis.HierarchicalBSpline(p).getKnots(3) if q == 1 else
          helper.basis.HierarchicalNotAKnotBSpline(p).getKnots(3))
  
  m = len(xi) - p - 1
  D = [xi[p], xi[m]]
  
  fig = Figure.create(figsize=figsize)
  ax = fig.gca()
  
  for k in range(m):
    color = "C{}".format(k % 9)
    b = helper.basis.NonUniformBSpline(p, xi, k)
    lb, ub = xi[k], xi[k+p+1]
    xx = np.linspace(lb, ub, 200)
    yy = b.evaluate(xx)
    ax.plot(xx, yy, "-", color=color, clip_on=False)
    
    r = np.argmax(yy)
    ax.text(xx[r], yy[r] + 0.02, r"$b_{{{},\ß\xi}}^p$".format(k),
            color=color, ha="center", va="bottom")
  
  if q == 0:
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
  
  for x in (D if q == 0 else [0, 1]):
    ax.plot([x, x], [0, yMax], "k--", clip_on=False)
  
  if q >= 1:
    h = 2**(-n)
    color = Figure.COLORS["mittelblau"]
    ax.text(0,     -0.2, r"$0$", ha="center", va="top", color=color)
    ax.text(h,     -0.2, r"$x_{l,1}\vphantom{0}$", ha="center", va="top", color=color)
    ax.text(2*h,   -0.2, r"$\cdots\vphantom{0}$", ha="center", va="top", color=color)
    ax.text(1-2*h, -0.2, r"$\cdots\vphantom{0}$", ha="center", va="top", color=color)
    ax.text(1-h,   -0.2, r"$x_{l,2^l-1}\vphantom{0}$", ha="center", va="top", color=color)
    ax.text(1,     -0.2, r"$1$", ha="center", va="top", color=color)
    ax.text(1+(p+1)*h, -0.082, r"$\vec{\xi}$", ha="center", va="top")
    ax.text(1+(p+1)*h, -0.2, r"$x\vphantom{0}$", ha="center", va="top", color=color)
    I = helper.grid.getNodalIndices1D(n)
    X = helper.grid.getCoordinates(n, I)
    ax.plot(X, 0*X, ".", color=color, clip_on=False, zorder=10)
  
  xtl = len(xi) * [""]
  xtl[0] = r"$\xi_0$"
  xtl[p] = r"$\xi_p$"
  xtl[m] = r"$\xi_m$"
  xtl[m+p] = r"$\xi_{m+p}$"
  
  ax.set_xticks(xi)
  ax.set_xticklabels(xtl)
  ax.tick_params(axis="x", length=6)
  
  if q == 0: xiStart, xiEnd = xi[0], xi[-1]
  else:      xiStart, xiEnd = -p*(xi[1]-xi[0]), 1+p*(xi[1]-xi[0])
  h = 0.05 * (xiEnd - xiStart)
  ax.set_xlim(xiStart - h, xiEnd + h)
  
  ax.set_yticks([0])
  ax.set_ylim(0, yMax)
  
  fig.save(tightLayout={"pad" : 1.3})
