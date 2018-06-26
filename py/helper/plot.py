#!/usr/bin/python3

import matplotlib as mpl
import numpy as np
import scipy.misc

import helper.figure

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



def getBezierCurve(C, tt=201):
  n = C.shape[0] - 1
  if isinstance(tt, int): tt = np.linspace(0, 1, tt)
  TT = np.column_stack([scipy.misc.comb(n, i) * (1-tt)**(n-i) * tt**i
                        for i in range(n+1)])
  XX = np.dot(TT, C)
  return XX

def getQuadraticBezierCurveViaAngle(a, b, angle, tt, c=None):
  a, b = np.array(a), np.array(b)
  d = len(a)
  
  if d == 2:
    angle += getAngle([1, 0], b - a)
    r = np.linalg.norm(b - a, ord=2) / 2
    p = a + r * np.array([np.cos(angle), np.sin(angle)])
    C = np.array([a, p, b])
    XX = getBezierCurve(C, tt)
    return XX
  elif d == 3:
    if c is None: raise ValueError("c required for 3D Bezier curves.")
    c = np.array(c)
    scaling1 = np.linalg.norm(b - a, ord=2)
    scaling2 = np.linalg.norm(c, ord=2)
    A = np.array([(b-a)/scaling1, c/scaling2]).T  # 3x2 matrix (from 2D to 3D)
    a2D = np.zeros((2,))
    b2D = scaling1 * np.array([1, 0])
    XX2D = getQuadraticBezierCurveViaAngle(a2D, b2D, angle, tt)
    XX = a + np.dot(A, XX2D.T).T
    return XX
  else:
    raise ValueError("Unsupported dimensionality.")

def getAngle(u, v):
  u, v = np.array(u), np.array(v)
  uNorm, vNorm = np.linalg.norm(u, ord=2), np.linalg.norm(v, ord=2)
  angle = np.arccos(np.dot(u, v) / (uNorm * vNorm))
  if np.cross(u, v) < 0: angle = 2 * np.pi - angle
  return angle



def convertColorToRGB(color):
  color = helper.figure.Figure.COLORS.get(color, color)
  color = mpl.colors.to_rgba(color)[:3]
  return color

def mixColors(color1, t, color2="white"):
  color1 = convertColorToRGB(color1)
  color2 = convertColorToRGB(color2)
  mixedColor = tuple([t * c1 + (1 - t) * c2
                      for c1, c2 in zip(color1, color2)])
  return mixedColor

def createLinearColormap(name, color1, color2):
  color1 = convertColorToRGB(color1)
  color2 = convertColorToRGB(color2)
  data = {
    c : [(0, c1, c1), (1, c2, c2)]
    for c, c1, c2 in zip(["red", "green", "blue"], color1[:3], color2[:3])
  }
  colormap = mpl.colors.LinearSegmentedColormap(name, data)
  return colormap
