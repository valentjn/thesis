#!/usr/bin/python3

import numpy as np
import scipy.misc

DEFAULT_ARROW_PROPERTIES = {
  "head_width" : 0.04,
  "head_length" : 0.04,
  "overhang" : 0.3,
  "length_includes_head" : True,
  "clip_on" : False,
  "lw" : 0.9,
  "fc" : "k",
}



def plotArrow(ax, start, end, scaleHead=1, **kwargs):
  for name, value in DEFAULT_ARROW_PROPERTIES.items():
    kwargs.setdefault(name, value)
  
  kwargs["head_width"] *= scaleHead
  kwargs["head_length"] *= scaleHead
  start, end = np.array(start), np.array(end)
  d = len(start)
  
  if d == 2:
    ax.arrow(*start, *(end - start), **kwargs)
  else:
    raise ValueError("Unsupported dimensionality.")

def plotArrowPolygon(ax, xx, yy, lineStyle, scaleHead=1,
                     virtualHeadLength=0.01, cutOff=6, **kwargs):
  virtualHeadStart = np.array([xx[-2], yy[-2]])
  virtualHeadEnd = np.array([xx[-1], yy[-1]])
  virtualHeadDirection = virtualHeadEnd - virtualHeadStart
  virtualHeadDirection /= np.linalg.norm(virtualHeadDirection, ord=2)
  virtualHeadStart = virtualHeadEnd - virtualHeadLength * virtualHeadDirection
  
  xx, yy = list(xx[:-cutOff]), list(yy[:-cutOff])
  xx += [virtualHeadStart[0]]
  yy += [virtualHeadStart[1]]
  xx, yy = np.array(xx), np.array(yy)
  plotFunction = ((lambda ax, xx, yy: ax.plot(xx, yy, lineStyle))
                  if type(lineStyle) is str else lineStyle)
  plotFunction(ax, xx, yy)
  plotArrow(ax, virtualHeadStart, virtualHeadEnd, scaleHead=scaleHead, **kwargs)

def getBezierCurve(C, tt):
  n = C.shape[0] - 1
  TT = np.column_stack([scipy.misc.comb(n, i) * (1-tt)**(n-i) * tt**i
                        for i in range(n+1)])
  XX = np.dot(TT, C)
  return XX

def getQuadraticBezierCurveViaAngle(a, b, angle, tt):
  a, b = np.array(a), np.array(b)
  angle += getAngle([1, 0], b - a)
  r = np.linalg.norm(b - a, ord=2) / 2
  p = a + r * np.array([np.cos(angle), np.sin(angle)])
  C = np.array([a, p, b])
  XX = getBezierCurve(C, tt)
  return XX

def getAngle(u, v):
  u, v = np.array(u), np.array(v)
  uNorm, vNorm = np.linalg.norm(u, ord=2), np.linalg.norm(v, ord=2)
  angle = np.arccos(np.dot(u, v) / (uNorm * vNorm))
  if np.cross(u, v) < 0: angle += np.pi
  return angle
