#!/usr/bin/python3

import queue
import unittest

import numpy as np
import scipy.optimize

import helper.basis
import helper.function
import tests.misc

class Test44SpatAdaptiveBFS(tests.misc.CustomTestCase):
  @staticmethod
  def getExampleHierarchicalFundamentalBases():
    bases1D = [[
      #helper.basis.HierarchicalClenshawCurtisLagrangePolynomial(),
      #helper.basis.HierarchicalLagrangePolynomial(),
      helper.basis.HierarchicalBSpline(1),
      helper.basis.HierarchicalClenshawCurtisBSpline(1),
      helper.basis.ModifiedHierarchicalBSpline(1),
      helper.basis.ModifiedHierarchicalClenshawCurtisBSpline(1),
    ]] + [[
      helper.basis.HierarchicalFundamentalSpline(p),
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
  
  @staticmethod
  def isChild1D(l, i, lp, ip):
    if lp == 0:
      return (l == 1) and (i == 1)
    else:
      return (l == lp + 1) and ((i == 2*ip-1) or (i == 2*ip+1))
  
  @staticmethod
  def isChild(l, i, lp, ip):
    if isinstance(l, np.ndarray):
      d = len(l)
      T = [t for t in range(d) if (l[t] != lp[t]) or (i[t] != ip[t])]
      return ((len(T) == 1) and Test44SpatAdaptiveBFS.isChild1D(
          l[T[0]], i[T[0]], lp[T[0]], ip[T[0]]))
    else:
      return Test44SpatAdaptiveBFS.isChild1D(l, i, lp, ip)
  
  @staticmethod
  def breadthFirstSearch(u, X, L, I, basis, modified=False, testCallback=None):
    y = np.array(u)
    d = (L.shape[1] if L.ndim > 1 else 1)
    N = L.shape[0]
    
    if modified:
      ones = np.ones((d,), dtype=int)
      Kp = [(ones, ones)]
    else:
      zeroI = helper.grid.flattenMeshGrid(
          np.meshgrid(*[[0, 1] for t in range(d)]))
      zeros = np.zeros((d,), dtype=int)
      Kp = [(zeros, i) for i in zeroI]
    
    LI = np.column_stack((L, I))
    Kp = [np.where(np.all(LI == np.hstack((l, i)), axis=1))[0][0]
          for l, i in Kp]
    
    Q = queue.Queue()
    for k in Kp: Q.put(k)
    lastLevelSum = np.sum(L[Kp[-1]])
    
    while not Q.empty():
      kp = Q.get()
      levelSum = np.sum(L[kp])
      
      if (testCallback is not None) and (levelSum > lastLevelSum):
        testCallback(u, X, L, I, basis, levelSum, y)
        lastLevelSum = levelSum
      
      for k in range(N):
        if (k != kp) and np.any(np.logical_or((L[kp] < L[k]),
              np.logical_and(np.equal(L[kp], L[k]), np.equal(I[kp], I[k])))):
          y[k] -= y[kp] * basis.evaluate(L[kp], I[kp], np.array([X[k]]))[0]
      
      for k in range(N):
        if ((k not in Kp) and
            Test44SpatAdaptiveBFS.isChild(L[k], I[k], L[kp], I[kp])):
          Q.put(k)
          Kp.append(k)
    
    return y
  
  def bfsCallback(self, fX, X, L, I, basis, q, y):
    N = X.shape[0]
    
    for k in range(N):
      if np.sum(L[k]) == q:
        x = np.array([X[k]])
        rhs = fX[k]
        
        for kp in range(N):
          if np.sum(L[kp]) < q:
            rhs -= y[kp] * basis.evaluate(L[kp], I[kp], x)
        
        if isinstance(rhs, np.ndarray): rhs = rhs[0]
        self.assertAlmostEqual(y[k], rhs, rtol=1e-6, atol=1e-10)
  
  def testLemmaForwardSubstitution(self):
    bases = self.getExampleHierarchicalFundamentalBases()
    
    for basisName, d, basis in bases:
      f = tests.misc.getObjectiveFunction(d)
      modified = ("Modified" in basisName)
      if "ClenshawCurtis" in basisName: distribution = "clenshawCurtis"
      else:                             distribution = "uniform"
      
      if d >= 4: continue
      
      with self.subTest(basis=basisName, d=d):
        X, L, I = tests.misc.generateSpatiallyAdaptiveSparseGrid(
            d, 100, distribution=distribution, withBoundary=(not modified))
        fX = f(X)
        interpolant = helper.function.Interpolant(basis, X, L, I, fX)
        aX = interpolant.aX
        N = X.shape[0]
        if d == 1: X, L, I = X.flatten(), L.flatten(), I.flatten()
        
        for k in range(N):
          x = np.array([X[k]])
          lSum = np.sum(L[k])
          rhs = fX[k]
          
          for kp in range(N):
            if np.sum(L[kp]) < lSum:
              rhs -= aX[kp] * basis.evaluate(L[kp], I[kp], x)
          
          if isinstance(rhs, np.ndarray): rhs = rhs[0]
          self.assertAlmostEqual(aX[k], rhs, rtol=1e-6, atol=1e-10)
  
  def testPropInvariantBFS(self):
    bases = self.getExampleHierarchicalFundamentalBases()
    
    for basisName, d, basis in bases:
      f = tests.misc.getObjectiveFunction(d)
      modified = ("Modified" in basisName)
      if "ClenshawCurtis" in basisName: distribution = "clenshawCurtis"
      else:                             distribution = "uniform"
      
      with self.subTest(basis=basisName, d=d):
        X, L, I = tests.misc.generateSpatiallyAdaptiveSparseGrid(
            d, 100, distribution=distribution, withBoundary=(not modified))
        fX = f(X)
        interpolant = helper.function.Interpolant(basis, X, L, I, fX)
        aX = interpolant.aX
        if d == 1: X, L, I = X.flatten(), L.flatten(), I.flatten()
        
        u = fX
        testCallback = self.bfsCallback
        y = self.breadthFirstSearch(u, X, L, I, basis, modified=modified,
                                    testCallback=testCallback)
        
        self.assertAlmostEqual(y, aX)
  
  def testCorAlgBFSCorrectness(self):
    # tested in testPropInvariantBFS
    pass
  
  def testPropHftSparseGridSpace(self):
    n, b = 4, 0
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      if "ClenshawCurtis" in basisName: continue
      if "Modified" in basisName: continue
      if ("HierarchicalNaturalBSpline" in basisName) and (d >= 2): continue
      if d >= 4: continue
      
      f = tests.misc.getObjectiveFunction(d)
      XX = np.random.random((10, d))
      
      with self.subTest(basis=basisName, d=d):
        basis1D = (basis.basis1D[0]
                  if isinstance(basis, helper.basis.TensorProduct) else
                  basis)
        basis1DTrafo = helper.basis.HierarchicalFundamentalTransformed(basis1D)
        basisTrafo = (helper.basis.TensorProduct(basis1DTrafo, d) if d > 1 else
                      basis1DTrafo)
        
        X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
        fX = f(X)
        
        lhsInterpolant = helper.function.Interpolant(basis, X, L, I, fX)
        lhsYY = lhsInterpolant.evaluate(XX)
        
        rhsInterpolant = helper.function.Interpolant(basisTrafo, X, L, I, fX)
        rhsYY = rhsInterpolant.evaluate(XX)
        
        self.assertAlmostEqual(lhsYY, rhsYY)
  
  # cannot be tested (too theoretical)
  #def testPropTiftNodalSpace(self):
  #  raise NotImplementedError
  
  def testThmFundamentalSplineExistence(self):
    for p in range(1, 16, 2):
      with self.subTest(p=p):
        basis = helper.basis.FundamentalSpline(p)
        gamma = (basis.gamma if p > 1 else np.exp(1))
        
        upperBound = (lambda beta, x:
                      beta * np.exp(-np.abs(x) * np.log(gamma)))
        objFun = (lambda x: -np.abs(basis.evaluate(np.array([x]))[0]) /
                  upperBound(1, x))
        result = scipy.optimize.minimize_scalar(
            objFun, bounds=(0, 1), method="bounded")
        beta = -result.fun
        
        beta += 1e-10
        
        xx = 200 * np.random.random((1000000,)) - 100
        yy = basis.evaluate(xx)
        self.assertLess(np.min(np.abs(yy) - upperBound(beta, xx)), 1e-10)



if __name__ == "__main__":
  unittest.main()
