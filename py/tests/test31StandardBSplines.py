#!/usr/bin/python3

import unittest

import numpy as np

import helper.basis

from tests.CustomTestCase import CustomTestCase
import tests.HelperChap2 as HelperChap2

class Test31StandardBSplines(CustomTestCase):
  def testPropSplineSpace(self):
    # copied from Höllig
    pass
  
  def testCorNodalBSplineSpace(self):
    xx = np.random.random((10,))
    
    for p in [1, 3, 5, 7]:
      basis1 = helper.basis.HierarchicalBSpline(p)
      
      for l in range(5):
        hInv = 2**l
        h = 1 / hInv
        m = hInv + 1
        xi = [(k - (p+1)//2) * h for k in range(m+p+1)]
        
        for i in range(m):
          with self.subTest(p=p, l=l, i=i):
            basis2 = helper.basis.NonUniformBSpline(p, xi, i)
            yy1 = basis1.evaluate(l, i, xx)
            yy2 = basis2.evaluate(xx)
            self.assertAlmostEqual(yy1, yy2)
  
  def testLemmaHierBSplineInNodalSpace(self):
    # tested in testCorHierSplittingBSpline
    pass
  
  def testPropHierBSplineLinearlyIndependent(self):
    # tested in testCorHierSplittingBSpline
    pass
  
  def testCorHierSplittingBSpline(self):
    for p in [1, 3, 5, 7]:
      basis = helper.basis.HierarchicalBSpline(p)
      basisName = "{}({})".format(type(basis).__name__, p)
      
      for n in range(5):
        h = 1 / 2**n
        D = [h*(p-1)/2, 1 - h*(p-1)/2]
        if D[0] >= D[1]: continue
        
        for moveXIntoD in [True, False]:
          with self.subTest(n=n, p=p, moveXIntoD=moveXIntoD):
            ANodal, LNodal, INodal = HelperChap2.computeFullGridMatrix(
              basisName, basis, [n], hierarchical=False, moveXIntoD=moveXIntoD)
            AHier,  LHier,  IHier  = HelperChap2.computeFullGridMatrix(
              basisName, basis, [n], hierarchical=True, moveXIntoD=moveXIntoD)
            
            N = ANodal.shape[0]
            fX = 2 * np.random.random((N,)) - 1
            
            cNodal = np.linalg.solve(ANodal, fX)
            cHier  = np.linalg.solve(AHier,  fX)
            
            xx = D[0] + (D[1] - D[0]) * np.random.random((10,))
            yyNodal = np.zeros((xx.shape[0],))
            yyHier  = np.zeros((xx.shape[0],))
            
            for k in range(N):
              yyNodal += cNodal[k] * basis.evaluate(LNodal[k], INodal[k], xx)
              yyHier  += cHier[k]  * basis.evaluate(LHier[k],  IHier[k],  xx)
            
            rtol = (1e-7 if (p < 7) or (n < 4) else 1e-5)
            
            if moveXIntoD or (p == 1):
              self.assertAlmostEqual(yyNodal, yyHier, rtol=rtol)
            else:
              self.assertNotAlmostEqual(yyNodal, yyHier, rtol=rtol)
  
  def testLemmaMarsden(self):
    for p in range(6):
      with self.subTest(p=p):
        m = 10
        xiDiff = np.random.random((m+p+1,))
        xi = np.cumsum(xiDiff)
        D = [xi[p], xi[m]]
        
        N = 10
        X = D[0] + (D[1] - D[0]) * np.random.random((N,))
        Y = 30 * np.random.random((N,)) - 15
        
        for x, y in zip(X, Y):
          lhs = (x - y)**p
          rhs = 0
          
          for k in range(m):
            basis = helper.basis.NonUniformBSpline(p, xi, k)
            c = 1
            for q in range(k+1, k+p+1): c *= (xi[q] - y)
            rhs += c * basis.evaluate([x])[0]
          
          self.assertAlmostEqual(lhs, rhs)



if __name__ == "__main__":
  unittest.main()
