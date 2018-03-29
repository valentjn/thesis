#!/usr/bin/python3

import numpy as np

import helper.function
import helper.grid

from .hierarchical_basis import HierarchicalBasis

class HierarchicalFundamentalTransformed(HierarchicalBasis):
  def __init__(self, basis):
    super().__init__(nu=basis.nu)
    self.basis = basis
  
  def getCoefficients(self, l, i):
    X, L, I = helper.grid.RegularSparseBoundary(l, 1, 0).generate()
    fX = [int((l == l2) and (i == i2)) for l2, i2 in zip(L, I)]
    c = helper.function.Interpolant(self.basis, X, L, I, fX).aX
    return c, L, I
  
  def evaluate(self, l, i, XX):
    c, L, I = self.getCoefficients(l, i)
    YY = sum(c2 * self.basis.evaluate(l2, i2, XX)
             for c2, l2, i2 in zip(c, L, I))
    return YY
  
  def getSupport(self, l, i):
    c, L, I = self.getCoefficients(l, i)
    supports = np.array([self.basis.getSupport(l2, i2)
                         for c2, l2, i2 in zip(c, L, I) if c2 != 0])
    return np.min(supports[:,0]), np.max(supports[:,1])
