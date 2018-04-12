#!/usr/bin/python3

import unittest

import numpy as np

import helper.basis
import tests.misc

class Test21NodalSpaces(tests.misc.CustomTestCase):
  def testLemmaTensorProductLinearIndependence(self):
    lPreset = [3, 1, 1, 2]
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      with self.subTest(basis=basisName, d=d):
        l = lPreset[:d]
        A, L, I = tests.misc.computeFullGridMatrix(basisName, basis, l)
        rank = np.linalg.matrix_rank(A)
        self.assertEqual(rank, L.shape[0])



if __name__ == "__main__":
  unittest.main()
