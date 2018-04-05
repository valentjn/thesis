#!/usr/bin/python3

import numpy as np

import helper.function
import helper.grid

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_lagrange_polynomial import HierarchicalLagrangePolynomial

class HierarchicalFundamentalTransformed(HierarchicalBasis):
  def __init__(self, basis, evaluationBasis=None):
    if evaluationBasis is None: evaluationBasis = basis
    super().__init__(nu=evaluationBasis.nu)
    self.basis = basis
    self.evaluationBasis = evaluationBasis
  
  def getCoefficients(self, l, i):
    X, L, I = helper.grid.RegularSparseBoundary(l, 1, 0).generate()
    fX = [int((l == l2) and (i == i2)) for l2, i2 in zip(L, I)]
    c = helper.function.Interpolant(self.basis, X, L, I, fX).aX
    X, L, I = X.flatten(), L.flatten(), I.flatten()
    return c, L, I
  
  def evaluate(self, l, i, XX):
    c, L, I = self.getCoefficients(l, i)
    
    if c is None:
      lagrangePolynomial = HierarchicalLagrangePolynomial(nu=self.evaluationBasis.nu)
      YY = lagrangePolynomial.evaluate(l, i, XX)
    else:
      YY = sum(c2 * self.evaluationBasis.evaluate(l2, i2, XX)
               for c2, l2, i2 in zip(c, L, I))
    
    return YY
  
  def getSupport(self, l, i):
    c, L, I = self.getCoefficients(l, i)
    
    if c is None:
      return 0, 1
    else:
      supports = np.array([self.evaluationBasis.getSupport(l2, i2)
                          for c2, l2, i2 in zip(c, L, I) if c2 != 0])
      return np.min(supports[:,0]), np.max(supports[:,1])
