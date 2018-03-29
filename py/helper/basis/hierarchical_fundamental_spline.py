#!/usr/bin/python3

from .fundamental_spline import FundamentalSpline
from .hierarchical_basis_from_parent_function import HierarchicalBasisFromParentFunction

class HierarchicalFundamentalSpline(HierarchicalBasisFromParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(FundamentalSpline(p, nu=nu))
    self.p = p
