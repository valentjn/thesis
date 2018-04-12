#!/usr/bin/python3

import unittest

import numpy as np

import helper.basis
import tests.misc

class Test32NotAKnot(tests.misc.CustomTestCase):
  @staticmethod
  def prepareEvaluatePolynomial(C):
    p = np.array(C.shape) - 1
    d = len(p)
    K1Ds = [np.arange(p[t]+1) for t in range(d)]
    Ks = np.meshgrid(*K1Ds, indexing="ij")
    K = helper.grid.flattenMeshGrid(Ks)
    C = C.flatten()
    return C, K
  
  @staticmethod
  def evaluatePolynomial(C, K, XX):
    YY = np.zeros((XX.shape[0],))
    
    for i in range(C.shape[0]):
      YY += C[i] * np.prod(XX**K[i,:], axis=1)
    
    return YY
  
  def testPropSchoenbergWhitneyConditions(self):
    for p in range(5):
      with self.subTest(p=p):
        for q in range(20):
          m = 10
          xiDiff = np.random.random((m+p+1,))
          xi = np.cumsum(xiDiff)
          D = [xi[p], xi[m]]
          
          t = []
          for k in range(m):
            left  = max(xi[k],     xi[p])
            right = min(xi[k+p+1], xi[m])
            center = (right + left) / 2
            radius = (right - left) / 2
            tNew = center + 0.7 * radius * np.random.randn()
            tNew = min(max(tNew, xi[p]), xi[m])
            t.append(tNew)
          
          t.sort()
          valid = (all([xi[k] < t[k] < xi[k+p+1] for k in range(m)]) and
                   all([t[k] < t[k+1] for k in range(m-1)]) and
                   (xi[p] <= t[0]) and (t[m-1] <= xi[m]))
          
          A = np.zeros((m, m))
          for k in range(m):
            basis = helper.basis.NonUniformBSpline(p, xi, k)
            A[:,k] = basis.evaluate(t)
          
          rank = np.linalg.matrix_rank(A)
          
          if valid: self.assertEqual(rank, m)
          else:     self.assertNotEqual(rank, m)
  
  def testPropHierSplittingNAKBSplineUV(self):
    for p in [1, 3, 5, 7]:
      for distribution in ["uniform", "clenshawCurtis"]:
        if distribution == "uniform":
          basis = helper.basis.HierarchicalNotAKnotBSpline(p)
        else:
          basis = helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(p)
        
        basisName = "{}({})".format(type(basis).__name__, p)
        
        for n in range(5):
          h = 1 / 2**n
          
          with self.subTest(n=n, p=p, distribution=distribution):
            ANodal, LNodal, INodal = tests.misc.computeFullGridMatrix(
              basisName, basis, [n], distribution=distribution, hierarchical=False)
            AHier,  LHier,  IHier  = tests.misc.computeFullGridMatrix(
              basisName, basis, [n], distribution=distribution, hierarchical=True)
            
            N = ANodal.shape[0]
            fX = 2 * np.random.random((N,)) - 1
            
            cNodal = np.linalg.solve(ANodal, fX)
            cHier  = np.linalg.solve(AHier,  fX)
            
            xx = np.random.random((10,))
            yyNodal = np.zeros((xx.shape[0],))
            yyHier  = np.zeros((xx.shape[0],))
            
            for k in range(N):
              yyNodal += cNodal[k] * basis.evaluate(LNodal[k], INodal[k], xx)
              yyHier  += cHier[k]  * basis.evaluate(LHier[k],  IHier[k],  xx)
            
            rtol = (1e-7 if (p < 7) or (n < 4) else 1e-5)
            
            self.assertAlmostEqual(yyNodal, yyHier, rtol=rtol)
  
  def testCorHierSplittingNAKBSplineMV(self):
    nPreset = [3, 2, 1, 2]
    bases1D = [[
      helper.basis.HierarchicalNotAKnotBSpline(p),
      helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(p)
    ] for p in [1, 3, 5, 7]]
    bases1D = [y for x in bases1D for y in x]
    
    bases = []
    
    for basis1D in bases1D:
      for d in range(2, 5):
        basisName = type(basis1D).__name__
        if hasattr(basis1D, "p"): basisName += "({})".format(basis1D.p)
        distribution = ("clenshawCurtis" if "ClenshawCurtis" in basisName else
                        "uniform")
        basis = helper.basis.TensorProduct(basis1D, d)
        bases.append((basisName, d, distribution, basis))
    
    for basisName, d, distribution, basis in bases:
      with self.subTest(basis=basisName, d=d):
        n = nPreset[:d]
        ANodal, LNodal, INodal = tests.misc.computeFullGridMatrix(
          basisName, basis, n, distribution=distribution, hierarchical=False)
        AHier,  LHier,  IHier  = tests.misc.computeFullGridMatrix(
          basisName, basis, n, distribution=distribution, hierarchical=True)
        
        N = ANodal.shape[0]
        fX = 2 * np.random.random((N,)) - 1
        
        cNodal = np.linalg.solve(ANodal, fX)
        cHier  = np.linalg.solve(AHier,  fX)
        
        XX = np.random.random((10, d))
        YYNodal = np.zeros((XX.shape[0],))
        YYHier  = np.zeros((XX.shape[0],))
        
        for k in range(N):
          YYNodal += cNodal[k] * basis.evaluate(LNodal[k,:], INodal[k,:], XX)
          YYHier  += cHier[k]  * basis.evaluate(LHier[k,:],  IHier[k,:],  XX)
        
        self.assertAlmostEqual(YYNodal, YYHier)
  
  def testCorSparseGridRegularNAKPolynomials(self):
    b = 0
    
    for d in range(1, 5):
      XX = np.random.random((10, d))
      
      for pScalar in [1, 3, 5]:
        p = pScalar * np.ones((d,), dtype=int)
        C = 2 * np.random.random(p+1) - 1
        C, K = self.prepareEvaluatePolynomial(C)
        
        for distribution in ["uniform", "clenshawCurtis"]:
          if distribution == "uniform":
            basis1D = helper.basis.HierarchicalNotAKnotBSpline(pScalar)
          else:
            basis1D = helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(
                pScalar)
          
          basis = helper.basis.TensorProduct(basis1D, d)
          lowerBound = int(np.sum(np.ceil(np.log2(p + 1))))
          
          for n in range(lowerBound, lowerBound + 2):
            X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
            if distribution != "uniform":
              X = helper.grid.getCoordinates(L, I, distribution=distribution)
            N = X.shape[0]
            if N > 10000: continue
            
            with self.subTest(d=d, n=n, p=pScalar, distribution=distribution):
              A = tests.misc.computeInterpolationMatrix(basis, X, L, I)
              fX = self.evaluatePolynomial(C, K, X)
              aX = np.linalg.solve(A, fX)
              
              YY = np.zeros((XX.shape[0],))
              for k in range(N): YY += aX[k] * basis.evaluate(L[k,:], I[k,:], XX)
              
              fXX = self.evaluatePolynomial(C, K, XX)
              
              valid = ((n >= lowerBound) or (pScalar == 1))
              if valid: self.assertAlmostEqual(YY, fXX)
              else:     self.assertNotAlmostEqual(YY, fXX)



if __name__ == "__main__":
  unittest.main()
