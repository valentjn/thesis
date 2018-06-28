#!/usr/bin/python3
# number of output figures = 5

import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot



d = 3
n = 4
b = 0

colorBoundary = "mittelblau"
colorBoundaryBack = helper.plot.mixColors(colorBoundary, 0.2)
colorInterior = "k"

for q in range(d + 2):
  fig = Figure.create(figsize=(2, 2), scale=0.89)
  ax = fig.add_subplot(111, projection="3d")
  
  grid = helper.grid.RegularSparseBoundary(n, d, b)
  X, L, _ = grid.generate()
  
  K = X[:,1].argsort()
  X, L = X[K,:], L[K,:]
  N = X.shape[0]
  NL = np.sum(L == 0, axis=1)
  
  IsBack = np.logical_and(np.any(L == 0, axis=1),
                          np.logical_and.reduce(X != [1, 0, 1], axis=1))
  
  xs = [[0, 1], [0, 0], [0, 0]]
  ys = [[1, 1], [1, 0], [1, 1]]
  zs = [[0, 0], [0, 0], [0, 1]]
  for x, y, z in zip(xs, ys, zs): ax.plot(x, y, "k-", zs=z, clip_on=False)
  
  for r in range(2):
    if (q <= 1) and (r == 1):
      xs = [[0, 1], [0.5, 0.5], [0.5, 0.5]]
      ys = [[0.5, 0.5], [0, 1], [0.5, 0.5]]
      zs = [[0.5, 0.5], [0.5, 0.5], [0, 1]]
      for x, y, z in zip(xs, ys, zs): ax.plot(x, y, "k--", zs=z, clip_on=False)
    
    for k in range(N - 1, -1, -1):
      isBack = IsBack[k]
      if r == int(isBack): continue
      Nl = NL[k]
      if (q > 0) and (Nl != q-1): continue
      
      if Nl == 0:
        color = colorInterior
      elif isBack:
        color = colorBoundaryBack
      else:
        color = colorBoundary
      
      ax.plot([X[k,0]], [X[k,1]], ".", zs=[X[k,2]], clip_on=False, color=color)
  
  xs = [[1, 1], [0, 1], [0, 0], [0, 0], [0, 1], [1, 1], [0, 1], [1, 1], [1, 1]]
  ys = [[0, 1], [0, 0], [0, 0], [0, 1], [1, 1], [0, 1], [0, 0], [0, 0], [1, 1]]
  zs = [[0, 0], [0, 0], [0, 1], [1, 1], [1, 1], [1, 1], [1, 1], [0, 1], [0, 1]]
  for x, y, z in zip(xs, ys, zs): ax.plot(x, y, "k-", zs=z, clip_on=False)
  
  ax.view_init(30, -65)
  ax.set_axis_off()
  
  fig.save()
