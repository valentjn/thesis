#!/usr/bin/python3

import numpy as np
import scipy.linalg

from .centralized_cardinal_bspline import CentralizedCardinalBSpline
from .parent_function import ParentFunction

class WeaklyFundamentalSpline(ParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(nu)
    self.p = p
    self.centralizedCardinalBSpline = CentralizedCardinalBSpline(p)
    self.evaluationBasis = CentralizedCardinalBSpline(p, nu=nu)
    self.c = self._calculateCoefficients()
  
  def _calculateCoefficients(self):
    N = self.p
    A = np.zeros((N-1, N))
    x = np.linspace(2.0 - self.p, self.p - 2, N - 1)
    center = (self.p-1)//2
    
    for j in range(N):
      k = j - center
      A[:,j] = self.centralizedCardinalBSpline.evaluate(x - k)
    
    b = np.eye(1, N, center).flatten()
    A = np.insert(A, center, b, axis=0)
    c = np.linalg.solve(A, b)
    
    return c
  
  def evaluate(self, xx):
    yy = np.zeros_like(xx)
    
    for k in range(-(self.p-1)//2, (self.p+1)//2):
      yy += (self.c[k+(self.p-1)//2] *
             self.evaluationBasis.evaluate(xx - k))
    
    return yy
  
  def getSupport(self):
    return -self.p, self.p
