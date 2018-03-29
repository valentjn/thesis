#!/usr/bin/python3

import helper.grid

from .hierarchical_clenshawcurtis_lagrange_polynomial import HierarchicalClenshawCurtisLagrangePolynomial
from .hierarchical_notaknot_bspline import HierarchicalNotAKnotBSpline

class HierarchicalClenshawCurtisNotAKnotBSpline(HierarchicalNotAKnotBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.lagrangeBasis = HierarchicalClenshawCurtisLagrangePolynomial()
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X
