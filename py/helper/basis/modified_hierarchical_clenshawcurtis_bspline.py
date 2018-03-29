#!/usr/bin/python3

from .hierarchical_clenshawcurtis_bspline import HierarchicalClenshawCurtisBSpline
from .modified_hierarchical_bspline import ModifiedHierarchicalBSpline

class ModifiedHierarchicalClenshawCurtisBSpline(ModifiedHierarchicalBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.unmodifiedBasis = HierarchicalClenshawCurtisBSpline(p, nu=nu)
