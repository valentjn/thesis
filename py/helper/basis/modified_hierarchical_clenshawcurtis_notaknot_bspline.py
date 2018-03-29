#!/usr/bin/python3

import helper.grid

from .hierarchical_clenshawcurtis_notaknot_bspline import HierarchicalClenshawCurtisNotAKnotBSpline
from .modified_hierarchical_notaknot_bspline import ModifiedHierarchicalNotAKnotBSpline

class ModifiedHierarchicalClenshawCurtisNotAKnotBSpline(ModifiedHierarchicalNotAKnotBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.unmodifiedBasis = HierarchicalClenshawCurtisNotAKnotBSpline(p)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X
