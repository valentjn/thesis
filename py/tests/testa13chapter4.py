#!/usr/bin/python3

import unittest

import numpy as np
import scipy.special

import helper.grid
import tests.misc

class Test24Boundary(tests.misc.CustomTestCase):
  @staticmethod
  def enumerateLevelsWithSum(n, d):
    if (d <= 0) or (n < 0):
      L = []
    elif d == 1:
      L = [[n]]
    elif n == 0:
      L = [d * [0]]
    else:
      L = [[l1] + l
           for l1 in range(n+1)
           for l in Test24Boundary.enumerateLevelsWithSum(n-l1, d-1)]
    
    return L
  
  def testLemmaInclusionExclusionCountingLemma(self):
    nck = (lambda n, k: scipy.special.comb(n, k, exact=True))
    
    for a in range(20):
      for r in range(a, 21):
        for s in range(-20, 21):
          with self.subTest(a=a, r=r, s=s):
            lhs = sum([(-1)**q * nck(a, q) * nck(r-q, s)
                       for q in range(a+1)])
            rhs = nck(r-a, s-a)
            self.assertEqual(lhs, rhs)
  
  def testLemmaCombiTechniqueEquivalenceRelation(self):
    b = 0
    
    for d in range(1, 5):
      for n in range(8-d):
        with self.subTest(d=d, n=n):
          X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
          N = X.shape[0]
          
          for k in range(N):
            Ls = [l for q in range(d)
                for l in self.enumerateLevelsWithSum(n-q, d)
                if not np.all(L[k,:] <= l)]
            
            if len(Ls) == 0: continue
            
            isEquivalent = (lambda l1, l2:
                all([((l1[t] == l2[t] < L[k,t]) or
                      (min(l1[t], l2[t]) >= L[k,t]))
                     for t in range(d)]))
            
            for l1 in Ls:
              self.assertTrue(isEquivalent(l1, l1))
              
              for l2 in Ls:
                if isEquivalent(l1, l2):
                  self.assertTrue(isEquivalent(l2, l1))
                  
                  for l3 in Ls:
                    if isEquivalent(l2, l3):
                      self.assertTrue(isEquivalent(l1, l3))
                else:
                  self.assertFalse(isEquivalent(l2, l1))



if __name__ == "__main__":
  unittest.main()
