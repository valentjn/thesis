#!/usr/bin/python3

from .weakly_fundamental_spline import WeaklyFundamentalSpline
from .hierarchical_basis_from_parent_function import HierarchicalBasisFromParentFunction

class HierarchicalWeaklyFundamentalSpline(HierarchicalBasisFromParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(WeaklyFundamentalSpline(p, nu=nu))
    self.p = p
  
  def evaluate(self, l, i, xx):
    return (super().evaluate(l, i, xx) if l >= 1 else
            i * xx + (1 - i) * (1 - xx))
