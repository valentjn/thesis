#!/usr/bin/python3

import numpy as np
import scipy.linalg

from .cardinal_bspline import CardinalBSpline
from .centralized_cardinal_bspline import CentralizedCardinalBSpline
from .parent_function import ParentFunction

class FundamentalSpline(ParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(nu)
    self.p = p
    self.centralizedCardinalBSpline = CentralizedCardinalBSpline(p, nu=nu)
    self.c, self.cutoff, self.gamma = self._calculateCoefficients()
  
  def _calculateCoefficients(self):
    if self.p == 1: return np.array([1]), 1, float("inf")
    
    cardinalBSpline = CardinalBSpline(self.p)
    valuesBSpline = cardinalBSpline.evaluate(np.array(range(1, self.p+1)))
    roots = np.roots(valuesBSpline)
    gamma = abs(max([x for x in roots if x < -1]))
    
    tol = 1e-10
    cutoff = -np.log(tol) / gamma
    
    cutoff = int((2 if self.p > 3 else 2.5) *
                 cutoff / valuesBSpline[(self.p-1)//2])  # only a guess
    N = 2*cutoff-1
    A = scipy.linalg.toeplitz(np.hstack((valuesBSpline[(self.p-1)//2:],
                                         (N - (self.p+1)//2) * [0])))
    b = np.zeros((N,))
    b[(N-1)//2] = 1
    c = np.linalg.solve(A, b)
    
    cutoff = (N-1)//2 - np.where(np.abs(c) >= tol)[0][0] + 1
    c = c[(N-1)//2-cutoff+1:(N-1)//2+cutoff]
    
    return c, cutoff, gamma
  
  def evaluate(self, xx):
    yy = np.zeros_like(xx)
    
    for k in range(-self.cutoff + 1, self.cutoff):
      yy += (self.c[k+self.cutoff-1] *
             self.centralizedCardinalBSpline.evaluate(xx - k))
    
    return yy
  
  def getSupport(self):
    return float("-inf"), float("inf")
