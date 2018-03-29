#!/usr/bin/python3

import helper.grid

from .hierarchical_lagrange_polynomial import HierarchicalLagrangePolynomial

class HierarchicalClenshawCurtisLagrangePolynomial(HierarchicalLagrangePolynomial):
  def __init__(self, nu=0):
    super().__init__(nu=nu)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X
