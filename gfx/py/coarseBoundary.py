#!/usr/bin/python3
# number of output figures = 8

import numpy as np

from helper.figure import Figure
import helper.grid

d = 2
n = 4
bMax = 3

for b in range(bMax + 1):
  fig = Figure.create(figsize=(2, 2), scale=0.8)
  ax = fig.gca()
  
  ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k-", clip_on=False)
  
  grid = helper.grid.RegularSparseBoundary(n, d, b)
  X, L, _ = grid.generate()
  K1 = np.any(L == 0, axis=1)
  K2 = np.logical_not(K1)
  ax.plot(X[K1,0], X[K1,1], ".", clip_on=False, color=Figure.COLORS["mittelblau"])
  ax.plot(X[K2,0], X[K2,1], "k.", clip_on=False)
  
  ax.set_xlim([0, 1])
  ax.set_ylim([0, 1])
  ax.set_xticks([])
  ax.set_yticks([])
  ax.spines["left"].set_visible(False)
  ax.spines["bottom"].set_visible(False)
  
  fig.save()



d = 3

for b in range(bMax + 1):
  fig = Figure.create(figsize=(2, 2), scale=1.0)
  ax = fig.add_subplot(111, projection="3d")
  
  xs = [[0, 1, 1, 0, 0], [0, 1, 1, 0, 0], [0, 0], [1, 1], [0, 0], [1, 1]]
  ys = [[0, 0, 1, 1, 0], [0, 0, 1, 1, 0], [0, 0], [0, 0], [1, 1], [1, 1]]
  zs = [[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 1], [0, 1], [0, 1], [0, 1]]
  for x, y, z in zip(xs, ys, zs): ax.plot(x, y, "k-", zs=z, clip_on=False)
  
  xs = [[0, 1], [0.5, 0.5], [0.5, 0.5]]
  ys = [[0.5, 0.5], [0, 1], [0.5, 0.5]]
  zs = [[0.5, 0.5], [0.5, 0.5], [0, 1]]
  for x, y, z in zip(xs, ys, zs): ax.plot(x, y, "k--", zs=z, clip_on=False)
  
  grid = helper.grid.RegularSparseBoundary(n, d, b)
  X, L, _ = grid.generate()
  
  K = X[:,1].argsort()
  X, L = X[K,:], L[K,:]
  N = X.shape[0]
  NL = np.sum(L == 0, axis=1)
  
  for k in range(N - 1, -1, -1):
    Nl = NL[k]
    
    if (Nl == 1) and ((X[k,0] == 0) or (X[k,1] == 1) or (X[k,2] == 0)):
      continue
    elif (Nl == 2) and (((X[k,0] == 0) and (X[k,2] == 0)) or
                        ((X[k,1] == 1) and (X[k,2] == 0)) or
                        ((X[k,0] == 0) and (X[k,1] == 1))):
      continue
    elif (X[k,0] == 0) and (X[k,1] == 1) and (X[k,2] == 0):
      continue
    
    if Nl == 0:
      color = "k"
    else:
      color = Figure.COLORS["mittelblau"]
      #factor = X[k,1]
      #color =  [factor * x + (1 - factor) * y
      #          for x, y in zip(Figure.COLORS["mittelblau"], Figure.COLORS["hellblau"])]
     
    ax.plot([X[k,0]], [X[k,1]], ".", zs=[X[k,2]], clip_on=False, color=color)
  
  ax.view_init(30, -65)
  ax.set_axis_off()
  
  fig.save()
