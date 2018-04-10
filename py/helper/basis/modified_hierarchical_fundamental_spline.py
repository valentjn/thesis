#!/usr/bin/python3

import numpy as np
import scipy.linalg

from .cardinal_bspline import CardinalBSpline
from .centralized_cardinal_bspline import CentralizedCardinalBSpline
from .hierarchical_basis import HierarchicalBasis
from .hierarchical_fundamental_spline import HierarchicalFundamentalSpline

class ModifiedHierarchicalFundamentalSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
    self.centralizedCardinalBSpline = CentralizedCardinalBSpline(p, nu=nu)
    self.unmodifiedBasis = HierarchicalFundamentalSpline(p, nu=nu)
    self.c, self.cutoff = self._calculateCoefficients()
  
  def _calculateCoefficients(self):
    if self.p == 1: return np.array([2, 1]), 2
    
    cardinalBSpline = CardinalBSpline(self.p)
    valuesBSpline = cardinalBSpline.evaluate(np.array(range(1, self.p+1)))
    roots = np.roots(valuesBSpline)
    gamma = abs(max([x for x in roots if x < -1]))
    
    tol = 1e-10
    cutoff = -np.log(tol) / gamma
    
    cutoff = int((2 if self.p > 3 else 2.5) *
                 cutoff / valuesBSpline[(self.p-1)//2])  # only a guess
    N = cutoff + (self.p+1)//2 - 1
    A = scipy.linalg.toeplitz(np.hstack((valuesBSpline[(self.p-1)//2:],
                                         (N - (self.p+1)//2) * [0])))
    b = np.zeros((N,))
    b[(self.p+1)//2] = 1
    
    for q in range(2, (self.p+1)//2+1):
      centralizedCardinalBSplineDerivative = CentralizedCardinalBSpline(self.p, nu=q)
      
      for k in range(1-(self.p+1)//2, cutoff):
        j = k + (self.p+1)//2 - 1
        if q == 2: A[0,j] = centralizedCardinalBSplineDerivative.evaluate(1 - k)
        A[q-1,j] = centralizedCardinalBSplineDerivative.evaluate(0 - k)
    
    c = np.linalg.solve(A, b)
    
    cutoff = np.where(np.abs(c) < tol)[0][0] + 1 - (self.p+1)//2
    c = c[:cutoff+(self.p+1)//2-1]
    
    return c, cutoff
  
  def evaluate(self, l, i, xx):
    if l == 1:
      yy = (np.ones_like(xx) if self.nu == 0 else np.zeros_like(xx))
    else:
      innerDeriv = 1
      
      if i == 2**l - 1:
        xx = 1 - xx
        i = 1
        innerDeriv *= -1
      
      if i == 1:
        yy = np.zeros_like(xx)
        for k in range(1-(self.p+1)//2, self.cutoff):
          yy += (self.c[k-1+(self.p+1)//2] *
                 self.centralizedCardinalBSpline.evaluate(2**l * xx - k))
        innerDeriv *= 2**l
      else:
        yy = self.unmodifiedBasis.evaluate(l, i, xx)
      
      if self.nu >= 1:
        innerDeriv **= self.nu
        yy *= innerDeriv
    
    return yy
  
  def getSupport(self, l, i):
    lb, ub = 0, 1
    return lb, ub
