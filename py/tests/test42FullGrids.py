#!/usr/bin/python3

import functools
import multiprocessing
import unittest

import numpy as np

import helper.basis
import helper.grid
import tests.misc

class Test42FullGrids(tests.misc.CustomTestCase):
  def upCallback(self, X, fX, bases1D, l, hierarchical, y, q, K, T):
    d = len(T)
    curT = T[:q+1]
    notCurT = T[q+1:]
    l = np.array(l)
    KT = np.unique(K[:,curT], axis=0)
    
    XX = X
    YY = np.zeros((XX.shape[0],))
    summand = np.zeros((K.shape[0],))
    
    for kt in KT:
      lt, it = tests.misc.convertContinuousToHierarchical(kt)
      if not hierarchical:
        lt, it = helper.grid.convertHierarchicalToNodal(lt, it, l[curT])
      
      for j, kp in enumerate(K):
        k = np.zeros((d,), dtype=int)
        k[curT] = kt
        k[notCurT] = kp[notCurT]
        j2 = np.where((K == k).all(axis=1))[0]
        summand[j] = y[j2]
      
      for qp, t in enumerate(curT):
        summand *= bases1D[t].evaluate(lt[qp], it[qp], XX[:,t])
      
      YY += summand
    
    fXX = fX
    self.assertAlmostEqual(YY, fXX)
  
  def testPropInvariantUnidirectionalPrinciple(self):
    lPreset = [3, 1, 1, 2]
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      if ("Natural" in basisName) and (d >= 3): continue
      
      for hierarchical in [False, True]:
        with self.subTest(basis=basisName, d=d, hierarchical=hierarchical):
          l = lPreset[:d]
          
          if "Modified" in basisName:
            X, L, I = helper.grid.Full(l).generate()
          else:
            X, L, I = helper.grid.FullBoundary(l).generate()
          
          if not hierarchical:
            L, I = helper.grid.convertHierarchicalToNodal(L, I, l)
          
          if "ClenshawCurtis" in basisName:
            distribution = "clenshawCurtis"
            X = helper.grid.getCoordinates(L, I, distribution=distribution)
          else:
            distribution = "uniform"
          
          N = X.shape[0]
          fX = 2 * np.random.random((N,)) - 1
          
          u = np.array(fX)
          K = tests.misc.convertToContinuous(L, I)
          T = np.arange(d)
          np.random.shuffle(T)
          L1D = functools.partial(tests.misc.hierarchize1D,
                                  basis, distribution, hierarchical)
          bases1D = (basis.basis1D if d > 1 else [basis])
          testCallback = (functools.partial(
              self.upCallback, X, fX, bases1D, l, hierarchical) if d < 4 else
              None)
          y = tests.misc.unidirectionalPrinciple(
            u, K, T, L1D, testCallback=testCallback)
          
          if d == 1: X, L, I = X.flatten(), L.flatten(), I.flatten()
          A = tests.misc.computeInterpolationMatrix(basis, X, L, I)
          aX = np.linalg.solve(A, fX)
          
          self.assertAlmostEqual(y, aX)
  
  def testCorAlgUnidirectionalPrincipleCorrectness(self):
    # tested in testPropInvariantUnidirectionalPrinciple
    pass



if __name__ == "__main__":
  unittest.main()
