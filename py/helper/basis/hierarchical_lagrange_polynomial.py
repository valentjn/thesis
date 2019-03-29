#!/usr/bin/python3

import numpy as np

import helper.grid

from .hierarchical_basis import HierarchicalBasis

class HierarchicalLagrangePolynomial(HierarchicalBasis):
  def __init__(self, nu=0):
    super().__init__(nu=nu)
    assert nu in [0, 1, 2]
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def evaluate(self, l, i, xx):
    I = helper.grid.getNodalIndices(l)
    X = self.getCoordinates(l, I)
    
    if self.nu == 0:
      yy = np.ones_like(xx)
      for i2 in I:
        if i2 != i: yy *= (xx - X[i2]) / (X[i] - X[i2])
    elif self.nu == 1:
      yy        = np.zeros_like(xx)
      yyProduct = np.ones_like(xx)
      for i2 in I:
        if i2 == i: continue
        yyProduct.fill(1)
        for i3 in I:
          if i3 in (i, i2): continue
          yyProduct *= (xx - X[i3]) / (X[i] - X[i3])
        yy += yyProduct / (X[i] - X[i2])
    elif self.nu == 2:
      yy        = np.zeros_like(xx)
      yySum     = np.zeros_like(xx)
      yyProduct = np.ones_like(xx)
      for i2 in I:
        if i2 == i: continue
        yySum.fill(0)
        for i3 in I:
          if i3 in (i, i2): continue
          yyProduct.fill(1)
          for i4 in I:
            if i4 in (i, i2, i3): continue
            yyProduct *= (xx - X[i4]) / (X[i] - X[i4])
          yySum += yyProduct / (X[i] - X[i3])
        yy += yySum / (X[i] - X[i2])
    else:
      raise NotImplementedError("Higher derivatives are not implemented.")
    
    return yy
  
  def getSupport(self, l, i):
    return 0, 1
