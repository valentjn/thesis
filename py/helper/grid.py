#!/usr/bin/python3

import numpy as np
import scipy.special



def getNodalIndices(l):
  if np.isscalar(l):
    I = list(range(2**l + 1))
  else:
    i1D = [getNodalIndices(l1D) for l1D in l]
    meshGrid = np.meshgrid(*i1D, indexing="ij")
    I = np.column_stack([grid.flatten() for grid in meshGrid])
  
  return I

def getHierarchicalIndices(l):
  if np.isscalar(l):
    I = (list(range(1, 2**l, 2)) if l > 0 else [0, 1])
  else:
    i1D = [getHierarchicalIndices(l1D) for l1D in l]
    meshGrid = np.meshgrid(*i1D, indexing="ij")
    I = np.column_stack([grid.flatten() for grid in meshGrid])
  
  return I



def convertNodalToHierarchical(L, I):
  if np.isscalar(L):
    if L == 0:
      pass
    elif I == 0:
      L, I = 0, 0
    else:
      Lp = L - int(np.log2((I ^ (I-1)) + 1) - 1)
      Ip = I // 2**(L - Lp)
      L, I = Lp, Ip
  else:
    L, I = np.array(L), np.array(I)
    N, d = L.shape
    
    for k in range(N):
      for t in range(d):
        L[k,t], I[k,t] = convertNodalToHierarchical(L[k,t], I[k,t])
  
  return L, I

def convertHierarchicalToNodal(L, I, lp):
  L, I = np.array(L), np.array(I)
  I *= 2**(lp - L)
  L = lp * np.ones_like(L)
  return L, I



def getCoordinates(L, I, distribution="uniform"):
  L, I = np.array(L), np.array(I)
  if L.size == 1: L = L * np.ones_like(I)
  
  if distribution == "uniform":
    X = I / 2**L
  elif distribution == "clenshawCurtis":
    HInv = 2**L
    K1 = (I < 0)
    K2 = (I > HInv)
    K = np.logical_not(np.logical_or(K1, K2))
    X = np.zeros(L.shape)
    X[K] = (1 - np.cos(np.pi * I[K] / HInv[K])) / 2
    X[K1] = I[K1] * ((1 - np.cos(np.pi / HInv[K1])) / 2)
    X[K2] = 1 + (I[K2] - HInv[K2]) * ((1 - np.cos(np.pi / HInv[K2])) / 2)
  else:
    raise NotImplementedError("Unknown grid point distribution.")
  
  return X



def generateMeshGrid(nns):
  xxs = [np.linspace(0, 1, nn) if np.isscalar(nn) else nn
         for nn in nns]
  XXs = np.meshgrid(*xxs)
  XX = flattenMeshGrid(XXs)
  return XXs + [XX]

def flattenMeshGrid(XXs):
  XX = np.column_stack([XXt.flatten() for XXt in XXs])
  return XX



class Full(object):
  def __init__(self, l):
    self.l = l
  
  def generate1D(self, l1D):
    return RegularSparse(l1D, 1).generate()
  
  def generate(self):
    X1Ds, L1Ds, I1Ds = [], [], []
    
    for l1D in self.l:
      X1D, L1D, I1D = self.generate1D(l1D)
      X1Ds.append(X1D.flatten())
      L1Ds.append(L1D.flatten())
      I1Ds.append(I1D.flatten())
    
    X = flattenMeshGrid(np.meshgrid(*X1Ds))
    L = flattenMeshGrid(np.meshgrid(*L1Ds))
    I = flattenMeshGrid(np.meshgrid(*I1Ds))
    
    return X, L, I

class FullBoundary(Full):
  def generate1D(self, l1D):
    return RegularSparseBoundary(l1D, 1, 0).generate()



class RegularSparse(object):
  def __init__(self, n, d):
    self.n = n
    self.d = d
  
  def getSize(self):
    if self.n <= 0:
      return (1 if self.d == 0 else 0)
    elif self.d == 0:
      return 1
    elif self.d < 0:
      return 0
    else:
      return sum([2**q * scipy.special.comb(self.d - 1 + q, self.d - 1, exact=True)
                  for q in range(self.n - self.d + 1)])
  
  def generate(self):
    n = self.n
    d = self.d
    N = self.getSize()
    L = np.zeros((N, d), dtype=int)
    I = np.zeros((N, d), dtype=int)
    l = np.ones((d,), dtype=int)
    l1 = d
    i = np.ones((d,), dtype=int)
    t = 0
    m = 0
    
    def generateRecursively():
      nonlocal n, d, L, I, l, l1, i, t, m
      
      if t == d:
        L[m,:] = l
        I[m,:] = i
        m += 1
      elif l1 <= n:
        l[t] += 1
        l1 += 1
        i[t] = 2 * i[t] - 1
        generateRecursively()
        i[t] += 2
        generateRecursively()
        l[t] -= 1
        l1 -= 1
        i[t] = (i[t] - 1) / 2
        
        t += 1
        generateRecursively()
        t -= 1
    
    generateRecursively()
    X = I / 2**L
    
    return X, L, I



class RegularSparseBoundary(object):
  def __init__(self, n, d, b):
    self.n = n
    self.d = d
    self.b = b
  
  def getSize(self):
    if self.b == 0:
      return sum([2**q * scipy.special.comb(self.d, q, exact=True) *
                  RegularSparse(self.n, self.d - q).getSize()
                  for q in range(self.d + 1)])
    elif self.b >= 1:
      return (RegularSparse(self.n, self.d).getSize() +
              sum([2**q * scipy.special.comb(self.d, q, exact=True) *
                   RegularSparse(self.n - q - self.b + 1, self.d - q).getSize()
                   for q in range(1, self.d + 1)]))
    else:
      raise ValueError("Invalid value for b.")
  
  def generate(self, testCallback=None):
    n, d, b = self.n, self.d, self.b
    
    if self.b == 0:
      oldL = [[l] for l in range(n+1)]
      newL = list(oldL)
      
      for t in range(2, d+1):
        newL = []
        
        for l in oldL:
          lNorm = sum(l)
          lStar = n - lNorm
          newL.extend([(*l, lt) for lt in range(0, lStar+1)])
        
        oldL = list(newL)
        if testCallback is not None: testCallback(n, d, b, t, newL)
      
      L = np.array(newL)
    
    elif self.b >= 1:
      oldL = [[l] for l in range(n-d+2)]
      newL = list(oldL)
      
      for t in range(2, d+1):
        newL = []
        
        for l in oldL:
          lNorm = sum(l)
          Nl = sum([lt == 0 for lt in l])
          
          if (lNorm + Nl <= n - d + t - b) or (Nl == t-1):
            newL.append((*l, 0))
          
          if Nl == 0: lStar = n - d + t - lNorm
          else:       lStar = n - d + t - b + 1 - lNorm - Nl
          newL.extend([(*l, lt) for lt in range(1, lStar+1)])
        
        oldL = list(newL)
        if testCallback is not None: testCallback(n, d, b, t, newL)
      
      L = np.array(newL)
    
    else:
      raise ValueError("Invalid value for b.")
    
    return DimensionallyAdaptiveSparse(L).generate()



class DimensionallyAdaptiveSparse(object):
  def __init__(self, L):
    self.L = np.array(L)
  
  def generate(self):
    I = [getHierarchicalIndices(self.L[k,:]) for k in range(self.L.shape[0])]
    
    if len(I) > 0:
      L = np.vstack([np.tile(self.L[k,:], [I[k].shape[0], 1])
                     for k in range(self.L.shape[0])])
      I = np.vstack(I)
    else:
      L = []
    
    X = getCoordinates(L, I)
    return X, L, I



class SpatiallyAdaptiveSparse(object):
  def __init__(self, L, I, distribution="uniform"):
    self.L, self.I = np.array(L), np.array(I)
    self.distribution = distribution
  
  def getGrid(self):
    X = getCoordinates(self.L, self.I, distribution=self.distribution)
    return X, self.L, self.I
  
  def refine(self, k):
    d = self.L.shape[1]
    LI = [tuple([*l, *i]) for l, i in zip(self.L, self.I)]
    li = LI[k]
    LIC = []
    lic = list(li)
    
    for t in range(d):
      lic[t] += 1
      
      for s in [-1, 1]:
        if (li[t] == 0) and (2*li[d+t]-1 == s): continue
        lic[d+t] = 2 * li[d+t] + s
        if tuple(lic) not in LI: LIC.append(list(lic))
      
      lic[t], lic[d+t] = li[t], li[d+t]
    
    if len(LIC) > 0:
      LI = np.vstack((LI, LIC))
      self.L, self.I = LI[:,:d], LI[:,d:]



class SGppGrid(object):
  def __init__(self, grid, *args):
    if type(grid) is str:
      import pysgpp
      self.label = "{}({})".format(grid, ", ".join([str(arg) for arg in args]))
      gridTypes = {
        "bSpline" : pysgpp.Grid.createBsplineBoundaryGrid,
        "bSplineNoBoundary" : pysgpp.Grid.createBsplineGrid,
        "fundamentalSpline" : pysgpp.Grid.createFundamentalSplineBoundaryGrid,
        "fundamentalNotAKnotSpline" :
            pysgpp.Grid.createFundamentalNotAKnotSplineBoundaryGrid,
        "modifiedBSpline" : pysgpp.Grid.createModBsplineGrid,
        "modifiedNotAKnotBSpline" : pysgpp.Grid.createModNotAKnotBsplineGrid,
        "notAKnotBSpline" : pysgpp.Grid.createNotAKnotBsplineBoundaryGrid,
        "weaklyFundamentalNotAKnotSpline" :
            pysgpp.Grid.createLagrangeNotAKnotSplineBoundaryGrid,
        "weaklyFundamentalSpline" :
            pysgpp.Grid.createLagrangeSplineBoundaryGrid,
      }
      grid = gridTypes[grid](*args)
    
    self.grid = grid
  
  def generateRegular(self, *args):
    self.grid.getStorage().clear()
    self.grid.getGenerator().regular(*args)
    return self.getPoints()
  
  def getPoints(self):
    gridStorage = self.grid.getStorage()
    N = gridStorage.getSize()
    d = gridStorage.getDimension()
    L = np.zeros((N, d), dtype=np.uint64)
    I = np.zeros((N, d), dtype=np.uint64)
    
    for k in range(N):
      gp = gridStorage.getPoint(k)
      
      for t in range(d):
        L[k,t] = gp.getLevel(t)
        I[k,t] = gp.getIndex(t)
    
    X = getCoordinates(L, I)
    return X, L, I
  
  def __str__(self):
    return self.label
