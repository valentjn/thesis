#!/usr/bin/python3

import numpy as np

import helper.function
import helper.grid

from .hierarchical_fundamental_transformed import HierarchicalFundamentalTransformed

class NodalFundamentalTransformed(HierarchicalFundamentalTransformed):
  def __init__(self, basis, evaluationBasis=None):
    super().__init__(basis, evaluationBasis=evaluationBasis)
  
  def getCoefficients(self, l, i):
    hInv = 2**l
    L = l * np.ones((hInv + 1, 1), dtype=int)
    I = np.reshape(np.array(range(hInv + 1)), (hInv + 1, 1))
    X = helper.grid.getCoordinates(L, I)
    fX = [int(i == i2) for i2 in I]
    c = helper.function.Interpolant(self.basis, X, L, I, fX).aX
    X, L, I = X.flatten(), L.flatten(), I.flatten()
    return c, L, I
