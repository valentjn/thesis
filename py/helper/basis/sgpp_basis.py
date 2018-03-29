#!/usr/bin/python3

import numpy as np

import pysgpp

from .hierarchical_basis import HierarchicalBasis
from .hierarchical_bspline import HierarchicalBSpline
from .hierarchical_lagrange_spline import HierarchicalLagrangeSpline
from .hierarchical_lagrange_notaknot_spline import HierarchicalLagrangeNotAKnotSpline
from .hierarchical_notaknot_bspline import HierarchicalNotAKnotBSpline
from .modified_hierarchical_notaknot_bspline import ModifiedHierarchicalNotAKnotBSpline

class SGppBasis(HierarchicalBasis):
  # format: {testFunctionName : (sgppClass, pythonClass)}
  BASIS_TYPES = {
    "hierarchicalBSpline" :
      (pysgpp.SBsplineBase, HierarchicalBSpline),
    "hierarchicalNotAKnotBSpline" :
      (pysgpp.SNotAKnotBsplineBase, HierarchicalNotAKnotBSpline),
    "modifiedHierarchicalNotAKnotBSpline" :
      (pysgpp.SNotAKnotBsplineModifiedBase, ModifiedHierarchicalNotAKnotBSpline),
    "hierarchicalLagrangeSpline" :
      (pysgpp.SLagrangeSplineBase, HierarchicalLagrangeSpline),
    "hierarchicalLagrangeNotAKnotSpline" :
      (pysgpp.SLagrangeNotAKnotSplineBase, HierarchicalLagrangeNotAKnotSpline),
  }
  
  def __init__(self, basis, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    if type(basis) is str: basis = SGppBasis.BASIS_TYPES[basis][0](p)
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
