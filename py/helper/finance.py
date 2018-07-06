#!/usr/bin/python3

import numpy as np

import helper.basis
import helper.function



class FinanceInterpolant(helper.function.Interpolant):
  def __init__(
        self, basis, X, L, I, fX, aX=None, bounds=None,
        boundsTransformed=None, gridType=None, p=None, struct=None,
        info=None):
    super().__init__(basis, X, L, I, fX, aX=aX)
    self.bounds            = bounds
    self.boundsTransformed = boundsTransformed
    self.gridType          = gridType
    self.p                 = p
    self.struct            = struct
    self.info              = info
  
  @staticmethod
  def fromStruct(struct, info=None):
    X = struct["gridPoints"]
    gridString = struct["gridString"][0]
    L, I = FinanceInterpolant.parseGridString(gridString)
    d = X.shape[1]
    
    bounds = np.row_stack((struct["lowerBounds"], struct["upperBounds"]))
    boundsTransformed = np.row_stack((struct["lbt"], struct["ubt"]))
    
    fX          = struct["values"]
    aX          = struct["surpluses"]
    gridType    = struct["gridType"][0]
    p           = struct["degree"]
    struct      = struct
    domainTrafo = struct["DomainTrafo"]
    valueTrafo  = struct["ValueTrafo"]
    
    p = (p[0,0] if len(p) > 0 else 1)
    
    if gridType == "lagrange-notaknot-spline-boundary":
      basis1D = helper.basis.HierarchicalWeaklyFundamentalSpline(p)
    elif gridType == "linear-boundary":
      assert p == 1
      basis1D = helper.basis.HierarchicalBSpline(p)
    else:
      raise ValueError("Unknown grid type.")
    
    basis = helper.basis.TensorProduct(basis1D, d)
    
    assert domainTrafo.size == 0
    assert valueTrafo.size == 0
    
    interpolant = FinanceInterpolant(
        basis, X, L, I, fX, aX=aX, bounds=bounds,
        boundsTransformed=boundsTransformed, gridType=gridType, p=p,
        struct=struct, info=info)
    
    return interpolant
  
  @staticmethod
  def parseGridString(gridString):
    lines = [x.strip() for x in gridString.splitlines()]
    
    gridType = lines[0]
    del lines[0]
    
    version, d, N = [int(x) for x in lines[0].split()]
    del lines[0]
    
    stretchingMode = int(lines[0])
    assert stretchingMode == 0
    del lines[0]
    
    boundingBox = lines[0]
    assert boundingBox == " ".join(d * ["0.000000e+00 1.000000e+00 0 0"])
    del lines[0]
    
    L, I = [], []
    
    for k in range(N):
      d2 = int(lines[0])
      assert d == d2
      li = [int(x) for x in lines[1].split()]
      L.append(li[0::2])
      I.append(li[1::2])
      leaf = bool(int(lines[2]))
      del lines[:3]
    
    L, I = np.array(L), np.array(I)
    return L, I
  
  def _evaluateBasis(self, k, XX):
    XXunitCube = (XX - self.bounds[0]) / (self.bounds[1] - self.bounds[0])
    return super()._evaluateBasis(k, XXunitCube)



def createJInterpolant(solution, t, discreteStateName, name="interpOptJ"):
  if t < 0: t += solution.size
  return FinanceInterpolant.fromStruct(
      solution[0,t][name][discreteStateName][0,0][0,0],
      info={"name" : name, "t" : t, "T" : solution.size,
            "discreteStateName" : discreteStateName})

def createGradJInterpolant(
      solution, t, discreteStateName, gradientStateName, name="interpGradJ"):
  if t < 0: t += solution.size
  return FinanceInterpolant.fromStruct(
      solution[0,t][name][discreteStateName][0,0][gradientStateName][0,0][0,0],
      info={"name" : name, "t" : t, "T" : solution.size,
            "discreteStateName" : discreteStateName,
            "gradientStateName" : gradientStateName})

def createPolicyInterpolant(interpPolicy, t, discreteStateName, policyName):
  if t < 0: t += interpPolicy.size
  return FinanceInterpolant.fromStruct(
      interpPolicy[0,t][discreteStateName][0,0][policyName][0,0],
      info={"name" : "interpPolicy", "t" : t, "T" : interpPolicy.size,
            "discreteStateName" : discreteStateName,
            "policyName" : policyName})
