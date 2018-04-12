#!/usr/bin/python3

import functools
import multiprocessing

import numpy as np

import helper.basis
import helper.grid
import helper.misc



def computeInterpolationMatrixColumn(basis, X, l, i):
  return basis.evaluate(l, i, X)



def computeInterpolationMatrix(basis, X, L, I, parallel=True):
  if parallel:
    with multiprocessing.Pool() as pool:
      columns = pool.starmap(functools.partial(
        computeInterpolationMatrixColumn, basis, X), zip(L, I))
    A = np.column_stack(columns)
  else:
    N = X.shape[0]
    A = np.zeros((N, N))
    for k in range(N):
      A[:,k] = computeInterpolationMatrixColumn(basis, X, L[k], I[k])
  
  return A



def computeFullGridMatrix(
    basisName, basis, l, hierarchical=False, moveXIntoD=False,
    distribution="uniform", parallel=True):
  d = len(l)
  
  if "Modified" in basisName:
    X, L, I = helper.grid.Full(l).generate()
  else:
    X, L, I = helper.grid.FullBoundary(l).generate()
  
  if distribution != "uniform":
    X = helper.grid.getCoordinates(L, I, distribution=distribution)
  if not hierarchical: L, I = helper.grid.convertHierarchicalToNodal(L, I, l)
  if d == 1: X, L, I = X.flatten(), L.flatten(), I.flatten()
  
  if moveXIntoD:
    assert d == 1
    assert hasattr(basis, "p")
    p = basis.p
    h = 1 / 2**(l[0])
    X = np.linspace(h*(p-1)/2, 1 - h *(p-1)/2, X.shape[0])
  
  A = computeInterpolationMatrix(basis, X, L, I, parallel=parallel)
  return A, L, I



def getExampleHierarchicalBases():
  bases1D = []
  
  bases1D += [[
    helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(p),
    helper.basis.HierarchicalNotAKnotBSpline(p),
    helper.basis.ModifiedHierarchicalClenshawCurtisNotAKnotBSpline(p),
    helper.basis.ModifiedHierarchicalNotAKnotBSpline(p),
  ] for p in [1, 3, 5, 7]]
  
  bases1D += [[
    helper.basis.HierarchicalClenshawCurtisLagrangePolynomial(),
    helper.basis.HierarchicalLagrangePolynomial(),
  ]]
  
  bases1D += [[
    helper.basis.HierarchicalBSpline(p),
    helper.basis.HierarchicalClenshawCurtisBSpline(p),
    helper.basis.HierarchicalFundamentalSpline(p),
    helper.basis.HierarchicalNaturalBSpline(p),
    helper.basis.HierarchicalWeaklyFundamentalSpline(p),
    helper.basis.ModifiedHierarchicalBSpline(p),
    helper.basis.ModifiedHierarchicalClenshawCurtisBSpline(p),
    helper.basis.ModifiedHierarchicalFundamentalSpline(p),
  ] for p in [1, 3, 5, 7]]
  
  bases1D = [y for x in bases1D for y in x]
  bases = []
  
  for basis1D in bases1D:
    if ((type(basis1D) is helper.basis.HierarchicalNaturalBSpline) and
        (basis1D.p > 5)):
      continue
    
    for d in range(1, 5):
      basisName = type(basis1D).__name__
      if hasattr(basis1D, "p"): basisName += "({})".format(basis1D.p)
      basis = (helper.basis.TensorProduct(basis1D, d) if d > 1 else basis1D)
      bases.append((basisName, d, basis))
  
  return bases



def getObjectiveFunction(d):
  return functools.partial(evaluateObjectiveFunction, d)

def evaluateObjectiveFunction(d, X):
  Y = 0.3 + np.sin(2.3 * np.pi *
                   np.prod(np.reshape(X-0.2, (-1,d)), axis=1))
  return Y



def generateSpatiallyAdaptiveSparseGrid(
      d, NMax, lMax=10, distribution="uniform", withBoundary=True):
  if withBoundary: l = np.zeros((d,), dtype=int)
  else:            l = np.ones((d,), dtype=int)
  I = helper.grid.getHierarchicalIndices(l)
  L = l * np.ones_like(I)
  LI = np.column_stack((L, I))
  N = LI.shape[0]
  
  while N + 2*d <= NMax:
    k = np.random.randint(N)
    li = LI[k,:]
    lip = np.array(li)
    
    for t in range(d):
      if li[t] == 0:
        lip[t] = 1
        lip[d+t] = 1
        LI = np.row_stack((LI, lip))
      else:
        lip[t] = li[t] + 1
        lip[d+t] = 2 * li[d+t] - 1
        LI = np.row_stack((LI, lip))
        lip[d+t] += 2
        LI = np.row_stack((LI, lip))
      
      lip[t], lip[d+t] = li[t], li[d+t]
    
    LI = np.unique(LI, axis=0)
    LI = LI[np.all((LI[:,:d] <= lMax), axis=1)]
    N = LI.shape[0]
  
  L, I = LI[:,:d], LI[:,d:]
  X = helper.grid.getCoordinates(L, I, distribution=distribution)
  return X, L, I



def convertToContinuous(L, I):
  L2, I2 = helper.grid.convertNodalToHierarchical(L, I)
  K = np.zeros_like(L2)
  J = (L2 >= 1)
  notJ = np.logical_not(J)
  K[J] = 2**(L2[J]-1) + (I2[J]+1)//2
  K[notJ] = I2[notJ]
  return K

def convertContinuousToHierarchical(K):
  L = np.zeros_like(K)
  I = np.zeros_like(K)
  J = (K >= 2)
  notJ = np.logical_not(J)
  L[J] = np.floor(np.log2(K[J]-1)).astype(int) + 1
  I[J] = 2 * (K[J] - 2**(L[J]-1)) - 1
  I[notJ] = K[notJ]
  return L, I

def isOnSamePole(t, d, k1, k2):
  return (np.all(k1[:t] == k2[:t]) and np.all(k1[t+1:d] == k2[t+1:d]))

def processPole(t, u, L1D, KJPole):
  KJPole = np.row_stack(KJPole)
  KPole, JPole = KJPole[:,:-1], KJPole[:,-1]
  KPole1D = KPole[:,t]
  y = L1D(u[JPole], t, KPole1D)
  return (y, JPole)

def unidirectionalPrinciple(u, K, T, L1D, testCallback=None):
  y = np.array(u)
  d = len(T)
  J = np.arange(K.shape[0])
  KJ = np.column_stack((K, J))
  
  with multiprocessing.Pool() as pool:
    for q, t in enumerate(T):
      KJPoles = helper.misc.getEquivalenceClasses(
          KJ, functools.partial(isOnSamePole, t, d))
      
      #for KJPole in KJPoles:
      #  KJPole = np.row_stack(KJPole)
      #  KPole, JPole = KJPole[:,:-1], KJPole[:,-1]
      #  KPole1D = KPole[:,t]
      #  y[JPole] = L1D(y[JPole], t, KPole1D)
      
      yJPoles = pool.map(functools.partial(processPole, t, y, L1D), KJPoles)
      
      for yPole, JPole in yJPoles:
        y[JPole] = yPole
      
      if testCallback is not None: testCallback(y, q, K, T)
  
  return y

def hierarchize1D(basis, distribution, hierarchical, u, t, K,
                  mode="hierarchize"):
  L, I = convertContinuousToHierarchical(K)
  if not hierarchical:
    L, I = helper.grid.convertHierarchicalToNodal(L, I, np.max(L))
  
  basis1D = (
    basis.basis1D[t] if isinstance(basis, helper.basis.TensorProduct) else
    basis)
  
  X = helper.grid.getCoordinates(L, I, distribution=distribution)
  A = computeInterpolationMatrix(basis1D, X, L, I, parallel=False)
  
  if mode == "hierarchize":
    return np.linalg.solve(A, u)
  elif mode == "dehierarchize":
    return np.dot(A, u)
  elif mode == "matrix":
    return A
  else:
    raise ValueError("Unknown mode.")
