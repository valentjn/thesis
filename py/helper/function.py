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
    super(Interpolant, self).__init__(X.shape[1])
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
    N = self.X.shape[0]
    YY = np.zeros((XX.shape[0],))
    
    for k in range(N):
      YY += self.aX[k] * self._evaluateBasis(k, XX)
    
    return YY



class SGppFunction(Function):
  def __init__(self, f):
    super(SGppFunction, self).__init__(f.getNumberOfParameters())
    self.f = f
  
  def evaluate(self, XX):
    import pysgpp
    #yy = np.array([self.f.eval(X) for X in XX])
    yy = pysgpp.DataVector(XX.shape[0])
    self.f.eval(np2sgpp(XX), yy)
    yy = sgpp2np(yy)
    return yy



class SGppInterpolant(SGppFunction):
  def __init__(self, grid, fX):
    import pysgpp
    self.grid = grid
    self.fX = fX
    self.aX = self._getSurpluses()
    f = pysgpp.OptInterpolantScalarFunction(grid, np2sgpp(self.aX))
    super(SGppInterpolant, self).__init__(f)
  
  def _getSurpluses(self):
    import pysgpp
    aX = pysgpp.DataVector(self.fX.size)
    hierarchizationSLE = pysgpp.OptHierarchisationSLE(self.grid)
    sleSolver = pysgpp.OptAutoSLESolver()
    assert sleSolver.solve(hierarchizationSLE, np2sgpp(self.fX), aX)
    return sgpp2np(aX)



class SGppTestFunction(SGppFunction):
  def __init__(self, f, d):
    if type(f) is str:
      import pysgpp
      testFunctionTypes = {
        "ackley" :
          (pysgpp.OptAckley,            True,   False),
        "absoluteValue" :
          (pysgpp.OptAbsoluteValue,     True,   True),
        "beale" :
          (pysgpp.OptBeale,             False,  False),
        "branin" :
          (pysgpp.OptBranin,            False,  True),
        "bubbleWrap" :
          (pysgpp.OptBubbleWrap,        True,   False),
        "easomYang" :
          (pysgpp.OptEasomYang,         True,   False),
        "eggholder" :
          (pysgpp.OptEggholder,         False,  False),
        "goldsteinPrice" :
          (pysgpp.OptGoldsteinPrice,    False,  False),
        "griewank" :
          (pysgpp.OptGriewank,          True,   False),
        "hartman3" :
          (pysgpp.OptHartman3,          False,  False),
        "hartman6" :
          (pysgpp.OptHartman6,          False,  False),
        "himmelblau" :
          (pysgpp.OptHimmelblau,        False,  True),
        "hoelderTable" :
          (pysgpp.OptHoelderTable,      False,  False),
        "increasingPower" :
          (pysgpp.OptIncreasingPower,   True,   True),
        "michalewicz" :
          (pysgpp.OptMichalewicz,       False,  True),
        "mladineo" :
          (pysgpp.OptMladineo,          False,  False),
        "perm" :
          (pysgpp.OptPerm,              True,   True),
        "rastrigin" :
          (pysgpp.OptRastrigin,         True,   True),
        "rosenbrock" :
          (pysgpp.OptRosenbrock,        True,   True),
        "schwefel" :
          (pysgpp.OptSchwefel,          True,   True),
        "shcb" :
          (pysgpp.OptSHCB,              False,  True),
        "sphere" :
          (pysgpp.OptSphere,            True,   True),
        "tremblingParabola" :
          (pysgpp.OptTremblingParabola, True,   True),
      }
      fInfo = testFunctionTypes[f]
      if fInfo[2]: warnings.warn("Using trivial test function {}.".format(f))
      args = ([d] if fInfo[1] else [])
      problem = fInfo[0](*args)
      f = problem.getObjectiveFunction()
    
    if f.getNumberOfParameters() != d: raise ValueError("Invalid dimensionality.")
    super(SGppTestFunction, self).__init__(f)
