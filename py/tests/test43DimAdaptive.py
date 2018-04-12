#!/usr/bin/python3

import functools
import multiprocessing
import unittest

import numpy as np
import scipy.special

import helper.basis
import helper.grid
import helper.misc
import tests.misc

class Test43DimAdaptive(tests.misc.CustomTestCase):
  @staticmethod
  def computeContribution(basisName, basis, distribution, f, XX, l):
    A, L, I = tests.misc.computeFullGridMatrix(
        basisName, basis, l, distribution=distribution,
        hierarchical=True, parallel=False)
    X = helper.grid.getCoordinates(L, I, distribution=distribution)
    fX = f(X)
    aX = np.linalg.solve(A, fX)
    
    N = X.shape[0]
    flXX = np.zeros((XX.shape[0],))
    for k in range(N): flXX += aX[k] * basis.evaluate(L[k], I[k], XX)
    
    return (flXX, L, I, aX)
  
  @staticmethod
  def enumerateLevelsWithSum(n, d):
    if (d <= 0) or (n < 0):
      L = []
    elif d == 1:
      L = [[n]]
    elif n == 0:
      L = [d * [0]]
    else:
      L = [[l1] + l
           for l1 in range(n+1)
           for l in Test43DimAdaptive.enumerateLevelsWithSum(n-l1, d-1)]
    
    return L
  
  @staticmethod
  def generateActiveGrids(activeLs, modified=False, distribution="uniform"):
    d = len(activeLs[0])
    Xs, Ls, Is = [], [], []
    
    for l in activeLs:
      if modified:
        X, L, I = helper.grid.Full(l).generate()
      else:
        X, L, I = helper.grid.FullBoundary(l).generate()
      
      X = helper.grid.getCoordinates(L, I, distribution=distribution)
      Xs.append(X)
      Ls.append(L)
      Is.append(I)
    
    LItotal = np.column_stack((np.row_stack(Ls), np.row_stack(Is)))
    LItotal = np.unique(LItotal, axis=0)
    Ltotal, Itotal = LItotal[:,:d], LItotal[:,d:]
    Xtotal = helper.grid.getCoordinates(Ltotal, Itotal,
                                        distribution=distribution)
    
    return Xs, Ls, Is, Xtotal, LItotal
  
  @staticmethod
  def residualInterpolation(
        u, Xs, Ls, Is, Xtotal, LItotal, basis, testCallback=None):
    y = np.zeros_like(u)
    rXtotal = np.array(u)
    j = 0
    
    for X, L, I in zip(Xs, Ls, Is):
      LI = np.column_stack((L, I))
      K = [np.where(np.all(LItotal == li, axis=1))[0][0] for li in LI]
      interpolant = helper.function.Interpolant(basis, X, L, I, rXtotal[K])
      fX = interpolant.evaluate(Xtotal)
      rXtotal -= fX
      for q in range(len(K)): y[K[q]] += interpolant.aX[q]
      
      if testCallback is not None:
        testCallback(
            u, Xs, Ls, Is, Xtotal, LItotal, basis, j, interpolant, y, rXtotal)
      
      j += 1
    
    return y
  
  def residualInterpolationCallback(self, fXtotal, Xs, Ls, Is, Xtotal, LItotal,
                                    basis, j, interpolant, y, rXtotal):
    if j > 0:
      unionX = np.unique(np.row_stack(Xs[:j]), axis=0)
      fUnionX = interpolant.evaluate(unionX)
      self.assertAlmostEqual(fUnionX, np.zeros_like(fUnionX), atol=1e-12)
    
    unionLI = np.unique(np.column_stack(
        (np.row_stack(Ls[:j+1]), np.row_stack(Is[:j+1]))), axis=0)
    K = [np.where(np.all(LItotal == li, axis=1))[0][0] for li in unionLI]
    self.assertAlmostEqual(rXtotal[K], np.zeros_like(rXtotal[K]), atol=1e-12)
    
    d = Xtotal.shape[1]
    if d == 1: Xtotal = Xtotal.flatten()
    rhs = np.array(fXtotal)
    for k in range(LItotal.shape[0]):
      l, i = LItotal[k,:d], LItotal[k,d:]
      if d == 1: l, i = l[0], i[0]
      rhs -= y[k] * basis.evaluate(l, i, Xtotal)
    self.assertAlmostEqual(rXtotal, rhs, atol=1e-12)
  
  def testThmCombiTechnique(self):
    n, b = 4, 0
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      basis1D = (basis.basis1D[0]
                 if isinstance(basis, helper.basis.TensorProduct) else
                 basis)
      p = getattr(basis1D, "p", None)
      
      if "Modified" in basisName: continue
      if d >= 4: continue
      if (p is not None) and (p >= 7): continue
      if ("Natural" in basisName) and (p >= 5):
        if d >= 3: continue
      
      valid = ((p == 1) or
               (d == 1) or
               ("NotAKnot" in basisName) or
               ("Natural" in basisName) or
               ("LagrangePolynomial" in basisName))
      if not valid: continue
      
      with self.subTest(basis=basisName, d=d):
        if "ClenshawCurtis" in basisName:
          distribution = "clenshawCurtis"
        else:
          distribution = "uniform"
        
        f = tests.misc.getObjectiveFunction(d)
        XX = np.random.random((10, d))
        if d == 1: XX = XX.flatten()
        fctXX = np.zeros((XX.shape[0],))
        
        Ls = [l for q in range(d)
              for l in self.enumerateLevelsWithSum(n-q, d)]
        
        with multiprocessing.Pool() as pool:
          data = pool.map(functools.partial(
              self.computeContribution, basisName, basis,
              distribution, f, XX), Ls)
        
        flXXs = [flXX[0] for flXX in data]
        
        r = 0
        
        for q in range(d):
          factor = (-1)**q * scipy.special.binom(d-1, q)
          curLs = self.enumerateLevelsWithSum(n-q, d)
          
          for l in curLs:
            fctXX += factor * flXXs[r]
            r += 1
        
        grid = helper.grid.RegularSparseBoundary(n, d, b)
        X, L, I = grid.generate()
        X = helper.grid.getCoordinates(L, I, distribution=distribution)
        fX = f(X)
        interpolant = helper.function.Interpolant(basis, X, L, I, fX)
        fsXX = interpolant.evaluate(XX)
        
        self.assertAlmostEqual(fctXX, fsXX)
        
        N = X.shape[0]
        aXct = np.zeros((N,))
        
        for k in range(N):
          r = -1
          
          for q in range(d):
            factor = (-1)**q * scipy.special.binom(d-1, q)
            curLs = self.enumerateLevelsWithSum(n-q, d)
            
            for l in curLs:
              r += 1
              curL, curI, curAX = data[r][1:]
              result = np.where(np.all(np.column_stack((curL, curI)) ==
                                       np.hstack((L[k,:], I[k,:])), axis=1))[0]
              if len(result) == 0: continue
              self.assertEqual(len(result), 1)
              aXct[k] += factor * curAX[result[0]]
        
        self.assertAlmostEqual(aXct, interpolant.aX, atol=1e-10)
  
  def testPropCombiTechniqueOne(self):
    b = 0
    
    for d in range(1, 5):
      for n in range(6):
        with self.subTest(d=d, n=n):
          X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
          N = X.shape[0]
          
          for k in range(N):
            lhs = 0
            
            for q in range(d):
              Ls = self.enumerateLevelsWithSum(n-q, d)
              setSize = len([l for l in Ls if np.all(L[k,:] <= l)])
              lhs += (-1)**q * scipy.special.binom(d-1, q) * setSize
            
            self.assertEqual(lhs, 1)
  
  def testLemmaCombiTechniqueIdenticalValues(self):
    b, p, distribution = 0, 3, "uniform"
    basis1D = helper.basis.HierarchicalBSpline(p)
    basisName = "{}({})".format(type(basis1D).__name__, p)
    
    for d in range(1, 4):
      basis = helper.basis.TensorProduct(basis1D, d)
      f = tests.misc.getObjectiveFunction(d)
      
      for n in range(7-d):
        with self.subTest(d=d, n=n):
          X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
          N = X.shape[0]
          
          with multiprocessing.Pool() as pool:
            for k in range(N):
              Ls = [l for q in range(d)
                  for l in self.enumerateLevelsWithSum(n-q, d)
                  if not np.all(L[k,:] <= l)]
              
              if len(Ls) == 0: continue
              
              isEquivalent = (lambda l1, l2:
                  all([((l1[t] == l2[t]) or (min(l1[t], l2[t]) >= L[k,t]))
                      for t in range(d)]))
              
              flxs = pool.map(functools.partial(
                  self.computeContribution, basisName, basis,
                  distribution, f, np.array([X[k,:]])), Ls)
              
              #for r1 in range(len(Ls)):
              #  for r2 in range(len(Ls)):
              #    if isEquivalent(Ls[r1], Ls[r2]):
              #      self.assertAlmostEqual(flxs[r1][0], flxs[r2][0])
              
              equivalenceClasses = helper.misc.getEquivalenceClasses(
                Ls, isEquivalent)
              Ls = np.array(Ls)
              
              for L0 in equivalenceClasses:
                flxs1 = None
                for l in L0:
                  flxs2 = flxs[np.where(np.all(Ls == l, axis=1))[0][0]][0]
                  if flxs1 is None: flxs1 = flxs2
                  else:             self.assertAlmostEqual(flxs1, flxs2)
  
  def testLemmaCombiTechniqueCharacterization(self):
    b = 0
    
    for d in range(1, 4):
      for n in range(7-d):
        with self.subTest(d=d, n=n):
          X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
          N = X.shape[0]
          
          for k in range(N):
            Ls = [l for q in range(d)
                for l in self.enumerateLevelsWithSum(n-q, d)
                if not np.all(L[k,:] <= l)]
            
            if len(Ls) == 0: continue
            
            isEquivalent = (lambda l1, l2:
                all([((l1[t] == l2[t]) or (min(l1[t], l2[t]) >= L[k,t]))
                    for t in range(d)]))
            equivalenceClasses = helper.misc.getEquivalenceClasses(
              Ls, isEquivalent)
            
            for L0 in equivalenceClasses:
              lStar = -1 * np.ones((d,), dtype=int)
              tInTL0 = d * [True]
              
              for l in L0:
                for t in range(d):
                  if tInTL0[t]:
                    if lStar[t] == -1:
                      lStar[t] = l[t]
                    elif l[t] != lStar[t]:
                      tInTL0[t] = False
              
              for l in Ls:
                isInLHS = (l in L0)
                isInRHS = True
                
                for t in range(d):
                  if tInTL0[t]:
                    if l[t] != lStar[t]:
                      isInRHS = False
                      break
                  else:
                    if l[t] < L[k,t]:
                      isInRHS = False
                      break
                
                self.assertEqual(isInLHS, isInRHS)
  
  def testPropCombiTechniqueZero(self):
    b, p, distribution = 0, 3, "uniform"
    basis1D = helper.basis.HierarchicalBSpline(p)
    basisName = "{}({})".format(type(basis1D).__name__, p)
    
    for d in range(1, 4):
      basis = helper.basis.TensorProduct(basis1D, d)
      f = tests.misc.getObjectiveFunction(d)
      
      for n in range(7-d):
        with self.subTest(d=d, n=n):
          X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
          N = X.shape[0]
          
          with multiprocessing.Pool() as pool:
            for k in range(N):
              Ls = [l for q in range(d)
                  for l in self.enumerateLevelsWithSum(n-q, d)
                  if not np.all(L[k,:] <= l)]
              
              if len(Ls) == 0: continue
              
              isEquivalent = (lambda l1, l2:
                  all([((l1[t] == l2[t]) or (min(l1[t], l2[t]) >= L[k,t]))
                      for t in range(d)]))
              
              flxs = pool.map(functools.partial(
                  self.computeContribution, basisName, basis,
                  distribution, f, np.array([X[k,:]])), Ls)
              
              lhs = 0
              r = 0
              
              for q in range(d):
                curLs = self.enumerateLevelsWithSum(n-q, d)
                innerSum = 0
                
                for l in curLs:
                  if not np.all(L[k,:] <= l):
                    innerSum += flxs[r][0]
                    r += 1
                
                lhs += (-1)**q * scipy.special.binom(d-1, q) * innerSum
              
              self.assertAlmostEqual(lhs, 0, atol=1e-10)
  
  def testPropCorrectnessAlgCombiTechnique(self):
    # tested in testThmCombiTechnique
    pass
  
  def testPropInvariantResidualInterpolation(self):
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      f = tests.misc.getObjectiveFunction(d)
      modified = ("Modified" in basisName)
      if "ClenshawCurtis" in basisName: distribution = "clenshawCurtis"
      else:                             distribution = "uniform"
      
      basis1D = (basis.basis1D[0]
                 if isinstance(basis, helper.basis.TensorProduct) else
                 basis)
      p = getattr(basis1D, "p", None)
      
      if d >= 4: continue
      if modified and ("NotAKnot" in basisName) and (d >= 3): continue
      if (p is not None) and (p >= 7): continue
      if basisName.startswith("HierarchicalFundamentalSpline") and (d >= 3):
        continue
      if basisName.startswith("HierarchicalNaturalBSpline") and (d >= 3):
        continue
      
      with self.subTest(basis=basisName, d=d):
        activeLs = []
        minLevel = (1 if modified else 0)
        
        for r in range(10):
          l = [np.random.randint(minLevel, 5) for d in range(d)]
          skip = any([all([l[t] <= l2[t] for t in range(d)])
                      for l2 in activeLs])
          if skip: continue
          activeLs.append(l)
          
          for j in range(len(activeLs) - 2, -1, -1):
            l2 = activeLs[j]
            if all([l2[t] <= l[t] for t in range(d)]): del activeLs[j]
        
        activeLs.sort(key=lambda l: -sum(l))
        
        Xs, Ls, Is, Xtotal, LItotal = self.generateActiveGrids(
            activeLs, modified=modified, distribution=distribution)
        fXtotal = f(Xtotal)
        
        u = fXtotal
        testCallback = self.residualInterpolationCallback
        y = self.residualInterpolation(
            u, Xs, Ls, Is, Xtotal, LItotal, basis, testCallback=testCallback)
        
        Ltotal, Itotal = LItotal[:,:d], LItotal[:,d:]
        interpolant = helper.function.Interpolant(
          basis, Xtotal, Ltotal, Itotal, fXtotal)
        aX = interpolant.aX
        
        self.assertAlmostEqual(y, aX, rtol=1e-6, atol=1e-10)
  
  def testCorAlgResidualInterpolationCorrectness(self):
    # tested in testPropInvariantResidualInterpolation
    pass



if __name__ == "__main__":
  unittest.main()
