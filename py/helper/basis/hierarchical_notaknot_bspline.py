#!/usr/bin/python3

import numpy as np

import helper.grid

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_bspline import restrictKnots
from .hierarchical_lagrange_polynomial import HierarchicalLagrangePolynomial
from .non_uniform_bspline import NonUniformBSpline

class HierarchicalNotAKnotBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
    self.lagrangeBasis = HierarchicalLagrangePolynomial(nu=nu)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def getKnots(self, l, i=None):
    assert l >= np.ceil(np.log2(self.p+1))
    hInv = 2**l
    I = [i for i in range(-self.p, hInv + self.p + 1)
         if (not (1 <= i <= (self.p-1)//2)) and
            (not (hInv - (self.p-1)//2 <= i <= hInv - 1))]
    if i is not None: I = restrictKnots(self.p, hInv, i, I)
    xi = self.getCoordinates(l, I)
    return xi
  
  def evaluate(self, l, i, xx):
    if l < np.ceil(np.log2(self.p+1)):
      yy = self.lagrangeBasis.evaluate(l, i, xx)
    else:
      xi = self.getKnots(l, i)
      basis = NonUniformBSpline(self.p, xi, nu=self.nu)
      yy = basis.evaluate(xx)
    
    return yy
  
  def getSupport(self, l, i):
    if l < np.ceil(np.log2(self.p+1)):
      lb, ub = 0, 1
    else:
      xi = self.getKnots(l, i)
      lb, ub = max(xi[0], 0), min(xi[-1], 1)
    
    return lb, ub
