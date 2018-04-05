#!/usr/bin/python3

import numpy as np

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_bspline import HierarchicalBSpline
from .hierarchical_notaknot_bspline import HierarchicalNotAKnotBSpline
from .hierarchical_weakly_fundamental_spline import HierarchicalWeaklyFundamentalSpline
#from .hierarchical_weakly_fundamental_notaknot_spline import HierarchicalWeaklyFundamentalNotAKnotSpline
from .modified_hierarchical_notaknot_bspline import ModifiedHierarchicalNotAKnotBSpline

class SGppBasis(HierarchicalBasis):
  def __init__(self, basis, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    
    if type(basis) is str:
      import pysgpp
      basisTypes = {
        "hierarchicalBSpline" :
          (pysgpp.SBsplineBase, HierarchicalBSpline),
        "hierarchicalNotAKnotBSpline" :
          (pysgpp.SNotAKnotBsplineBase, HierarchicalNotAKnotBSpline),
        "modifiedHierarchicalNotAKnotBSpline" :
          (pysgpp.SNotAKnotBsplineModifiedBase, ModifiedHierarchicalNotAKnotBSpline),
        "hierarchicalLagrangeSpline" :
          (pysgpp.SLagrangeSplineBase, HierarchicalWeaklyFundamentalSpline),
        #"hierarchicalLagrangeNotAKnotSpline" :
        #  (pysgpp.SLagrangeNotAKnotSplineBase, HierarchicalWeaklyFundamentalNotAKnotSpline),
      }
      basis = basisTypes[basis][0](p)
    self.basis = basis
  
  def evaluate(self, l, i, xx):
    yy = np.array([self.basis.eval(np.asscalar(l), np.asscalar(i), x) for x in xx])
    return yy
  
  def getSupport(self, l, i):
    p = self.basis.getDegree()
    
    for basisType in SGppBasis.BASIS_TYPES.values():
      if type(self.basis) is basisType[0]:
        return basisType[1](p).getSupport(l, i)
    
    return NotImplementedError("Unsupported basis type.")
