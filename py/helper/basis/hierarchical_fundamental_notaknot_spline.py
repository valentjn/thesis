#!/usr/bin/python3

from .hierarchical_basis import HierarchicalBasis

class HierarchicalFundamentalNotAKnotSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
  
  def _getCoefficients(self, l, i):
    pass
  
  def evaluate(self, l, i, xx):
    pass
  
  def getSupport(self, l, i):
    pass
