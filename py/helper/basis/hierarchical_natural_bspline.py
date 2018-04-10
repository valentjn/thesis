#!/usr/bin/python3

import helper.grid
import helper.symbolicSplines

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_bspline import HierarchicalBSpline, restrictKnots

class HierarchicalNaturalBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
    self.basisCache = {}
  
  def getKnots(self, l, i=None):
    hInv = 2**l
    I = list(range(-(self.p+1)//2, hInv + (self.p+1)//2 + 1))
    if i is not None: I = restrictKnots(self.p, hInv, i, I)
    xi = helper.grid.getCoordinates(l, I)
    return xi
  
  def evaluate(self, l, i, xx):
    hInv = 2**l
    
    if l == 0:
      yy = i * xx + (1 - i) * (1 - xx)
    elif (i - (self.p+1)//2 < 0) or (i + (self.p+1)//2 > hInv):
      if (l, i) in self.basisCache:
        basis = self.basisCache[(l, i)]
      else:
        xi = self.getKnots(l, i)
        basis = helper.symbolicSplines.BSpline(xi)
        basesToAdd = []
        conditions = []
        
        if i - (self.p+1)//2 < 0:
          for j in range((self.p-1)//2):
            xi = self.getKnots(l, i-j-1)
            basesToAdd.append(helper.symbolicSplines.BSpline(xi))
            conditions.append((0, 0, j+2))
        
        if i + (self.p+1)//2 > hInv:
          for j in range((self.p-1)//2):
            xi = self.getKnots(l, i+j+1)
            basesToAdd.append(helper.symbolicSplines.BSpline(xi))
            conditions.append((1, 0, j+2))
        
        basis, _ = basis.addSplinesForInterpolation(basesToAdd, conditions)
        self.basisCache[(l, i)] = basis
      
      yy = basis.evaluate(xx)
    else:
      if (l, i) in self.basisCache:
        basis = self.basisCache[(l, i)]
      else:
        basis = HierarchicalBSpline(self.p)
        self.basisCache[(l, i)] = basis
      
      yy = basis.evaluate(l, i, xx)
    
    return yy
  
  def getSupport(self, l, i):
    return HierarchicalBSpline(self.p).getSupport(l, i)
