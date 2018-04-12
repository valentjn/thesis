#!/usr/bin/python3

import unittest

import helper.grid
import tests.misc

class Test24Boundary(tests.misc.CustomTestCase):
  def checkGridSizes(self, gridFunction, examples=[], skipFunction=None):
    for d in range(1, 6):
      for n in range(7):
        if skipFunction is not None:
          if skipFunction(n, d): continue
        
        with self.subTest(n=n, d=d):
          grid = gridFunction(n, d)
          X, _, _ = grid.generate()
          self.assertEqual(X.shape[0], grid.getSize())
    
    for n, d, size in examples:
      with self.subTest(n=n, d=d):
        grid = gridFunction(n, d)
        X, _, _ = grid.generate()
        self.assertEqual(X.shape[0], grid.getSize())
        self.assertEqual(X.shape[0], size)
  
  def coarseTestCallback(self, n, d, b, t, L):
    for l in L:
      self.assertEqual(len(l), t)
      if all([x >= 1 for x in l]):
        self.assertLessEqual(sum(l), n-d+t)
      else:
        if not all([x == 0 for x in l]):
          self.assertLessEqual(sum([max(x, 1) for x in l]), n-d+t-b+1)
  
  def testLemmaNumberOfGridPointsBoundary(self):
    b = 0
    gridFunction = (lambda n, d: helper.grid.RegularSparseBoundary(n, d, b))
    examples = [(5, 1, 33), (6, 2, 385), (10, 6, 2912257)]
    self.checkGridSizes(gridFunction, examples=examples)
  
  def testLemmaNumberOfGridPointsInterior(self):
    gridFunction = (lambda n, d: helper.grid.RegularSparse(n, d))
    examples = [(5, 1, 31), (6, 2, 129), (10, 6, 2561)]
    self.checkGridSizes(gridFunction, examples=examples)
  
  def testPropGridSizeCoarseBoundary(self):
    for b in range(1, 6):
      gridFunction = (lambda n, d: helper.grid.RegularSparseBoundary(n, d, b))
      skipFunction = (lambda n, d: (n < d))
      self.checkGridSizes(gridFunction, skipFunction=skipFunction)
  
  def testPropInvariantCoarseBoundary(self):
    for b in range(1, 6):
      for d in range(1, 6):
        for n in range(7):
          if n < d: continue
          grid = helper.grid.RegularSparseBoundary(n, d, b)
          grid.generate(testCallback=self.coarseTestCallback)
  
  def testCorAlgCoarseBoundaryCorrectness(self):
    for b in range(1, 6):
      for d in range(1, 6):
        for n in range(7):
          if n < d: continue
          grid = helper.grid.RegularSparseBoundary(n, d, b)
          X, L, I = grid.generate()
          self.coarseTestCallback(n, d, b, d, L)



if __name__ == "__main__":
  unittest.main()
