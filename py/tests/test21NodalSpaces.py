#!/usr/bin/python3

import unittest

import numpy as np

import helper.basis

from tests.CustomTestCase import CustomTestCase
import tests.HelperChap2 as HelperChap2

class Test21NodalSpaces(CustomTestCase):
  def testLemmaTensorProductLinearIndependence(self):
    lPreset = [3, 1, 1, 2]
    bases = HelperChap2.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      with self.subTest(basis=basisName, d=d):
        l = lPreset[:d]
        A, L, I = HelperChap2.computeFullGridMatrix(basisName, basis, l)
        rank = np.linalg.matrix_rank(A)
        self.assertEqual(rank, L.shape[0])



if __name__ == "__main__":
  unittest.main()
