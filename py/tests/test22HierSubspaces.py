#!/usr/bin/python3

import random
import unittest

import numpy as np

import helper.basis
import tests.misc

class Test22HierSubspaces(tests.misc.CustomTestCase):
  # cannot be tested (too theoretical)
  #def testLemmaHierSplittingUV(self):
  #  raise NotImplementedError
  
  def testCorHierSplittingHatUV(self):
    p = 1
    bases1D = [
      helper.basis.HierarchicalBSpline(p),
      helper.basis.HierarchicalClenshawCurtisLagrangePolynomial(),
      helper.basis.HierarchicalLagrangePolynomial(),
    ]
    
    bases = []
    
    for basis1D in bases1D:
      basisName = type(basis1D).__name__
      if hasattr(basis1D, "p"): basisName += "({})".format(basis1D.p)
      basis = basis1D
      bases.append((basisName, basis))
    
    for basisName, basis in bases:
      for n in range(5):
        with self.subTest(basis=basisName, n=n):
          ANodal, LNodal, INodal = tests.misc.computeFullGridMatrix(
            basisName, basis, [n], hierarchical=False)
          AHier,  LHier,  IHier  = tests.misc.computeFullGridMatrix(
            basisName, basis, [n], hierarchical=True)
          
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
          
          self.assertAlmostEqual(yyNodal, yyHier)
  
  # cannot be tested (too theoretical)
  #def testLemmaHierSplittingMV(self):
  #  raise NotImplementedError
  
  # cannot be tested (too theoretical)
  #def testPropSplittingUVToMV(self):
  #  raise NotImplementedError
  
  def testCorHierSplittingHatMV(self):
    nPreset, p = [3, 2, 1, 2], 1
    bases1D = [
      helper.basis.HierarchicalBSpline(p),
      helper.basis.HierarchicalClenshawCurtisLagrangePolynomial(),
      helper.basis.HierarchicalLagrangePolynomial(),
    ]
    
    bases = []
    
    for basis1D in bases1D:
      for d in range(2, 5):
        basisName = type(basis1D).__name__
        if hasattr(basis1D, "p"): basisName += "({})".format(basis1D.p)
        basis = helper.basis.TensorProduct(basis1D, d)
        bases.append((basisName, d, basis))
    
    for basisName, d, basis in bases:
      with self.subTest(basis=basisName, d=d):
        n = nPreset[:d]
        ANodal, LNodal, INodal = tests.misc.computeFullGridMatrix(
          basisName, basis, n, hierarchical=False)
        AHier,  LHier,  IHier  = tests.misc.computeFullGridMatrix(
          basisName, basis, n, hierarchical=True)
        
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



if __name__ == "__main__":
  unittest.main()
