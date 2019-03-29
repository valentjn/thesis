#!/usr/bin/python3

import numpy as np

from .hierarchical_basis import HierarchicalBasis

class TensorProduct(HierarchicalBasis):
  def __init__(self, basis1D, d=None):
    super().__init__(nu=(basis1D[0].nu if d is None else basis1D.nu))
    self.basis1D = (basis1D if d is None else d * [basis1D])
  
  def evaluate(self, l, i, XX):
    NN, d = XX.shape
    YY = np.ones((NN,))
    for t in range(d): YY *= self.basis1D[t].evaluate(l[t], i[t], XX[:,t])
    return YY
  
  def getSupport(self, l, i):
    d = l.size
    support = np.array([self.basis1D[t].getSupport(l[t], i[t]) for t in range(d)]).T
    return support
