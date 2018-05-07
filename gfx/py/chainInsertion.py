#!/usr/bin/python3
# number of output figures = 4

import random

import numpy as np

import helper.basis
from helper.figure import Figure
import helper.grid



def getChain(l1, i1, l2, i2, T):
  chain = [(np.array(l1), np.array(i1))]
  
  for t in T:
    lNext, iNext = chain[-1]
    lNext, iNext = np.array(lNext), np.array(iNext)
    lNext[t], iNext[t] = l2[t], i2[t]
    chain.append((lNext, iNext))
  
  if np.all(chain[-1][0] == l2) and np.all(chain[-1][1] == i2):
    return chain
  else:
    return None



n, d, b = 3, 2, 1
numberOfRefinements = 20
seed = 1
T = [0, 1]

X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
N = L.shape[0]

grid = helper.grid.SpatiallyAdaptiveSparse(L, I)
refinementCounter = 0
random.seed(seed)

while refinementCounter < numberOfRefinements:
  k = random.randrange(N)
  grid.refine(k)
  newN = grid.L.shape[0]
  
  if newN > N:
    N = newN
    refinementCounter += 1

for q in range(4):
  fig = Figure.create(figsize=(2, 2), scale=1.3)
  ax = fig.gca()
  
  X, L, I = grid.getGrid()
  N = X.shape[0]
  
  ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k-")
  ax.plot(X[:,0], X[:,1], "k.", clip_on=False)
  
  if q >= 1:
    if q == 1:   basis1D = helper.basis.HierarchicalBSpline(1)
    elif q == 2: basis1D = helper.basis.HierarchicalBSpline(3)
    elif q == 3: basis1D = helper.basis.HierarchicalWeaklyFundamentalSpline(3)
    basis = helper.basis.TensorProduct(basis1D, d)
    oldN = 0
    LI = np.hstack((L, I))
    
    while oldN < N:
      print(N)
      oldN = N
      oldX, oldL, oldI = X, L, I
      
      for k1 in range(N):
        for k2 in range(N):
          chain = getChain(L[k1], I[k1], L[k2], I[k2], T)
          x2 = np.array([X[k2]])
          
          for l, i in chain[1:-1]:
            li = np.hstack((l, i))
            
            if abs(basis.evaluate(L[k1], I[k1], x2)) > 1e-10:
              if not np.any(np.all(li == LI, axis=1)):
                LI = np.vstack((LI, li))
      
      L, I = LI[:,:d], LI[:,d:]
      X = helper.grid.getCoordinates(L, I)
      N = L.shape[0]
      
      if N > oldN:
        K = np.any(np.all(np.hstack((oldL, oldI)) ==
                          np.hstack((L, I))[:,np.newaxis], axis=2), axis=1)
        notK = np.logical_not(K)
        ax.plot(X[notK,0], X[notK,1], ".", clip_on=False)
  
  ax.set_axis_off()
  
  fig.save()
