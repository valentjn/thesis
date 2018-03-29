#!/usr/bin/python3

import helper.grid
import helper.symbolicSplines

from .hierarchical_basis import HierarchicalBasis

class HierarchicalLagrangePolynomial(HierarchicalBasis):
  def __init__(self, nu=0):
    super().__init__()
    assert nu == 0
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def evaluate(self, l, i, xx):
    I = list(range(2**l + 1))
    X = self.getCoordinates(l, I)
    data = [(X[j], int(j == i)) for j in I]
    basis = helper.symbolicSplines.InterpolatingPolynomialPiece(data)
    yy = basis.evaluate(xx)
    return yy
  
  def getSupport(self, l, i):
    return 0, 1
