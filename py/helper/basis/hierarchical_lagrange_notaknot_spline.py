#!/usr/bin/python3

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_lagrange_spline import HierarchicalLagrangeSpline

class HierarchicalLagrangeNotAKnotSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
  
  def evaluate(self, l, i, xx):
    raise NotImplementedError
  
  def getSupport(self, l, i):
    hInv = 2**l
    h = 1 / hInv
    
    if self.p == 3:
      if l <= 2:
        return 0, 1
      else:
        if i == 1:
          return 0, 4*h
        elif i == 3:
          return 0, 6*h
        elif i == hInv - 3:
          return 1-6*h, 1
        elif i == hInv - 1:
          return 1-4*h, 1
        else:
          return HierarchicalLagrangeSpline(p).getSupport(l, i)
    else:
      raise NotImplementedError("Unsupported B-spline degree.")
