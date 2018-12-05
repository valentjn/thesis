#!/usr/bin/python3

import numpy as np

import helper.grid
import helper.symbolic_splines

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_notaknot_bspline import HierarchicalNotAKnotBSpline

class ModifiedHierarchicalNotAKnotBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
    self.unmodifiedBasis = HierarchicalNotAKnotBSpline(p)
  
  def evaluate(self, l, i, xx):
    if l == 1:
      yy = np.ones_like(xx)
    else:
      if i == 2**l - 1:
        i = 1
        xx = 1 - xx
      
      if i == 1:
        if l < np.ceil(np.log2(self.p+1)):
          I = list(range(2**l + 1))
          X = helper.grid.getCoordinates(l, I)
          data = [(0, 0, 2)] + [(X[j], int(j == 1)) for j in I[1:]]
          basis = helper.symbolic_splines.InterpolatingPolynomialPiece(data)
          yy = basis.evaluate(xx)
        else:
          xiLeft = self.unmodifiedBasis.getKnots(l, 0)
          xi = self.unmodifiedBasis.getKnots(l, 1)
          basisLeft = helper.symbolic_splines.BSpline(xiLeft)
          basis = helper.symbolic_splines.BSpline(xi)
          
          if self.p > 1:
            basis, _ = basis.addSplinesForInterpolation([basisLeft], [(0, 0, 2)])
          else:
            basis += basisLeft * (xi[2] / (xi[2] - xi[1]))
          
          yy = basis.evaluate(xx)
      else:
        yy = self.unmodifiedBasis.evaluate(l, i, xx)
    
    return yy
  
  def getSupport(self, l, i):
    return self.unmodifiedBasis.getSupport(l, i)
