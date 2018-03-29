#!/usr/bin/python3

import numpy as np

import helper.grid
import helper.symbolicSplines

from .hierarchical_basis import HierarchicalBasis

class HierarchicalLagrangePolynomial(HierarchicalBasis):
  def __init__(self, nu=0):
    super().__init__(nu=nu)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def evaluate(self, l, i, xx):
    I = list(range(2**l + 1))
    X = self.getCoordinates(l, I)
    data = [(X[j], int(j == i)) for j in I]
    basis = helper.symbolicSplines.InterpolatingPolynomialPiece(data)
    basis = basis.differentiate(times=self.nu)
    
    if basis.degree >= 1:
      yy = basis.evaluate(xx)
    else:
      c = (basis.coeffs[0] if basis.degree == 0 else 0)
      yy = c * np.ones_like(xx)
    
    return yy
  
  def getSupport(self, l, i):
    return 0, 1
