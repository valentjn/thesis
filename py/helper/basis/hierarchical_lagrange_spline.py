#!/usr/bin/python3

from .hierarchical_basis import HierarchicalBasis

class HierarchicalLagrangeSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
  
  def evaluate(self, l, i, xx):
    raise NotImplementedError
  
  def getSupport(self, l, i):
    h = 2**(-l)
    x = i*h
    lb, ub = max(x-self.p*h, 0), min(x+self.p*h, 1)
    return lb, ub
