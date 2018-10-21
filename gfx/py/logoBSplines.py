#!/usr/bin/python3
# number of output figures = 1

import numpy as np
import scipy.integrate
import scipy.optimize

import helper.basis
from helper.figure import Figure



def main():
  p = 3
  innerRadius = 1
  outerRadius = 1.3
  n = 24
  nn = 101
  innerBSplineSize = [0.6, 0.6]
  
  basis = helper.basis.CardinalBSpline(p)
  
  fig = Figure.create(figsize=(3, 3))
  ax = fig.gca()
  
  tt = np.linspace(0, 2*np.pi, nn)
  xx, yy = innerRadius * np.cos(tt), innerRadius * np.sin(tt)
  ax.plot(xx, yy, "k-")
  xx, yy = outerRadius * np.cos(tt), outerRadius * np.sin(tt)
  ax.plot(xx, yy, "k-")
  
  for i in range(n):
    tt = np.linspace((i - (p+1)/2) * 2*np.pi/n,
                     (i + (p+1)/2) * 2*np.pi/n, nn)
    rr = basis.evaluate(np.linspace(0, p+1, nn))
    rr = innerRadius + (outerRadius - innerRadius) * rr
    print(rr)
    xx, yy = rr * np.cos(tt), rr * np.sin(tt)
    ax.plot(xx, yy, "k-")
  
  objFun = (lambda a: (scipy.integrate.quadrature(
        (lambda x: basis.evaluate(x) - a),
        scipy.optimize.minimize_scalar(
          lambda x: (basis.evaluate(x) - a)**2).x,
        (p+1) - scipy.optimize.minimize_scalar(
          lambda x: (basis.evaluate(x) - a)**2).x
      )[0] - 0.5)**2)
  yShift = scipy.optimize.minimize_scalar(objFun).x
  print(yShift)
  
  tt = np.linspace(0, p+1, nn)
  xx = innerBSplineSize[0] * (tt - (p+1)/2) / ((p+1)/2)
  yy = basis.evaluate(tt) - yShift
  yy = innerBSplineSize[1] * (yy / np.amax(np.abs(yy)))
  ax.plot(xx, yy, "k-")
  
  ax.set_aspect("equal")
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
