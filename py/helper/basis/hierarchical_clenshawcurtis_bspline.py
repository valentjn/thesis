#!/usr/bin/python3

import helper.grid

from .hierarchical_bspline import HierarchicalBSpline, restrictKnots
from .non_uniform_bspline import NonUniformBSpline

class HierarchicalClenshawCurtisBSpline(HierarchicalBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p)
    assert nu == 0
  
  def getKnots(self, l, i=None):
    hInv = 2**l
    I = list(range(-(self.p+1)//2, hInv + (self.p+1)//2 + 1))
    if i is not None: I = restrictKnots(self.p, hInv, i, I)
    xi = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return xi
  
  def evaluate(self, l, i, xx):
    xi = self.getKnots(l, i)
    basis = NonUniformBSpline(self.p, xi)
    yy = basis.evaluate(xx)
    return yy
  
  def getSupport(self, l, i):
    xi = self.getKnots(l, i)
    lb, ub = max(xi[0], 0), min(xi[-1], 1)
    return lb, ub
