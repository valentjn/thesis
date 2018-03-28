#!/usr/bin/python3

import abc

import numpy as np
import scipy.interpolate
import scipy.linalg

import pysgpp

import helper.function
import helper.grid
import helper.symbolicSplines



def restrictKnots(p, hInv, i, I):
  offset = 0
  
  if i < 0:
    I = [I[0] - j * (I[1] - I[0]) for j in range(-i, 0, -1)] + I
    offset = -i
  elif i > hInv:
    I = I + [I[-1] + j * (I[-1] - I[-2]) for j in range(1, i-hInv+1)]
  
  I = I[i+offset:i+offset+p+2]
  return I



class ParentFunction(abc.ABC):
  def __init__(self, nu=0):
    self.nu = nu
  
  @abc.abstractmethod
  def evaluate(self, xx): pass

  @abc.abstractmethod
  def getSupport(self): pass



class NonUniformBSpline(ParentFunction):
  def __init__(self, p, xi, k=None, nu=0):
    if k is None:
      super().__init__(nu)
      fakeXi = np.hstack([p * [xi[0]], xi, p * [xi[-1]]])
      fakeC = np.zeros((2*p+1,))
      fakeC[p] = 1
      self.bSpline = scipy.interpolate.BSpline(fakeXi, fakeC, p)
      self.support = [xi[0], xi[-1]]
    else:
      self.__init__(p, xi[k:k+p+2], nu=nu)
  
  def evaluate(self, xx):
    xx = np.array(xx).flatten().astype(float)
    K = np.logical_and(xx >= self.support[0], xx < self.support[1])
    yy = np.zeros_like(xx)
    yy[K] = self.bSpline(xx[K], nu=self.nu)
    return yy
  
  def getSupport(self):
    return self.support



class CardinalBSpline(NonUniformBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, list(range(0, p+2)), nu=nu)



class CentralizedCardinalBSpline(NonUniformBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, list(range(-(p+1)//2, (p+1)//2 + 1)), nu=nu)



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



class HierarchicalBasis(abc.ABC):
  def __init__(self, nu=0):
    self.nu = nu
  
  @abc.abstractmethod
  def evaluate(self, l, i, xx): pass

  @abc.abstractmethod
  def getSupport(self, l, i): pass



class HierarchicalBasisFromParentFunction(HierarchicalBasis):
  def __init__(self, parentFunction):
    super().__init__(nu=parentFunction.nu)
    self.parentFunction = parentFunction
  
  def evaluate(self, l, i, xx):
    tt = 2**l * xx - i
    yy = self.parentFunction.evaluate(tt)
    yy *= 2**(l*self.nu)
    return yy
  
  def getSupport(self, l, i):
    lb, ub = self.parentFunction.getSupport()
    lb = max((lb + i) / 2**l, 0)
    ub = min((ub + i) / 2**l, 1)
    return lb, ub



class HierarchicalFundamentalSpline(HierarchicalBasisFromParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(FundamentalSpline(p, nu=nu))
    self.p = p



class ModifiedHierarchicalFundamentalSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
    self.centralizedCardinalBSpline = CentralizedCardinalBSpline(p, nu=nu)
    self.unmodifiedBasis = HierarchicalFundamentalSpline(p, nu=nu)
    self.c, self.cutoff = self._calculateCoefficients()
  
  def _calculateCoefficients(self):
    if self.p == 1: return np.array([2, 1]), 1
    
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



class HierarchicalBSpline(HierarchicalBasisFromParentFunction):
  def __init__(self, p, nu=0):
    super().__init__(CentralizedCardinalBSpline(p, nu=nu))
    self.p = p
  
  def getKnots(self, l, i=None):
    hInv = 2**l
    I = list(range(-(self.p+1)//2, hInv + (self.p+1)//2 + 1))
    if i is not None: I = restrictKnots(self.p, hInv, i, I)
    xi = helper.grid.getCoordinates(l, I)
    return xi



class ModifiedHierarchicalBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    self.p = p
    self.unmodifiedBasis = HierarchicalBSpline(p, nu=nu)
  
  def getKnots(self, l, i=None):
    return super().getKnots(l, i)
  
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
        for j in range(i - self.p, i + 1):
          yy += (i+1-j) * self.unmodifiedBasis.evaluate(l, j, xx)
      else:
        yy = self.unmodifiedBasis.evaluate(l, i, xx)
      
      if self.nu >= 1:
        innerDeriv **= self.nu
        yy *= innerDeriv
    
    return yy
  
  def getSupport(self, l, i):
    return self.unmodifiedBasis.getSupport(l, i)



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



class ModifiedHierarchicalClenshawCurtisBSpline(ModifiedHierarchicalBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.unmodifiedBasis = HierarchicalClenshawCurtisBSpline(p, nu=nu)



class HierarchicalLagrangePolynomial(HierarchicalBasis):
  def __init__(self, nu=0):
    super().__init__()
    assert nu == 0
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I)
    return X
  
  def evaluate(self, l, i, xx):
    I = list(range(2**l + 1))
    X = self.getCoordinates(l, I)
    data = [(X[j], int(j == i)) for j in I]
    basis = helper.symbolicSplines.InterpolatingPolynomialPiece(data)
    yy = basis.evaluate(xx)
    return yy
  
  def getSupport(self, l, i):
    return 0, 1



class HierarchicalClenshawCurtisLagrangePolynomial(HierarchicalLagrangePolynomial):
  def __init__(self, nu=0):
    super().__init__(nu=nu)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X



class HierarchicalNotAKnotBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
    self.lagrangeBasis = HierarchicalLagrangePolynomial()
  
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
      basis = NonUniformBSpline(self.p, xi)
      yy = basis.evaluate(xx)
    
    return yy
  
  def getSupport(self, l, i):
    if l < np.ceil(np.log2(self.p+1)):
      lb, ub = 0, 1
    else:
      xi = self.getKnots(l, i)
      lb, ub = max(xi[0], 0), min(xi[-1], 1)
    
    return lb, ub



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
          basis = helper.symbolicSplines.InterpolatingPolynomialPiece(data)
          yy = basis.evaluate(xx)
        else:
          xiLeft = self.unmodifiedBasis.getKnots(l, 0)
          xi = self.unmodifiedBasis.getKnots(l, 1)
          basisLeft = helper.symbolicSplines.BSpline(xiLeft)
          basis = helper.symbolicSplines.BSpline(xi)
          basis, _ = basis.addSplinesForInterpolation([basisLeft], [(0, 0, 2)])
          yy = basis.evaluate(xx)
      else:
        yy = unmodifiedBasis.evaluate(l, i, xx)
    
    return yy
  
  def getSupport(self, l, i):
    return self.unmodifiedBasis.getSupport(l, i)



class HierarchicalClenshawCurtisNotAKnotBSpline(HierarchicalNotAKnotBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.lagrangeBasis = HierarchicalClenshawCurtisLagrangePolynomial()
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X



class ModifiedHierarchicalClenshawCurtisNotAKnotBSpline(ModifiedHierarchicalNotAKnotBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, nu=nu)
    self.unmodifiedBasis = HierarchicalClenshawCurtisNotAKnotBSpline(p)
  
  def getCoordinates(self, l, I):
    X = helper.grid.getCoordinates(l, I, distribution="clenshawCurtis")
    return X



class HierarchicalNaturalBSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
  
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
      yy = basis.evaluate(xx)
    else:
      yy = HierarchicalBSpline(self.p).evaluate(l, i, xx)
    
    return yy
  
  def getSupport(self, l, i):
    return HierarchicalBSpline(self.p).getSupport(l, i)



class HierarchicalLagrangeSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
  
  def evaluate(self, l, i, xx):
    raise NotImplementedError
  
  def getSupport(self, l, i):
    h = 2**(-l)
    x = i*h
    lb, ub = max(x-self.p*h, 0), min(x+self.p*h, 1)
    return lb, ub



class HierarchicalLagrangeNotAKnotSpline(HierarchicalBasis):
  def __init__(self, p, nu=0):
    super().__init__(nu=nu)
    assert nu == 0
    self.p = p
  
  def evaluate(self, l, i, xx):
    raise NotImplementedError
  
  def getSupport(self, l, i):
    hInv = 2**l
    h = 1 / hInv
    
    if self.p == 3:
      if l <= 2:
        return 0, 1
      else:
        if i == 1:
          return 0, 4*h
        elif i == 3:
          return 0, 6*h
        elif i == hInv - 3:
          return 1-6*h, 1
        elif i == hInv - 1:
          return 1-4*h, 1
        else:
          return HierarchicalLagrangeSpline(p).getSupport(l, i)
    else:
      raise NotImplementedError("Unsupported B-spline degree.")



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



class TensorProduct(HierarchicalBasis):
  def __init__(self, basis1D, d=None):
    super().__init__(nu=(basis1D[0].nu if d is None else basis1D.nu))
    self.basis1D = (basis1D if d is None else d * [basis1D])
  
  def evaluate(self, l, i, XX):
    NN, d = XX.shape
    YY = np.ones((NN,))
    for t in range(d): YY = YY * self.basis1D[t].evaluate(l[t], i[t], XX[:,t])
    return YY
  
  def getSupport(self, l, i):
    d = l.size
    support = np.array([self.basis1D[t].getSupport(l[t], i[t]) for t in range(d)]).T
    return support



class HierarchicalFundamentalTransformed(HierarchicalBasis):
  def __init__(self, basis):
    super().__init__(nu=basis.nu)
    self.basis = basis
  
  def getCoefficients(self, l, i):
    X, L, I = helper.grid.RegularSparseBoundary(l, 1, 0).generate()
    fX = [int((l == l2) and (i == i2)) for l2, i2 in zip(L, I)]
    c = helper.function.Interpolant(self.basis, X, L, I, fX).aX
    return c, L, I
  
  def evaluate(self, l, i, XX):
    c, L, I = self.getCoefficients(l, i)
    YY = sum(c2 * self.basis.evaluate(l2, i2, XX)
             for c2, l2, i2 in zip(c, L, I))
    return YY
  
  def getSupport(self, l, i):
    c, L, I = self.getCoefficients(l, i)
    supports = np.array([self.basis.getSupport(l2, i2)
                         for c2, l2, i2 in zip(c, L, I) if c2 != 0])
    return np.min(supports[:,0]), np.max(supports[:,1])



class NodalFundamentalTransformed(HierarchicalFundamentalTransformed):
  def __init__(self, basis):
    super().__init__(nu=basis.nu)
    self.basis = basis
  
  def getCoefficients(self, l, i):
    hInv = 2**l
    L = l * np.ones((hInv + 1, 1))
    I = np.reshape(np.array(range(hInv + 1)), (hInv + 1, 1))
    X = helper.grid.getCoordinates(L, I)
    fX = [int(i == i2) for i2 in I]
    c = helper.function.Interpolant(self.basis, X, L, I, fX).aX
    return c, L, I
