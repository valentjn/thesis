#!/usr/bin/python3

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import pysgpp

import helper.basis
import helper.function
import helper.grid

f = "beale"
d = 2
p = 3
b = 1
ns = list(range(1, 8))
grids = [
  helper.grid.SGppGrid("bSpline", d, p, b),
  helper.grid.SGppGrid("notAKnotBSpline", d, p, b),
  helper.grid.SGppGrid("modifiedBSpline", d, p),
  helper.grid.SGppGrid("modifiedNotAKnotBSpline", d, p),
  helper.grid.SGppGrid("bSplineNoBoundary", d, p),
  helper.grid.SGppGrid("notAKnotBSpline", d, p, 100),
]

f = helper.function.SGppTestFunction(f, d)

fig = plt.figure()
#ax = fig.add_subplot(111, projection="3d")
ax = fig.gca()
XX0, XX1, XX = helper.grid.generateMeshGrid((100, 100))

Ns=  np.zeros((len(grids), len(ns)))
errors = np.zeros((len(grids), len(ns)))

for q, grid in enumerate(grids):
  basis1D = helper.basis.SGppBasis(grid.grid.getBasis())
  basis = helper.basis.TensorProduct(basis1D, d)
  
  for r, n in enumerate(ns):
    grid.generateRegular(n)
    X, L, I = grid.getPoints()
    if q == 5:
      K = np.any(L == 0, axis=1).nonzero()[0].tolist()
      K = pysgpp.IndexList(K)
      grid.grid.getStorage().deletePoints(K)
      X, L, I = grid.getPoints()
    fX = f.evaluate(X)
    #fInterp = helper.function.Interpolant(basis, X, L, I, fX)
    fInterp = helper.function.SGppInterpolant(grid.grid, fX)
    YY = np.reshape(fInterp.evaluate(XX), XX0.shape)
    
    #ax.plot_surface(XX0, XX1, YY)
    errors[q, r] = f.computeRelativeL2Error(fInterp)
    Ns[q, r] = X.shape[0]

for q, _ in enumerate(grids):
  ax.plot(Ns[q,:], errors[q,:], ".-")

ax.set_xscale("log")
ax.set_yscale("log")
ax.legend([str(grid) for grid in grids])

plt.show()
