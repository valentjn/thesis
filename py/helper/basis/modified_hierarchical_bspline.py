#!/usr/bin/python3

import numpy as np

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_bspline import HierarchicalBSpline

class ModifiedHierarchicalBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
    self.unmodifiedBasis = HierarchicalBSpline(p, nu=nu)
  
  def getKnots(self, l, i=None):
    return super().getKnots(l, i)
  
  def evaluate(self, l, i, xx):
    if l == 1:
      yy = (np.ones_like(xx) if self.nu == 0 else np.zeros_like(xx))
    else:
      innerDeriv = 1
      
      if i == 2**l - 1:
        xx = 1 - xx
        i = 1
        innerDeriv *= -1
      
      if i == 1:
        yy = np.zeros_like(xx)
        for j in range(i - self.p, i + 1):
          yy += (i+1-j) * self.unmodifiedBasis.evaluate(l, j, xx)
      else:
        yy = self.unmodifiedBasis.evaluate(l, i, xx)
      
      if self.nu >= 1:
        innerDeriv **= self.nu
        yy *= innerDeriv
    
    return yy
  
  def getSupport(self, l, i):
    return self.unmodifiedBasis.getSupport(l, i)
