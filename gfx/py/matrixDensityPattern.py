#!/usr/bin/python3
# number of output figures = 1

import matplotlib.patches
import numpy as np

import helper.basis
from helper.figure import Figure
import helper.function
import helper.grid

def plotPopulationStructure(A, ax, pos, size, color):
  tol = 1e-8
  N = A.shape[0]
  h = np.array(size) / N
  
  # k = column index
  for k in range(N):
    x = pos[0] + k * h[0]
    jStart = None
    
    # j = row index
    for j in range(N+1):
      draw = False
      
      if j < N:
        if abs(A[j,k]) >= tol:
          if jStart is None: jStart = j
        elif jStart is not None:
          draw = True
      else:
        draw = (jStart is not None)
      
      if draw:
        y = pos[1] + (N - j) * h[1]
        ax.add_patch(matplotlib.patches.Rectangle(
          (x, y), h[0], (j - jStart) * h[1], edgecolor="none", facecolor=color))
        jStart = None



def plotSGWithSupport(X, l, i, p, ax, pos, size):
  s = lambda x, y: (pos[0] + size[0] * x, pos[1] + size[1] * y)
  basis1D = helper.basis.HierarchicalBSpline(p)
  basis = helper.basis.TensorProduct(basis1D, d)
  lb, ub = basis.getSupport(l, i)
  
  x = helper.grid.getCoordinates(l, i)
  k = np.where((X == x).all(axis=1))[0][0]
  
  edgeColor, brightness = "C0", 0.5
  faceColor = [x + brightness * (1 - x)
              for x in matplotlib.colors.to_rgba(edgeColor)[:3]]
  ax.add_patch(matplotlib.patches.Rectangle(
    s(*lb), *(size * (ub - lb)), edgecolor=edgeColor, facecolor=faceColor))
  
  xSquare, ySquare = np.array([0, 1, 1, 0, 0]), np.array([0, 0, 1, 1, 0])
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  
  if p == 1:
    K = np.logical_and((lb < X), (X < ub)).all(axis=1)
  else:
    K = np.logical_and((lb <= X), (X < ub)).all(axis=1)
  
  K[k] = False
  ax.plot(*s(X[K,0], X[K,1]), ".", clip_on=False, color=edgeColor)
  ax.plot(*s(*x), "x", clip_on=False, mew=2, color=edgeColor)
  
  K = np.logical_not(K)
  K[k] = False
  ax.plot(*s(X[K,0], X[K,1]), "k.", clip_on=False)



def plotSGWithVanishingPoints(X, L, I, l, i, ax, pos, size):
  s = lambda x, y: (pos[0] + size[0] * x, pos[1] + size[1] * y)
  basis1D = helper.basis.HierarchicalBSpline(p)
  basis = helper.basis.TensorProduct(basis1D, d)
  lb, ub = basis.getSupport(l, i)
  
  x = helper.grid.getCoordinates(l, i)
  k = np.where((X == x).all(axis=1))[0][0]
  
  xSquare, ySquare = np.array([0, 1, 1, 0, 0]), np.array([0, 0, 1, 1, 0])
  ax.plot(*s(xSquare, ySquare), "k-", clip_on=False)
  
  color = "C0"
  K = np.logical_or((l < L), np.equal(x, X)).all(axis=1)
  
  K[k] = False
  ax.plot(*s(X[K,0], X[K,1]), ".", clip_on=False, color=color)
  ax.plot(*s(*x), "x", clip_on=False, mew=2, color=color)
  
  K = np.logical_not(K)
  K[k] = False
  ax.plot(*s(X[K,0], X[K,1]), "k.", clip_on=False)



n = 4
d = 2
b = 1
p = 3

l = np.array([2, 2])
i = np.array([1, 1])

grid = helper.grid.RegularSparseBoundary(n, d, b)
X, L, I = grid.generate()
K = np.lexsort((*L.T, np.sum(L, axis=1)))
X, L, I = X[K,:], L[K,:], I[K,:]
N = X.shape[0]

fX = np.zeros((N,))



fig = Figure.create(figsize=(2, 2), scale=2.8)
ax = fig.gca()

xMargin = 0.1
yMargin = 0.1
xTextMargin = 0.1
yTextMargin = 0.1

for q in range(3):
  p = 2 * q + 1
  basis1D = helper.basis.HierarchicalBSpline(p)
  basis = helper.basis.TensorProduct(basis1D, d)
  interpolant = helper.function.Interpolant(basis, X, L, I, fX)
  A = interpolant.getInterpolationMatrix()
  AInv = np.linalg.inv(A)
  
  x, y = q * (1 + xMargin), 0
  plotPopulationStructure(AInv, ax, (x, y), (1, 1), "C1")
  y += 1 + yMargin
  plotPopulationStructure(A, ax, (x, y), (1, 1), "C0")
  y += 1 + yMargin
  plotSGWithSupport(X, l, i, p, ax, (x, y), (1, 1))
  y += 1 + yTextMargin
  
  ax.text(x + 0.5, y, "$p = {}$".format(p), ha="center", va="bottom")

ax.text(-xTextMargin-0.05, 1.5 + yMargin, "$A$",
        ha="right", va="center", color="C0")
ax.text(-xTextMargin, 0.5, "$A^{-1}$",
        ha="right", va="center", color="C1")

ax.set_aspect("equal")
ax.set_xlim(-1, 3 + 2 * xMargin)
ax.set_ylim(0, 4 + 2 * yMargin + yTextMargin)
ax.set_axis_off()

fig.save()



l = np.array([2, 1])
i = np.array([1, 1])

fig = Figure.create(figsize=(2, 2), scale=2.0)
ax = fig.gca()

basis1D = helper.basis.HierarchicalLagrangePolynomial()
basis = helper.basis.TensorProduct(basis1D, d)
interpolant = helper.function.Interpolant(basis, X, L, I, fX)
A = interpolant.getInterpolationMatrix()
AInv = np.linalg.inv(A)

h = (1/N, 1/N)
K = 1 + np.where(np.diff(np.sum(L, axis=1)))[0]

#x, y = 0, 0
#plotPopulationStructure(AInv, ax, (x, y), (1, 1), "C1")
#for k in K:
#  xLine, yLine = x + k * h[0], y + (N - k) * h[1]
#  ax.plot([x, x+1], [yLine, yLine], "k-")
#  ax.plot([xLine, xLine], [y, y+1], "k-")

y += 1 + yMargin
plotPopulationStructure(A, ax, (x, y), (1, 1), "C0")
for k in K:
  xLine, yLine = x + k * h[0], y + (N - k) * h[1]
  ax.plot([x, x+1], [yLine, yLine], "k-")
  ax.plot([xLine, xLine], [y, y+1], "k-")

y += 1 + yMargin
plotSGWithVanishingPoints(X, L, I, l, i, ax, (x, y), (1, 1))

ax.set_aspect("equal")
ax.set_axis_off()

fig.save()
