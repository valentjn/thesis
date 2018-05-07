#!/usr/bin/python3

import numpy as np

import helper.grid

from .hierarchical_basis import HierarchicalBasis

class HierarchicalLagrangePolynomial(HierarchicalBasis):
  def __init__(self, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def evaluate(self, l, i, xx):
    I = helper.grid.getNodalIndices(l)
    X = self.getCoordinates(l, I)
    yy = np.ones_like(xx)
    
    for ip in I:
      if ip != i: yy *= (xx - X[ip]) / (X[i] - X[ip])
    
    return yy
  
  def getSupport(self, l, i):
    return 0, 1
