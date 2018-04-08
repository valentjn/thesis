#!/usr/bin/python3

import random
import unittest

import numpy as np
import scipy.special

import helper.basis
import helper.grid

def findLevelIndex(K, l, i):
  lp, ip = helper.grid.reduceLevelIndex1D(l, i)
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
    
    return((dividedDifference(dataRight) -
            dividedDifference(dataLeft)) /
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

def hermiteHierarchization1D(u, n, K, bases, testCallback=None):
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
    nodalIl = helper.grid.getNodalIndices1D(l)
    Kl = np.array([findLevelIndex(K, l, i) for i in nodalIl])
    Xl = helper.grid.getCoordinates(l, nodalIl)
    
    hierIl = np.array(helper.grid.getHierarchicalIndices1D(l))
    flm1 = np.zeros((len(nodalIl), (p+1)//2))
    
    evenIl = [i for i in nodalIl if i not in hierIl]
    flm1[evenIl] = fl[l-1][Kl[evenIl]]
    
    for i in hierIl:
      data = [np.hstack((Xl[i-1], flm1[i-1])),
              np.hstack((Xl[i+1], flm1[i+1]))]
      flm1[i] = hermiteInterpolation1D([Xl[i]], data, nu=(p-1)//2)
    
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
    
    if testCallback is not None: testCallback(fl, y, l, K, bases)
  
  return y



class Test45SpatAdaptiveUP(unittest.TestCase):
  def assertAllClose(self, a, b, **kwargs):
    self.assertTrue(np.allclose(a, b, **kwargs))
  
  def createDataHermiteHierarchization(self, p):
    n, d, b = 4, 1, 0
    bases = [helper.basis.HierarchicalWeaklyFundamentalSpline(p, nu=nu)
            for nu in range((p+1)//2)]
    grid = helper.grid.RegularSparseBoundary(n, d, b)
    X, L, I = grid.generate()
    X, L, I = X.flatten(), L.flatten(), I.flatten()
    K = np.column_stack((L, I))
    f = (lambda x: 0.3 + np.sin(2.3*np.pi*(X-0.2)))
    fX = f(X)
    
    return bases, n, X, L, I, K, fX
  
  def callbackHermiteHierarchization(self, fl, y, l, K, bases):
    p = bases[0].p
    nodalIl = helper.grid.getNodalIndices1D(l)
    Kl = np.array([findLevelIndex(K, l, i) for i in nodalIl])
    Xl = helper.grid.getCoordinates(l, nodalIl)
    
    for q in range((p+1)//2):
      Yl = np.zeros_like(Xl)
      
      for lp in range(l+1):
        hierIlp = helper.grid.getHierarchicalIndices1D(lp)
        for ip in hierIlp:
          Yl += y[findLevelIndex(K, lp, ip)] * bases[q].evaluate(lp, ip, Xl)
      
      self.assertAllClose(Yl, fl[l][Kl,q])
  
  def testLemmaHermiteInterpolation(self):
    random.seed(42)
    a = random.uniform(0, 3)
    b = a + random.uniform(2, 4)
    
    for p in [1, 3, 5, 7]:
      data = [[a] + [random.gauss(0, 2) for x in range((p+1)//2)],
              [b] + [random.gauss(0, 2) for x in range((p+1)//2)]]
      
      for nu in range((p+1)//2):
        y = hermiteInterpolation1D(np.array([a, b]), data, nu=nu)
        y2 = np.row_stack((data[0][1:nu+2], data[1][1:nu+2]))
        self.assertAllClose(y, y2)
  
  def testPropInvariantHermiteHierarchization(self):
    for p in [1, 3, 5, 7]:
      bases, n, X, L, I, K, fX = self.createDataHermiteHierarchization(p)
      callback = self.callbackHermiteHierarchization
      hermiteHierarchization1D(fX, n, K, bases, testCallback=callback)
  
  def testCorAlgHermiteHierarchizationCorrectness(self):
    for p in [1, 3, 5, 7]:
      bases, n, X, L, I, K, fX = self.createDataHermiteHierarchization(p)
      aX = hermiteHierarchization1D(fX, n, K, bases)
      Y = np.zeros_like(X)
      for k in range(X.shape[0]): Y += aX[k] * bases[0].evaluate(L[k], I[k], X)
      self.assertAllClose(Y, fX)



if __name__ == "__main__":
  unittest.main()
