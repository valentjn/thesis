#!/usr/bin/python3

import numpy as np

import helper.function
import helper.grid

from .hierarchical_fundamental_transformed import HierarchicalFundamentalTransformed
from .hierarchical_notaknot_bspline import HierarchicalNotAKnotBSpline

class NodalWeaklyFundamentalTransformed(HierarchicalFundamentalTransformed):
  def __init__(self, basis, evaluationBasis=None):
    super().__init__(basis, evaluationBasis=evaluationBasis)
  
  def getCoefficients(self, l, i):
    hInv = 2**l
    p = self.basis.p
    
    # without the hack, this produces incorrect results for NAK B-splines
    # the B-splines of index 3 and hInv-3 don't vanish at 0 and 1;
    # this is just a dirty hack which should fix the figure in
    # hierarchicalBasis, not designed for general degrees
    dirtyHackEnabled = (
        isinstance(self.basis, HierarchicalNotAKnotBSpline) and (p == 3))
    
    iLeft, iRight = i-(p-1)//2, i+(p-1)//2
    if dirtyHackEnabled:
      if i == 3:        iLeft -= 1
      if i == hInv - 3: iRight += 1
    omitLeft, omitRight = max(-iLeft, 0), max(iRight - hInv, 0)
    
    iLeft += omitLeft
    iRight -= omitRight
    N = iRight - iLeft + 1
    
    x = np.linspace(i-self.p+2, i+self.p-2, N-1) / hInv
    if dirtyHackEnabled:
      if i == 3:        x = np.linspace(0, i+self.p-2, N-1) / hInv
      if i == hInv - 3: x = np.linspace(i-self.p+2, hInv, N-1) / hInv
    x = (x[omitLeft:-omitRight] if omitRight > 0 else
         x[omitLeft:])
    
    A = np.zeros((N-1, N))
    
    for k in range(N):
      j = iLeft + k
      bx = self.basis.evaluate(l, j, x)
      
      try:
        A[:,k] = bx
      except ValueError:
        return None, None, None
    
    center = i - iLeft
    b = np.eye(1, N, center).flatten()
    A = np.insert(A, center, b, axis=0)
    
    try:
      c = np.linalg.solve(A, b)
    except np.linalg.linalg.LinAlgError:
      return None, None, None
    
    L = l * np.ones((N,), dtype=int)
    I = np.linspace(iLeft, iRight, N).astype(int)
    
    return c, L, I
