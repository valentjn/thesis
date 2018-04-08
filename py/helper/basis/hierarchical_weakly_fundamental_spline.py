#!/usr/bin/python3

import numpy as np

from .weakly_fundamental_spline import WeaklyFundamentalSpline
from .hierarchical_basis_from_parent_function import HierarchicalBasisFromParentFunction

class HierarchicalWeaklyFundamentalSpline(HierarchicalBasisFromParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(WeaklyFundamentalSpline(p, nu=nu))
    self.p = p
  
  def evaluate(self, l, i, xx):
    if l >= 1:
      yy = super().evaluate(l, i, xx)
    elif self.nu == 0:
      yy = i * xx + (1 - i) * (1 - xx)
    elif self.nu == 1:
      yy = (2*i-1) * np.ones_like(xx)
    else:
      yy = np.zeros_like(xx)
    
    return yy
