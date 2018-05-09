#!/usr/bin/python3
# number of output figures = 1

import numpy as np
import scipy.special

import helper.basis
from helper.figure import Figure
import helper.grid

def findLevelIndex(K, l, i):
  lp, ip = helper.grid.convertNodalToHierarchical(l, i)
  return (np.where((K == (lp, ip)).all(axis=1))[0][0])

def dividedDifference(data):
  # data in the form
  # [(a, f(a), df(a), ...), (b, f(b), df(b), ...), ...]
  if len(data) == 1:
    return data[0][-1] / scipy.special.factorial(len(data[0]) - 2)
  else:
    dataLeft = list(data)
    if len(dataLeft[-1]) > 2: dataLeft[-1] = dataLeft[-1][:-1]
    else:                     del dataLeft[-1]
    
    dataRight = list(data)
    if len(dataRight[0]) > 2: dataRight[0] = dataRight[0][:-1]
    else:                     del dataRight[0]
    
    return ((dividedDifference(dataRight) - dividedDifference(dataLeft)) /
            (data[-1][0] - data[0][0]))

def hermiteInterpolation1D(xx, data, nu=0):
  # data in the form
  # [(a, f(a), df(a), ...), (b, f(b), df(b), ...), ...]
  yy = np.zeros((len(xx), nu+1))
  xProduct = [1] + (nu * [0])
  curXData = []
  curData = []
  
  for dataPoint in data:
    x = dataPoint[0]
    curData.append([x])
    
    for k in range(1, len(dataPoint)):
      curData[-1].append(dataPoint[k])
      coeff = dividedDifference(curData)
      
      for q in range(nu, -1, -1):
        yy[:,q] += coeff * xProduct[q]
        xProduct[q] = (xProduct[q] * (xx - x) +
                      q * (xProduct[q-1] if q > 0 else 0))
  
  return yy

def hermiteHierarchization1D(u, n, K, bases):
  N = u.shape[0]
  p = bases[0].p
  y = np.zeros((N,))
  fl = np.zeros((n+1, N, (p+1)//2))
  
  k0 = findLevelIndex(K, 0, 0)
  k1 = findLevelIndex(K, 0, 1)
  
  for i in range(2):
    k = (k0 if i == 0 else k1)
    y[k] = u[k]
    fl[0][k][0] = u[k]
    if p > 1: fl[0][k][1] = (u[k1] - u[k0])
  
  for l in range(1, n+1):
    nodalIl = helper.grid.getNodalIndices(l)
    Kl = np.array([findLevelIndex(K, l, i)
                    for i in nodalIl])
    Xl = helper.grid.getCoordinates(l, nodalIl)
    
    hierIl = np.array(helper.grid.getHierarchicalIndices(l))
    flm1 = np.zeros((len(nodalIl), (p+1)//2))
    
    evenIl = [i for i in nodalIl if i not in hierIl]
    flm1[evenIl] = fl[l-1][Kl[evenIl]]
    
    for i in hierIl:
      data = [np.hstack((Xl[i-1], flm1[i-1])),
              np.hstack((Xl[i+1], flm1[i+1]))]
      flm1[i] = hermiteInterpolation1D(
          [Xl[i]], data, nu=(p-1)//2)
    
    rl = np.zeros_like(nodalIl, dtype=float)
    rl[hierIl] = u[Kl[hierIl]] - flm1[hierIl][:,0]
    
    A = np.zeros((len(hierIl), len(hierIl)))
    for i in hierIl: A[:,(i-1)//2] = bases[0].evaluate(l, i, Xl[hierIl])
    b = rl[hierIl]
    yl = np.linalg.solve(A, b)
    y[Kl[hierIl]] = yl
    
    for q in range((p+1)//2):
      rl = np.zeros_like(nodalIl, dtype=float)
      for i in hierIl: rl += y[Kl[i]] * bases[q].evaluate(l, i, Xl)
      for i in nodalIl: fl[l][Kl[i]][q] = flm1[i][q] + rl[i]
  
  return fl

def getSecant(ax, x, fx, dfx, h):
  d = np.array([1, dfx])
  xl, yl = ax.get_xlim(), ax.get_ylim()
  pos = ax.get_window_extent()
  xScale = pos.width / (xl[1] - xl[0])
  yScale = pos.height / (yl[1] - yl[0])
  d *= h / np.sqrt((d[0]*xScale)**2 + (d[1]*yScale)**2)
  return [x - d[0], x + d[0]], [fx - d[1], fx + d[1]]



n, d, b, p = 3, 1, 0, 3
bases = [helper.basis.HierarchicalWeaklyFundamentalSpline(p, nu=nu)
         for nu in range((p+1)//2)]
grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()
X, L, I = X.flatten(), L.flatten(), I.flatten()
N = X.shape[0]
K = np.column_stack((L, I))
f = (lambda X: 1.2 + np.sin(2.3*np.pi*(X-0.4)) +
               0.3 * np.exp(-(X - 0.7)**2/(2*0.05)) *
                     np.sin(9.8*np.pi*(X-0.34)))
fX = f(X)

fl = hermiteHierarchization1D(fX, n, K, bases)



fig = Figure.create(figsize=(3, 5))
xlim = [0, 1]
ylim = [0, 2.4]

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  ax.set_xlim(xlim)
  ax.set_ylim(ylim)
  
  xx = np.linspace(0, 1, 200)
  ax.plot(xx, f(xx), "-", color="C0", clip_on=False)
  
  Il = helper.grid.getNodalIndices(l)
  Xl = helper.grid.getCoordinates(l, Il)
  
  for i in Il:
    if i < max(Il):
      xl, xr = Xl[i], Xl[i+1]
      xx = np.linspace(xl, xr, 201)
      kl, kr = np.where(X == xl)[0][0], np.where(X == xr)[0][0]
      data = [np.hstack((xl, fl[l][kl])), np.hstack((xr, fl[l][kr]))]
      yy = hermiteInterpolation1D(xx, data)
      ax.plot(xx, yy, "-", color="C1", clip_on=False)
      
      x = (xl + xr) / 2
      ax.plot([x, x], [f(x), yy[100]], "k--", clip_on=False)
      ax.plot(x, yy[100], ".", color="C1", clip_on=False)
      ax.plot(x, f(x), ".", color="C0", clip_on=False)
    
    x = Xl[i]
    k = np.where(X == x)[0][0]
    ax.plot(*getSecant(ax, x, fX[k], fl[l][k,1], h=13), "k-",
            clip_on=(not (0.2 < x < 0.8)))
  
  ax.plot(Xl, f(Xl), "k.", clip_on=False)
  ax.text(1, 2.4, r"$\ell = {}$".format(l), ha="right", va="top")
  
  if l == 0:   x, y = 0.2, 0.95
  elif l == 1: x, y = 0.2, 1.55
  elif l == 2: x, y = 0.15, 0.7
  elif l == 3: x, y = 0.1, 0.75
  
  ax.text(x, y, r"$f_{{{}}}$".format(l),
          color="C1", ha="center", va="bottom")
  
  if l == 0:   x, y = 0.5, 2
  elif l == 1: x, y = 0.5, 2
  elif l == 2: x, y = 0.5, 2
  elif l == 3: x, y = 0.5, 2
  
  ax.text(x, y, r"$f$", color="C0", ha="center", va="bottom")
  
  ax.set_xticks(Xl)
  ax.set_xticklabels(["$x_{{{},{}}}$".format(l, i) for i in Il])

fig.save()
