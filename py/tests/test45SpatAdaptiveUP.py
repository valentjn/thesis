#!/usr/bin/python3

import functools
import multiprocessing
import random
import unittest

import numpy as np
import scipy.special

import helper.basis
import helper.grid
import tests.misc

class Test45SpatAdaptiveUP(tests.misc.CustomTestCase):
  @staticmethod
  def createDataHermiteHierarchization(p):
    n, d, b = 4, 1, 0
    bases = [helper.basis.HierarchicalWeaklyFundamentalSpline(p, nu=nu)
            for nu in range((p+1)//2)]
    grid = helper.grid.RegularSparseBoundary(n, d, b)
    X, L, I = grid.generate()
    X, L, I = X.flatten(), L.flatten(), I.flatten()
    K = np.column_stack((L, I))
    f = (lambda x: 0.3 + np.sin(2.3*np.pi*(X-0.2)))
    fX = f(X)
    
    return bases, n, X, L, I, K, fX
  
  def hermiteHierarchizationCallback(self, fl, y, l, K, bases):
    p = bases[0].p
    nodalIl = helper.grid.getNodalIndices1D(l)
    Kl = np.array([self.findLevelIndex(K, l, i) for i in nodalIl])
    Xl = helper.grid.getCoordinates(l, nodalIl)
    
    for q in range((p+1)//2):
      Yl = np.zeros_like(Xl)
      
      for lp in range(l+1):
        hierIlp = helper.grid.getHierarchicalIndices1D(lp)
        for ip in hierIlp:
          Yl += (y[self.findLevelIndex(K, lp, ip)] *
                 bases[q].evaluate(lp, ip, Xl))
      
      self.assertAlmostEqual(Yl, fl[l][Kl,q])
  
  @staticmethod
  def findLevelIndex(K, l, i):
    lp, ip = helper.grid.convertNodalToHierarchical1D(l, i)
    return (np.where((K == (lp, ip)).all(axis=1))[0][0])
  
  @staticmethod
  def dividedDifference(data):
    # data in the form
    # [(a, f(a), df(a), ...), (b, f(b), df(b), ...), ...]
    if len(data) == 1:
      return data[0][-1] / scipy.special.factorial(len(data[0]) - 2)
    else:
      dataLeft = list(data)
      if len(dataLeft[-1]) > 2: dataLeft[-1] = dataLeft[-1][:-1]
      else:                     del dataLeft[-1]
      
      dataRight = list(data)
      if len(dataRight[0]) > 2: dataRight[0] = dataRight[0][:-1]
      else:                     del dataRight[0]
      
      return((Test45SpatAdaptiveUP.dividedDifference(dataRight) -
              Test45SpatAdaptiveUP.dividedDifference(dataLeft)) /
            (data[-1][0] - data[0][0]))

  @staticmethod
  def hermiteInterpolation1D(xx, data, nu=0):
    # data in the form
    # [(a, f(a), df(a), ...), (b, f(b), df(b), ...), ...]
    yy = np.zeros((len(xx), nu+1))
    xProduct = [1] + (nu * [0])
    curXData = []
    curData = []
    
    for dataPoint in data:
      x = dataPoint[0]
      curData.append([x])
      
      for k in range(1, len(dataPoint)):
        curData[-1].append(dataPoint[k])
        coeff = Test45SpatAdaptiveUP.dividedDifference(curData)
        
        for q in range(nu, -1, -1):
          yy[:,q] += coeff * xProduct[q]
          xProduct[q] = (xProduct[q] * (xx - x) +
                        q * (xProduct[q-1] if q > 0 else 0))
    
    return yy
  
  @staticmethod
  def hermiteHierarchization1D(u, n, K, bases, testCallback=None):
    N = u.shape[0]
    p = bases[0].p
    y = np.zeros((N,))
    fl = np.zeros((n+1, N, (p+1)//2))
    
    k0 = Test45SpatAdaptiveUP.findLevelIndex(K, 0, 0)
    k1 = Test45SpatAdaptiveUP.findLevelIndex(K, 0, 1)
    
    for i in range(2):
      k = (k0 if i == 0 else k1)
      y[k] = u[k]
      fl[0][k][0] = u[k]
      if p > 1: fl[0][k][1] = (u[k1] - u[k0])
    
    for l in range(1, n+1):
      nodalIl = helper.grid.getNodalIndices1D(l)
      Kl = np.array([Test45SpatAdaptiveUP.findLevelIndex(K, l, i)
                     for i in nodalIl])
      Xl = helper.grid.getCoordinates(l, nodalIl)
      
      hierIl = np.array(helper.grid.getHierarchicalIndices1D(l))
      flm1 = np.zeros((len(nodalIl), (p+1)//2))
      
      evenIl = [i for i in nodalIl if i not in hierIl]
      flm1[evenIl] = fl[l-1][Kl[evenIl]]
      
      for i in hierIl:
        data = [np.hstack((Xl[i-1], flm1[i-1])),
                np.hstack((Xl[i+1], flm1[i+1]))]
        flm1[i] = Test45SpatAdaptiveUP.hermiteInterpolation1D(
            [Xl[i]], data, nu=(p-1)//2)
      
      rl = np.zeros_like(nodalIl, dtype=float)
      rl[hierIl] = u[Kl[hierIl]] - flm1[hierIl][:,0]
      
      A = np.zeros((len(hierIl), len(hierIl)))
      for i in hierIl: A[:,(i-1)//2] = bases[0].evaluate(l, i, Xl[hierIl])
      b = rl[hierIl]
      yl = np.linalg.solve(A, b)
      y[Kl[hierIl]] = yl
      
      for q in range((p+1)//2):
        rl = np.zeros_like(nodalIl, dtype=float)
        for i in hierIl: rl += y[Kl[i]] * bases[q].evaluate(l, i, Xl)
        for i in nodalIl: fl[l][Kl[i]][q] = flm1[i][q] + rl[i]
      
      if testCallback is not None: testCallback(fl, y, l, K, bases)
    
    return y
  
  @staticmethod
  def iterativeRefinement(u, y0, Linv, Lp):
    r = u - Linv(y0)
    y = np.array(y0)
    
    for m in range(1000):
      if np.max(np.abs(r)) < 1e-10: break
      y += Lp(r)
      r -= Linv(Lp(r))
    
    return y, r
  
  @staticmethod
  def getChain(l1, i1, l2, i2, T):
    chain = [(np.array(l1), np.array(i1))]
    
    for t in T:
      lNext, iNext = chain[-1]
      lNext, iNext = np.array(lNext), np.array(iNext)
      lNext[t], iNext[t] = l2[t], i2[t]
      chain.append((lNext, iNext))
    
    if np.all(chain[-1][0] == l2) and np.all(chain[-1][1] == i2):
      return chain
    else:
      return None
  
  def testLemmaIterativeRefinementEquivalent(self):
    # tested in testPropIterativeRefinementSufficient
    pass
  
  def testPropIterativeRefinementSufficient(self):
    tol = {"rtol" : 1e-3, "atol" : 1e-8}
    
    for p in [1, 3, 5, 7]:
      basisLin1D = helper.basis.HierarchicalBSpline(1)
      basis1D = helper.basis.HierarchicalBSpline(p)
      
      for d in range(1, 5):
        f = tests.misc.getObjectiveFunction(d)
        basisLin = (helper.basis.TensorProduct(basisLin1D, d) if d > 1 else
                    basisLin1D)
        basis = (helper.basis.TensorProduct(basis1D, d) if d > 1 else
                 basis1D)
        
        with self.subTest(p=p, d=d):
          X, L, I = tests.misc.generateSpatiallyAdaptiveSparseGrid(
              d, 500)
          fX = f(X)
          
          A = tests.misc.computeInterpolationMatrix(basis, X, L, I)
          aX = np.linalg.solve(A, fX)
          
          ALin = tests.misc.computeInterpolationMatrix(basisLin, X, L, I)
          ALinInv = np.linalg.inv(ALin)
          
          Linv = (lambda x: np.dot(A, x))
          Lp   = (lambda x: np.dot(ALinInv, x))
          
          u = fX
          y0 = 2 * np.random.random((X.shape[0],)) - 1
          y, r = self.iterativeRefinement(u, y0, Linv, Lp)
          
          if np.max(np.abs(r)) < 1e-10:
            self.assertAlmostEqual(y, aX, **tol)
          else:
            self.assertNotAlmostEqual(y, aX, **tol)
          
          N = X.shape[0]
          m = 100
          power = np.linalg.matrix_power(np.eye(N) - np.dot(A, ALinInv), m)
          powerNormRoot = np.power(np.linalg.norm(power), 1/m)
          
          if powerNormRoot < 1:
            self.assertAlmostEqual(y, aX, **tol)
  
  def testLemmaDualityUnidirectionalPrinciple(self):
    n, b = 4, 0
    hierarchical = True
    bases = tests.misc.getExampleHierarchicalBases()
    
    for basisName, d, basis in bases:
      f = tests.misc.getObjectiveFunction(d)
      modified = ("Modified" in basisName)
      if "ClenshawCurtis" in basisName: distribution = "clenshawCurtis"
      else:                             distribution = "uniform"
      
      with self.subTest(basis=basisName, d=d):
        #X, L, I = tests.misc.generateSpatiallyAdaptiveSparseGrid(
        #    d, 500)
        grid = (helper.grid.RegularSparse(n, d) if modified else
                helper.grid.RegularSparseBoundary(n, d, b))
        X, L, I = grid.generate()
        if distribution != "uniform":
          X = helper.grid.getCoordinates(L, I, distribution=distribution)
        
        fX = f(X)
        
        u = np.array(fX)
        K = tests.misc.convertToContinuous(L, I)
        T = np.arange(d)
        np.random.shuffle(T)
        L1D = functools.partial(tests.misc.hierarchize1D,
                                basis, distribution, hierarchical)
        bases1D = (basis.basis1D if d > 1 else [basis])
        y = tests.misc.unidirectionalPrinciple(u, K, T, L1D)
        
        TRev = T[::-1]
        LInv1D = functools.partial(tests.misc.hierarchize1D,
                                   basis, distribution, hierarchical,
                                   mode="dehierarchize")
        u2 = tests.misc.unidirectionalPrinciple(y, K, TRev, LInv1D)
        
        if d == 1: X, L, I = X.flatten(), L.flatten(), I.flatten()
        A = tests.misc.computeInterpolationMatrix(basis, X, L, I)
        aX = np.linalg.solve(A, fX)
        fX2 = np.dot(A, y)
        
        try:
          self.assertAlmostEqual(y, aX, atol=1e-10)
          upCorrect = True
        except AssertionError:
          upCorrect = False
        
        try:
          self.assertAlmostEqual(u2, fX2, atol=1e-10)
          upInvCorrect = True
        except AssertionError:
          upInvCorrect = False
        
        if upCorrect: self.assertTrue(upInvCorrect)
        else:         self.assertFalse(upInvCorrect)
        
        N = X.shape[0]
        LI = np.column_stack((L, I))
        containsAllChains = True
        
        if d == 1:
          X = np.reshape(X, (N,1))
          L = np.reshape(L, (N,1))
          I = np.reshape(I, (N,1))
        
        for k1 in range(N):
          if not containsAllChains: break
        
          for k2 in range(N):
            if not containsAllChains: break
            
            if np.abs(A[k2,k1]) > 1e-12:
              chain = self.getChain(L[k1], I[k1], L[k2], I[k2], TRev)
              
              for l, i in chain:
                li = np.hstack((l, i))
                
                if not np.any(np.all(LI == li, axis=1)):
                  containsAllChains = False
                  break
        
        if upCorrect: self.assertTrue(containsAllChains)
        else:         self.assertFalse(containsAllChains)
  
  @staticmethod
  def calculateA1D(getL1D, data):
    t, KPole = data
    K1D = np.array([k[t] for k in KPole])
    A1D = getL1D(t, K1D)
    return A1D
  
  def testLemmaChainExistenceSufficient(self):
    p = 3
    hierarchical = True
    basis1D = helper.basis.HierarchicalBSpline(p)
    
    for d in range(1, 5):
      basisName = "{}({})".format(type(basis1D).__name__, p)
      modified = ("Modified" in basisName)
      if "ClenshawCurtis" in basisName: distribution = "clenshawCurtis"
      else:                             distribution = "uniform"
      
      basis = (helper.basis.TensorProduct(basis1D, d) if d > 1 else
               basis1D)
      
      with self.subTest(d=d):
        X, L, I = tests.misc.generateSpatiallyAdaptiveSparseGrid(
            d, 200)
        #grid = (helper.grid.RegularSparse(n, d) if modified else
        #        helper.grid.RegularSparseBoundary(n, d, b))
        #X, L, I = grid.generate()
        if distribution != "uniform":
          X = helper.grid.getCoordinates(L, I, distribution=distribution)
        
        K = tests.misc.convertToContinuous(L, I)
        T = np.arange(d)
        np.random.shuffle(T)
        getL1D = functools.partial(tests.misc.hierarchize1D,
            basis, distribution, hierarchical, None, mode="matrix")
        N = X.shape[0]
        As = [np.eye(N)]
        
        KTuples = [tuple(k) for k in K]
        allKPoles = []
        
        for t in T:
          isOnSamePole = functools.partial(tests.misc.isOnSamePole,
                                           t, d)
          KPoles = helper.misc.getEquivalenceClasses(KTuples, isOnSamePole)
          allKPoles.extend([(t, tuple(sorted(KPole))) for KPole in KPoles])
        
        with multiprocessing.Pool() as pool:
          A1Ds = pool.map(functools.partial(self.calculateA1D, getL1D),
                          allKPoles)
        
        A1Ds = dict(zip(allKPoles, A1Ds))
        
        for t in T:
          isOnSamePole = functools.partial(tests.misc.isOnSamePole,
                                           t, d)
          KPoles = helper.misc.getEquivalenceClasses(K, isOnSamePole)
          At = np.zeros((N, N))
          
          for KPole in KPoles:
            KPoleTuple = tuple(sorted([tuple(k.tolist()) for k in KPole]))
            A1D = A1Ds[(t, KPoleTuple)]
            N1D = A1D.shape[0]
            
            Q = [np.where(np.all(K == k, axis=1))[0][0] for k in KPole]
            
            for r1 in range(N1D):
              for r2 in range(N1D):
                At[Q[r2],Q[r1]] = A1D[r2,r1]
          
          As.append(np.dot(At, As[-1]))
        
        LI = np.column_stack((L, I))
        
        for j in range(d+1):
          for k1 in range(N):
            for k2 in range(N):
              chain = self.getChain(L[k1,:], I[k1,:],
                                    L[k2,:], I[k2,:], T[:j])
              if chain is not None:
                chain = tests.misc.convertToContinuous(
                    np.array([x[0] for x in chain]),
                    np.array([x[1] for x in chain]))
                containsChain = all([np.any(np.all(K == k, axis=1))
                                    for k in chain])
              else:
                containsChain = False
              
              if np.abs(As[j][k2,k1]) > 1e-10:
                self.assertTrue(containsChain)
              
              if containsChain:
                rhs = 1
                
                for t, kj in zip(T[:j], chain[1:]):
                  isOnSamePole = functools.partial(tests.misc.isOnSamePole,
                                                   t, d)
                  KPole = [k for k in K if isOnSamePole(k, kj)]
                  KPoleTuple = tuple(sorted([tuple(k.tolist())
                                             for k in KPole]))
                  A1D = A1Ds[(t, KPoleTuple)]
                  
                  K1D = np.array([k[t] for k in KPole])
                  r1 = np.where(K1D == K[k1,t])[0][0]
                  r2 = np.where(K1D == K[k2,t])[0][0]
                  rhs *= A1D[r2,r1]
                
                lhs = As[j][k2,k1]
                self.assertAlmostEqual(lhs, rhs)
  
  def testLemmaChainExistenceNecessary(self):
    # tested in testLemmaChainExistenceSufficient
    pass
  
  def testPropCorrectnessUPCharacterization(self):
    # tested in testLemmaDualityUnidirectionalPrinciple
    pass
  
  def testCorEquivalentCorrectnessUPHierarchization(self):
    # tested in testLemmaDualityUnidirectionalPrinciple
    pass
  
  def testLemmaHermiteInterpolation(self):
    a = random.uniform(0, 3)
    b = a + random.uniform(2, 4)
    
    for p in [1, 3, 5, 7]:
      data = [[a] + [random.gauss(0, 2) for x in range((p+1)//2)],
              [b] + [random.gauss(0, 2) for x in range((p+1)//2)]]
      
      for nu in range((p+1)//2):
        y = self.hermiteInterpolation1D(np.array([a, b]), data, nu=nu)
        y2 = np.row_stack((data[0][1:nu+2], data[1][1:nu+2]))
        self.assertAlmostEqual(y, y2)
  
  def testPropInvariantHermiteHierarchization(self):
    for p in [1, 3, 5, 7]:
      bases, n, X, L, I, K, fX = self.createDataHermiteHierarchization(p)
      callback = self.hermiteHierarchizationCallback
      self.hermiteHierarchization1D(fX, n, K, bases, testCallback=callback)
  
  def testCorAlgHermiteHierarchizationCorrectness(self):
    for p in [1, 3, 5, 7]:
      bases, n, X, L, I, K, fX = self.createDataHermiteHierarchization(p)
      aX = self.hermiteHierarchization1D(fX, n, K, bases)
      Y = np.zeros_like(X)
      for k in range(X.shape[0]): Y += aX[k] * bases[0].evaluate(L[k], I[k], X)
      self.assertAlmostEqual(Y, fX)



if __name__ == "__main__":
  unittest.main()
