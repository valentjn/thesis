#!/usr/bin/python3

from .non_uniform_bspline import NonUniformBSpline

class CentralizedCardinalBSpline(NonUniformBSpline):
  def __init__(self, p, nu=0):
    super().__init__(p, list(range(-(p+1)//2, (p+1)//2 + 1)), nu=nu)
