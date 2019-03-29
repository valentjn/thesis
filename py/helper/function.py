#!/usr/bin/python3

import abc
import warnings

import numpy as np



def sgpp2np(x):
  import pysgpp
  if type(x) is pysgpp.DataMatrix:
    return np.array([[x.get(k, j) for j in range(x.getNcols())]
                     for k in range(x.getNrows())])
  else:
    return np.array([x[k] for k in range(x.getSize())])

def np2sgpp(x):
  import pysgpp
  return (pysgpp.DataVector(x) if x.ndim == 1 else pysgpp.DataMatrix(x))



class Function(abc.ABC):
  def __init__(self, d):
    self.d = d
  
  @abc.abstractmethod
  def evaluate(self, XX): pass
  
  def computeRelativeL2Error(self, fInterp, NN=1e5):
    XX = np.random.rand(int(NN), int(self.d))
    yy = self.evaluate(XX)
    yyInterp = fInterp.evaluate(XX)
    absoluteError = np.sqrt(np.sum((yy - yyInterp)**2 / NN))
    norm = np.sqrt(np.sum(yy**2 / NN))
    return absoluteError / norm



class Interpolant(Function):
  def __init__(self, basis, X, L, I, fX, aX=None):
    super().__init__(X.shape[1])
    self.basis = basis
    self.X, self.L, self.I = X, L, I
    self.fX = fX
    self.aX = (aX if aX is not None else self._getSurpluses())
  
  def _getSurpluses(self):
    A = self.getInterpolationMatrix()
    aX = np.linalg.solve(A, self.fX)
    return aX
  
  def _evaluateBasis(self, k, XX):
    l, i = self.L[k,:], self.I[k,:]
    if l.shape[0] == 1:
      l, i = l[0], i[0]
      if XX.ndim == 2: XX = XX[:,0]
    YY = self.basis.evaluate(l, i, XX)
    YY = YY.flatten()
    return YY
  
  def getInterpolationMatrix(self):
    N = self.X.shape[0]
    A = np.zeros((N, N))
    
    for k in range(N):
      A[:,k] = self._evaluateBasis(k, self.X)
    
    return A
  
  def evaluate(self, XX):
    if XX.ndim == 1: XX = np.array([XX])
    N, NN = self.X.shape[0], XX.shape[0]
    
    if self.aX.ndim == 1:
      YY = np.zeros((NN,))
      for k in range(N): YY += self.aX[k] * self._evaluateBasis(k, XX)
    else:
      m = self.aX.shape[1]
      YY = np.zeros((NN, m))
      
      for k in range(N):
        YY += (np.reshape(self.aX[k,:], (1, m)) *
               np.reshape(self._evaluateBasis(k, XX), (NN, 1)))
    
    return YY



class InterpolantGradient(Interpolant):
  def __init__(self, basis1D, basis1DGradient, X, L, I, fX, aX=None):
    import helper.basis
    if not hasattr(basis1D, "__len__"):
      basis1D = X.shape[1] * [basis1D]
    if not hasattr(basis1DGradient, "__len__"):
      basis1DGradient = X.shape[1] * [basis1DGradient]
    self.basis1D         = basis1D
    self.basis1DGradient = basis1DGradient
    basis = helper.basis.TensorProduct(basis1D)
    super().__init__(basis, X, L, I, fX, aX=aX)
  
  def evaluate(self, XX):
    assert (self.aX.ndim == 1), "Only scalar-valued interpolants " \
                                "are supported."
    assert (self.L.ndim == 2), "L needs to be a matrix."
    assert (self.I.ndim == 2), "I needs to be a matrix."
    if XX.ndim == 1: XX = np.array([XX])
    
    (N, d), NN = self.X.shape, XX.shape[0]
    YY,         curYY         = np.zeros((NN,)),   np.zeros((NN,))
    YYGradient, curYYGradient = np.zeros((NN, d)), np.zeros((NN, d))
    
    for k in range(N):
      curYY.fill(self.aX[k])
      curYYGradient.fill(self.aX[k])
      
      for t in range(d):
        YY1D = self.basis1D[t].evaluate(
            self.L[k,t], self.I[k,t], XX[:,t])
        YY1DGradient = self.basis1DGradient[t].evaluate(
            self.L[k,t], self.I[k,t], XX[:,t])
        curYY *= YY1D
        
        for t2 in range(d):
          curYYGradient[:,t2] *= (YY1DGradient if t2 == t else YY1D)
      
      YY         += curYY
      YYGradient += curYYGradient
    
    return YY, YYGradient



class InterpolantHessian(Interpolant):
  def __init__(self, basis1D, basis1DGradient, basis1DHessian,
               X, L, I, fX, aX=None):
    import helper.basis
    if not hasattr(basis1D, "__len__"):
      basis1D = X.shape[1] * [basis1D]
    if not hasattr(basis1DGradient, "__len__"):
      basis1DGradient = X.shape[1] * [basis1DGradient]
    if not hasattr(basis1DHessian, "__len__"):
      basis1DHessian = X.shape[1] * [basis1DHessian]
    self.basis1D         = basis1D
    self.basis1DGradient = basis1DGradient
    self.basis1DHessian  = basis1DHessian
    basis = helper.basis.TensorProduct(basis1D)
    super().__init__(basis, X, L, I, fX, aX=aX)
  
  def evaluate(self, XX):
    assert (self.aX.ndim == 1), "Only scalar-valued interpolants " \
                                "are supported."
    assert (self.L.ndim == 2), "L needs to be a matrix."
    assert (self.I.ndim == 2), "I needs to be a matrix."
    if XX.ndim == 1: XX = np.array([XX])
    
    (N, d), NN = self.X.shape, XX.shape[0]
    YY,         curYY         = np.zeros((NN,)),      np.zeros((NN,))
    YYGradient, curYYGradient = np.zeros((NN, d)),    np.zeros((NN, d))
    YYHessian,  curYYHessian  = np.zeros((NN, d, d)), np.zeros((NN, d, d))
    
    for k in range(N):
      curYY.fill(self.aX[k])
      curYYGradient.fill(self.aX[k])
      curYYHessian.fill(self.aX[k])
      
      for t in range(d):
        YY1D = self.basis1D[t].evaluate(
            self.L[k,t], self.I[k,t], XX[:,t])
        YY1DGradient = self.basis1DGradient[t].evaluate(
            self.L[k,t], self.I[k,t], XX[:,t])
        YY1DHessian = self.basis1DHessian[t].evaluate(
            self.L[k,t], self.I[k,t], XX[:,t])
        curYY *= YY1D
        
        for t2 in range(d):
          if t2 == t:
            curYYGradient[:,t2] *= YY1DGradient
            for t3 in range(d):
              curYYHessian[:,t2,t3] *= (YY1DHessian if t3 == t else
                                        YY1DGradient)
          else:
            curYYGradient[:,t2] *= YY1D
            for t3 in range(d):
              curYYHessian[:,t2,t3] *= (YY1DGradient if t3 == t else YY1D)
      
      YY         += curYY
      YYGradient += curYYGradient
      YYHessian  += curYYHessian
    
    return YY, YYGradient, YYHessian



class SGppFunction(Function):
  def __init__(self, f):
    super().__init__(f.getNumberOfParameters())
    self.f = f
  
  def evaluate(self, XX):
    import pysgpp
    
    if XX.ndim == 1:
      yy = self.f.eval(np2sgpp(XX))
    else:
      yy = pysgpp.DataVector(XX.shape[0])
      self.f.eval(np2sgpp(XX), yy)
      yy = sgpp2np(yy)
    
    return yy



class SGppVectorFunction(Function):
  def __init__(self, f):
    super().__init__(f.getNumberOfParameters())
    self.m = f.getNumberOfComponents()
    self.f = f
  
  def evaluate(self, XX):
    import pysgpp
    
    if XX.ndim == 1:
      yy = pysgpp.DataVector(self.m)
    else:
      yy = pysgpp.DataMatrix(XX.shape[0], self.m)
    
    self.f.eval(np2sgpp(XX), yy)
    yy = sgpp2np(yy)
    
    return yy



class SGppInterpolant(SGppFunction):
  def __init__(self, grid, fX, aX=None):
    import pysgpp
    self.grid = grid
    self.fX = fX
    self.aX = (aX if aX is not None else self._getSurpluses())
    f = pysgpp.OptInterpolantScalarFunction(grid, np2sgpp(self.aX))
    super().__init__(f)
  
  def _getSurpluses(self):
    import pysgpp
    aX = pysgpp.DataVector(self.fX.size)
    hierarchizationSLE = pysgpp.OptHierarchisationSLE(self.grid)
    sleSolver = pysgpp.OptAutoSLESolver()
    assert sleSolver.solve(hierarchizationSLE, np2sgpp(self.fX), aX)
    return sgpp2np(aX)



class SGppVectorInterpolant(SGppVectorFunction):
  def __init__(self, grid, fX, aX=None):
    import pysgpp
    self.grid = grid
    self.fX = fX
    self.aX = (aX if aX is not None else self._getSurpluses())
    f = pysgpp.OptInterpolantVectorFunction(grid, np2sgpp(self.aX))
    super().__init__(f)
  
  def _getSurpluses(self):
    import pysgpp
    aX = pysgpp.DataMatrix(*self.fX.shape)
    hierarchizationSLE = pysgpp.OptHierarchisationSLE(self.grid)
    sleSolver = pysgpp.OptAutoSLESolver()
    assert sleSolver.solve(hierarchizationSLE, np2sgpp(self.fX), aX)
    return sgpp2np(aX)



class SGppTestFunction(SGppFunction):
  def __init__(self, f, d):
    if type(f) is str:
      import pysgpp
      testFunctionTypes = {
        "absoluteValue" :
          (pysgpp.OptAbsoluteValueObjective,     True,   True),
        "ackley" :
          (pysgpp.OptAckleyObjective,            True,   False),
        "alpine02" :
          (pysgpp.OptAlpine02Objective,          True,   False),
        "beale" :
          (pysgpp.OptBealeObjective,             False,  False),
        "branin01" :
          (pysgpp.OptBranin01Objective,          False,  True),
        "branin02" :
          (pysgpp.OptBranin02Objective,          False,  False),
        "bubbleWrap" :
          (pysgpp.OptBubbleWrapObjective,        True,   False),
        "easomYang" :
          (pysgpp.OptEasomYangObjective,         True,   False),
        "eggHolder" :
          (pysgpp.OptEggholderObjective,         False,  False),
        "goldsteinPrice" :
          (pysgpp.OptGoldsteinPriceObjective,    False,  False),
        "griewank" :
          (pysgpp.OptGriewankObjective,          True,   False),
        "hartman3" :
          (pysgpp.OptHartman3Objective,          False,  False),
        "hartman6" :
          (pysgpp.OptHartman6Objective,          False,  False),
        "himmelblau" :
          (pysgpp.OptHimmelblauObjective,        False,  True),
        "hoelderTable" :
          (pysgpp.OptHoelderTableObjective,      False,  False),
        "increasingPower" :
          (pysgpp.OptIncreasingPowerObjective,   True,   True),
        "michalewicz" :
          (pysgpp.OptMichalewiczObjective,       False,  True),
        "mladineo" :
          (pysgpp.OptMladineoObjective,          False,  False),
        "perm" :
          (pysgpp.OptPermObjective,              True,   True),
        "rastrigin" :
          (pysgpp.OptRastriginObjective,         True,   True),
        "rosenbrock" :
          (pysgpp.OptRosenbrockObjective,        True,   True),
        "schwefel06" :
          (pysgpp.OptSchwefel06Objective,        False,  False),
        "schwefel22" :
          (pysgpp.OptSchwefel22Objective,        True,   False),
        "schwefel26" :
          (pysgpp.OptSchwefel26Objective,        True,   True),
        "shcb" :
          (pysgpp.OptSHCBObjective,              False,  True),
        "sphere" :
          (pysgpp.OptSphereObjective,            True,   True),
        "tremblingParabola" :
          (pysgpp.OptTremblingParabolaObjective, True,   True),
      }
      fInfo = testFunctionTypes[f]
      if fInfo[2]: warnings.warn("Using trivial test function {}.".format(f))
      args = ([d] if fInfo[1] else [])
      f = fInfo[0](*args)
    
    if f.getNumberOfParameters() != d:
      raise ValueError("Invalid dimensionality.")
    
    super(SGppTestFunction, self).__init__(f)
