#!/usr/bin/python3

import numpy as np
import sympy as sp
from sympy.abc import x



class Spline(object):
  def __init__(self, knots, pieces):
    assert(len(knots) == len(pieces) + 1)
    self._knots = tuple(knots)
    self._pieces = pieces
    self._maxima = None
    self._minima = None
  
  def differentiate(self, times=1):
    derivative_pieces = [piece.differentiate(times=times) for piece in self.pieces]
    return Spline(self.knots, derivative_pieces)
  
  def dx(self, times=1):
    return self.differentiate(times=times)
  
  def evaluate(self, xx):
    return sp.lambdify(x, self.getFunction().as_expr())(xx)
  
  def getFunction(self):
    pieces = [(0, True)]
    
    for k in range(len(self.knots) - 1):
      condition = (x > self.knots[k])
      function = self.pieces[k].getFunction().as_expr()
      pieces.append((function, condition))
    
    pieces.append((0, x > self.knots[-1]))
    return sp.Piecewise(*pieces[::-1])
  
  def restrict(self, a, b):
    i = self.knots.index(a)
    j = self.knots.index(b)
    return Spline(self.knots[i:j+1], self.pieces[i:j])
  
  def _optimize(self):
    TOL = 1e-6
    self._maxima = []
    self._minima = []
    in_with_tol = lambda x0, x_list: any([abs(x1 - x0) < TOL for x1 in x_list])
    
    for piece in self.pieces:
      if piece.degree == 1:
        pieceL = piece.evaluate(piece.a)
        pieceR = piece.evaluate(piece.b)
        if pieceL < pieceR:
          if not in_with_tol(piece.a, self._minima):
            self._minima.append(piece.a.n())
          if not in_with_tol(piece.b, self._maxima):
            self._maxima.append(piece.b.n())
        else:
          if not in_with_tol(piece.a, self._maxima):
            self._maxima.append(piece.a.n())
          if not in_with_tol(piece.b, self._minima):
            self._minima.append(piece.b.n())
      else:
        pieceDx = piece.dx()
        pieceDx2 = pieceDx.dx()
        roots = sorted([root[0] for root in pieceDx.getFunction().roots(ring=RR)])
        for root in roots:
          if ((piece.a - TOL <= root <= piece.b + TOL) and
              (self.knots[0] + TOL <= root <= self.knots[-1] - TOL)):
            if pieceDx2.evaluate(root) < 0:
              if not in_with_tol(root, self._maxima):
                self._maxima.append(root)
            else:
              if not in_with_tol(root, self._minima):
                self._minima.append(root)
    
    def searchFirstNonZeroDerivative(piece, x0):
      pieceDx = piece
      while True:
        pieceDx = pieceDx.dx()
        value = pieceDx.evaluate(x0)
        if value != 0: return value
    
    if self.pieces[0].degree > 1:
      if searchFirstNonZeroDerivative(self.pieces[0], self.knots[0] + TOL) > 0:
        self._minima.insert(0, self.knots[0])
      else:
        self._maxima.insert(0, self.knots[0])
    
    if self.pieces[-1].degree > 1:
      if searchFirstNonZeroDerivative(self.pieces[-1], self.knots[-1] - TOL) < 0:
        self._minima.append(self.knots[-1])
      else:
        self._maxima.append(self.knots[-1])
  
  def max(self):
    if self._maxima is None: self._optimize()
    return self._maxima
  
  def min(self):
    if self._minima is None: self._optimize()
    return self._minima
  
  def normalize(self, l_inf=1):
    m = max([abs(self.evaluate(x0))
             for x0 in self.min() + self.max()])
    return self * (l_inf / m)
  
  def plot(self, **kwargs):
    fcn = self.getFunction()
    return sp.plotting.plot(fcn, xlim=(self.knots[0], self.knots[-1]), show=False, **kwargs)
  
  def generateCode(self, translate=0):
    def formatNumber(x):
      return "{:g}".format(x)
    
    code = """if ((t < {}) || (t > {})) {{
  return 0.0;
}}""".format(formatNumber(self.pieces[0].a  - translate),
             formatNumber(self.pieces[-1].b - translate))
    for piece in self.pieces:
      coeffs = piece.getTaylorCoefficients()
      if piece.b == self.pieces[-1].b:
        code += " else {\n"
      else:
        code += " else if (t < {}) {{\n".format(formatNumber(piece.b - translate))
      if len(coeffs) > 1:
        if piece.a - translate < 0.0:
          code += "  t += {};\n".format(formatNumber(translate - piece.a))
        elif piece.a - translate > 0.0:
          code += "  t -= {};\n".format(formatNumber(piece.a - translate))
        code += "  double result = {};\n".format(formatNumber(coeffs[-1]))
        for l in range(piece.degree - 1, -1, -1):
          if coeffs[l] == 0:
            code += "  result *= t;\n"
          else:
            code += "  result = {} + result * t;\n".format(formatNumber(coeffs[l]))
        code += "  return result;\n}"
      else:
        code += "  return {};\n}}".format(formatNumber(coeffs[0]))
    code += "\n"
    return code
  
  def addSplinesForInterpolation(self, splines, data):
    m = len(data)
    assert(len(splines) == m)
    A = np.zeros((m, m))
    b = np.zeros((m,))
    
    for i in range(m):
      times = data[i][2] if len(data[i]) == 3 else 0
      b[i] = data[i][1] - self.dx(times=times).evaluate(data[i][0])
      for j in range(m):
        A[i,j] = splines[j].dx(times=times).evaluate(data[i][0])
    
    c = np.linalg.solve(A, b)
    s = self
    
    for j in range(m):
      s += splines[j] * c[j]
    
    return s, c
  
  def __add__(self, other):
    sum_knots = sorted(list(set(self.knots) | set(other.knots)))
    sum_pieces = []
    
    for k in range(len(sum_knots) - 1):
      a, b = sum_knots[k], sum_knots[k + 1]
      interval_in_self  = (a in self.knots)  and (b in self.knots)
      interval_in_other = (a in other.knots) and (b in other.knots)
      if interval_in_self:  self_piece  = self.pieces[self.knots.index(a)]
      if interval_in_other: other_piece = other.pieces[other.knots.index(a)]
      
      if interval_in_self:
        if interval_in_other:
          sum_pieces.append(self_piece + other_piece)
        else:
          sum_pieces.append(self_piece)
      else:
        if interval_in_other:
          sum_pieces.append(other_piece)
        else:
          sum_pieces.append(PolynomialPiece(a, b, [0]))
    
    return Spline(sum_knots, sum_pieces)
  
  def __sub__(self, other):
    return self + other * (-1)
  
  def __mul__(self, gamma):
    return Spline(self.knots, [piece * gamma for piece in self.pieces])
  
  def __str__(self):
    s = "Spline with knots = {} and coeffs = ".format(self.knots)
    
    C = [piece.getTaylorCoefficients() for piece in self.pieces]
    s += "[{}]\n".format("; ".join([" ".join([str(y) for y in c[::-1]])
                                    for c in C]))
    return s
  
  def piecesToString(self):
    return "\n".join([str(piece) for piece in self.pieces])
  
  @property
  def knots(self): return self._knots
  @property
  def pieces(self): return self._pieces
  @property
  def isBSpline(self): return self._isBSpline



class BSpline(Spline):
  cache = {}
  
  def __init__(self, knots):
    knots = tuple(knots)
    
    if knots in BSpline.cache.keys():
      pass
    elif len(knots) == 2:
      BSpline.cache[knots] = Spline(knots, [PolynomialPiece(knots[0], knots[1], [1])])
    else:
      leftBSpline  = BSpline(knots[:-1])
      rightBSpline = BSpline(knots[1:])
      spline = ((leftBSpline * "x" - leftBSpline * knots[0]) * (1 / (knots[-2] - knots[0])) +
                (rightBSpline * knots[-1] - rightBSpline * "x") * (1 / (knots[-1] - knots[1])))
      BSpline.cache[knots] = spline
    
    super(BSpline, self).__init__(knots, BSpline.cache[knots].pieces)



class InterpolatingSpline(Spline):
  def __init__(self, knots, data):
    m = len(data)
    p = len(knots) - m - 1
    A = matrix(QQ, m, m)
    b = vector(QQ, [y for x, y in data])
    bSplines = []
    
    for j in range(m):
      bSpline = BSpline(knots[j:j+p+2])
      bSplines.append(bSpline)
      
      for i in range(m):
        if bSpline.knots[0] < data[i][0] < bSpline.knots[-1]:
          A[i,j] = bSpline.evaluate(data[i][0])
    
    c = A.solve_right(b)
    
    for j in range(m):
      weightedBSpline = bSplines[j] * c[j]
      if j == 0: spline = weightedBSpline
      else:      spline += weightedBSpline
    
    super(InterpolatingSpline, self).__init__(spline.knots[p:-p], spline.pieces[p:-p])



class PolynomialPiece(object):
  def __init__(self, a, b, coeffs):
    self._a = a
    self._b = b
    self._coeffs = coeffs
    self._degree = len(self.coeffs) - 1
    self._function = None
    self._taylorFunction = None
    self._taylorCoeffs = None
  
  def differentiate(self, times=1):
    if times == 0:
      return self
    elif times > 1:
      return self.differentiate().differentiate(times=times - 1)
    else:
      derivativeCoeffs = [(l + 1) * self.coeffs[l + 1] for l in range(self.degree)]
      return PolynomialPiece(self.a, self.b, derivativeCoeffs)
  
  def dx(self, times=1):
    return self.differentiate(times=times)
  
  def evaluate(self, xx):
    return sp.lambdify(x, self.getFunction().as_expr())(xx)
  
  def getFunction(self):
    if self._function is None:
      self._function = sp.Poly.from_list(self.coeffs[::-1], gens=x)
    
    return self._function
  
  def getTaylorFunction(self):
    if self._taylorFunction is None:
      self._taylorFunction = self.getFunction().shift(self.a)
    
    return self._taylorFunction
  
  def getTaylorCoefficients(self):
    if self._taylorCoeffs is None:
      self._taylorCoeffs = self.getTaylorFunction().all_coeffs()[::-1]
    
    return self._taylorCoeffs
  
  def plot(self, **kwargs):
    fcn = self.getFunction()
    return sp.plotting.plot(fcn.as_expr(), xlim=(self.a, self.b), show=False, **kwargs)
  
  def __add__(self, other):
    assert((self.a == other.a) and (self.b == other.b))
    sum_degree = max(self.degree, other.degree)
    sum_coeffs = (sum_degree + 1) * [0]
    
    for l in range(sum_degree + 1):
      if l <= self.degree:  sum_coeffs[l] += self.coeffs[l]
      if l <= other.degree: sum_coeffs[l] += other.coeffs[l]
    
    return PolynomialPiece(self.a, self.b, sum_coeffs)
  
  def __sub__(self, other):
    return self + other * (-1)
  
  def __mul__(self, other):
    if other == "x":
      return PolynomialPiece(self.a, self.b, [0] + self.coeffs)
    else:
      return PolynomialPiece(self.a, self.b, [coeff * other for coeff in self.coeffs])
  
  def __str__(self):
    s = "Section x in [{}, {}): c = {}\n".format(self.a, self.b, self.getTaylorCoefficients())
    s += "    (= {})".format(self.getTaylorFunction())
    return s
  
  @property
  def a(self): return self._a
  @property
  def b(self): return self._b
  @property
  def degree(self): return self._degree
  @property
  def coeffs(self): return self._coeffs



class LagrangePolynomialPiece(PolynomialPiece):
  def __init__(self, a, b, data):
    L = 0
    
    for p in data:
      if p[1] != 0:
        product = p[1]
        for q in data:
          if q[0] != p[0]: product *= (x - q[0]) / (p[0] - q[0])
        L += product
    
    coeffs = sp.Poly.from_expr(L, x).all_coeffs()[::-1]
    super(LagrangePolynomialPiece, self).__init__(a, b, coeffs)



class InterpolatingPolynomialPiece(PolynomialPiece):
  def __init__(self, data):
    m = len(data)
    A = np.zeros((m, m))
    b = np.zeros((m,))
    data.sort()
    
    # ax^4 + bx^3 + cx^2 + dx + e
    # 4ax^3 + 3bx^2 + 2cx + d
    # 12ax^2 + 6bx + 2c
    
    for i in range(m):
      times = data[i][2] if len(data[i]) == 3 else 0
      b[i] = data[i][1]
      
      for j in range(m):
        A[i,j] = ((np.product([k+1 for k in range(j-times, j)]) * data[i][0]**(j-times))
                  if j >= times else 0)
    
    coeffs = np.linalg.solve(A, b)
    a, b = data[0][0], data[-1][0]
    super(InterpolatingPolynomialPiece, self).__init__(a, b, coeffs)
