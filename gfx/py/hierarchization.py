#!/usr/bin/python3
# number of output figures = 3

import matplotlib.patches
import numpy as np

import helper.basis
from helper.figure import Figure
import helper.function
import helper.grid

n = 3
d = 1
b = 0
p = 3

fX = [0.3, 0.8, 0.6, 0.7, 0.4, 0.9, 0.8, 0.75, 0.2]

grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()
K = np.argsort(X, axis=0).flatten()
X, L, I = X[K,:], L[K,:], I[K,:]
N = X.shape[0]

for pCurrent in [1, p]:
  basis = helper.basis.HierarchicalNotAKnotBSpline(pCurrent)
  interpolant = helper.function.Interpolant(basis, X, L, I, fX)
  if pCurrent == 1: aX = np.array(interpolant.aX)

xt = np.array(X).flatten()
xtl = [(r"$x_{\ell,i} \in \Omega^{\mathrm{s}}$" if i == 2**(n-1) else "")
       for i in range(2**n + 1)]
xtl[0] = "$0$"
xtl[-1] = "$1$"

xq = 0.8
k, _ = np.where(xt > xq)[0]
xt2 = np.hstack((xt[:k], np.array([xq]), xt[k:]))
xtl2 = xtl[:k] + ["$x$"] + xtl[k:]


for q in range(3):
  fig = Figure.create(figsize=(2.2, 2.3))
  ax = fig.gca()
  
  if q == 0:
    xx = np.linspace(0, 1, 200)
    XX = np.array([xx]).T
    yy2 = interpolant.evaluate(XX)
    ax.plot(xx, yy2, "k-", clip_on=False)
    ax.plot(X, fX, "k.", clip_on=False)
    ax.text(0.67, 0.4, r"$f(x_{\ell,i})$", ha="center", va="center")
  elif q == 1:
    for k in range(N):
      i = I[k,0] * 2**(n-L[k,0])
      color = "C{}".format((i if i < 2**n else 0) % 9)
      ax.plot([X[k,0], X[k,0]], [0, aX[k]], "--", color=color, clip_on=False,
              zorder=10)
    
    ax.plot(X, aX, "ko", clip_on=False, ms=3, fillstyle="none", zorder=20)
    ax.text(0.65, 0.5, r"$\alpha_{\ell,i}$", ha="center", va="center")
  else:
    xx = np.linspace(0, 1, 513)
    XX = np.array([xx]).T
    
    for l in range(n+1):
      I = helper.grid.getHierarchicalIndices(l)
      
      for i in I:
        k = i * 2**(n-l)
        kl = (i-1) * 2**(n-l)
        kr = (i+1) * 2**(n-l)
        color = "C{}".format(k % 9)
        
        if l > 0:
          x = [X[kl,0], X[k,0], X[kr,0]]
          y = [fX[kl], fX[k], fX[kr]]
        else:
          if i == 1: continue
          x = [X[0,0], X[-1,0]]
          y = [fX[0], fX[-1]]
        
        ax.plot(x, y, "-", color=color, clip_on=False)
        
        for r in range(len(x) - 1):
          if x[r] <= xq <= x[r+1]:
            t = (xq - x[r]) / (x[r+1] - x[r])
            yq = (1 - t) * y[r] + t * y[r+1]
            if l != n: ax.plot([xq - 0.015, xq + 0.015], [yq, yq], "k-")
        
        if l > 0:
          x = [X[k,0], X[k,0]]
          y = [(fX[kl] + fX[kr]) / 2, fX[k]]
          ax.plot(x, y, "--", color=color, clip_on=False, zorder=10)
        else:
          ax.plot([0, 0], [0, fX[0]],  "--", color=color, clip_on=False, zorder=10)
          ax.plot([1, 1], [0, fX[-1]], "--", color=color, clip_on=False, zorder=10)
    
    line, = ax.plot(X, fX, "k.--", clip_on=False, zorder=20)
    line.set_dashes([3, 3])
    
    ax.plot([xq, xq], [0, yq], "k:", clip_on=False)
    ax.plot(xq, yq, "kx", clip_on=False, mew=2)
    ax.text(0.535, 0.8, r"$f^{\mathrm{s}}$", ha="center", va="center")
    ax.text(xq, yq + 0.05, r"$f^{\mathrm{s}}(x)$", ha="left", va="bottom")
  
  #center = (0.1, 0.93)
  #radius = 0.07
  #color = Figure.COLORS["mittelblau"]
  #ax.add_artist(matplotlib.patches.Circle(center, radius, ec="none", fc=color))
  #ax.text(*center, r"$\mathbf{{{}}}$".format(q+1),
  #        ha="center", va="center", color="w")
  
  ax.set_xlim(0, 1)
  ax.set_xticks(xt2 if q == 2 else xt)
  ax.set_xticklabels(xtl2 if q == 2 else xtl)
  
  ax.set_ylim(0, 1)
  ax.set_yticks([0, 1])
  
  fig.save()
