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



def plotConvergenceTriangle(ax, x, y, width, order, side="lower",
                            ec="k", fc=None):
  isXLogScale = (ax.get_xscale() == "log")
  xFcn = ((lambda x: np.log2(x)) if isXLogScale else (lambda x: x))
  y0 = y / 2**(order*xFcn(x))
  if (order > 0) == (side == "lower"): x2 = x + width
  else:                                x2 = x - width
  y2 = y0 * 2**(order*xFcn(x2))
  
  if side not in ["lower", "upper"]:
    raise ValueError("Invalid value for \"side\".")
  
  xx, yy = [x2, x, x2, x2], [y, y, y2, y]
  XY = np.array([[x2, y], [x, y], [x2, y2]])
  
  ax.add_artist(mpl.patches.Polygon(XY, ec=ec, fc=fc,
                                    fill=(fc is not None)))
  center = ax.transData.inverted().transform(
    np.mean(ax.transData.transform(XY), axis=0))
  ax.text(*center, "${:g}$".format(abs(order)),
          ha="center", va="center", color=ec)

def plotConvergenceLine(ax, x, y, order, tx=None, ty=None, **kwargs):
  x1, x2 = ax.get_xlim()
  isXLogScale = (ax.get_xscale() == "log")
  xFcn = ((lambda x: np.log2(x)) if isXLogScale else (lambda x: x))
  y0 = y / 2**(-order*xFcn(x))
  yFcn = (lambda x: y0 * 2**(-order*xFcn(x)))
  y1, y2 = yFcn(x1), yFcn(x2)
  color = 3*[0.5]
  ax.plot([x1, x2], [y1, y2], "-", color=color, zorder=-1000)
  if tx is not None:
    kwargs = {"clip_on" : False, "color" : color, **kwargs}
    ax.text(tx, ty, "${}$".format(order), **kwargs)



def convertColorToRGB(color):
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



def addCustomLegend(ax, elements, *args, transpose=True,
                    outside=False, outsideDistance=0.05, **kwargs):
  if transpose:
    nCols = kwargs.get("ncol", 1)
    nRows = int(np.ceil(len(elements) / nCols))
    I = np.array(list(range(nRows * nCols)), dtype=int)
    I = np.reshape(np.reshape(I, (nRows, nCols)).T, (-1,))
    elements = [elements[i] for i in I if i < len(elements)]
  
  kwargs = {
    "borderaxespad" : 0,
    "borderpad"     : 0.25,
    "handletextpad" : 0.25,
    "columnspacing" : 0.5,
    "edgecolor"     : "mittelblau",
    "facecolor"     : "none",
    **kwargs,
  }
  
  if outside:
    assert "loc" in kwargs, (
        "Cannot place legend outside of axis if loc is not given.")
    assert "bbox_to_anchor" not in kwargs, (
        "Cannot place legend outside of axis if bbox_to_anchor is given.")
    loc = kwargs["loc"]
    assert isinstance(loc, (str, int)), (
        "Cannot place legend outside of axis if is a point "
        "(need location code integer or string).")
    locationStrings = ["best", "upper right", "upper left", "lower left",
                       "lower right", "right", "center left", "center right",
                       "lower center", "upper center", "center"]
    if isinstance(loc, int): loc = locationStrings[loc]
    assert loc not in ["best", "center"], (
        "Cannot place legend outside of axis if loc is best or center.")
    if loc == "right": loc = "center right"
    locY, locX = loc.split(" ")
    point = [0.5, 0.5]
    newLocY, newLocX = "center", "center"
    eps = outsideDistance
    if np.isscalar(eps): eps = [eps, eps]
    if locX == "left":    point[0], newLocX = -eps[0], "right"
    elif locX == "right": point[0], newLocX = 1+eps[0], "left"
    if locY == "lower":   point[1], newLocY = -eps[1], "upper"
    elif locY == "upper": point[1], newLocY = 1+eps[1], "lower"
    kwargs["loc"] = "{} {}".format(newLocY, newLocX)
    kwargs["bbox_to_anchor"] = point
  
  labels = [x["label"] for x in elements]
  for x in elements: del x["label"]
  handles = [mpl.lines.Line2D([0], [0], **x) for x in elements]
  ax.legend(handles, labels, *args, **kwargs)



def transform(ax, offset, scale, plot):
  if isinstance(plot, list):
    for plot2 in plot: transform(ax, offset, scale, plot2)
  else:
    transformation = mpl.transforms.Affine2D()
    if isinstance(scale, float): scale = [scale]
    transformation.scale(*scale)
    transformation.translate(*offset)
    plot.set_transform(transformation + ax.transData)



def computeZOrderValue(ax, X):
  aspectRatio = np.array([1, 1, 1])
  elev, azim = np.pi*ax.elev/180, np.pi*ax.azim/180
  xl, yl, zl = ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()
  aspectFactor = (aspectRatio /
                  np.array([np.diff(xl), np.diff(yl), np.diff(zl)]).flatten())
  center = np.array([np.mean(xl), np.mean(yl), np.mean(zl)])
  
  RAzim = np.array([[ np.cos(azim), np.sin(azim), 0],
                    [-np.sin(azim), np.cos(azim), 0], [0, 0, 1]])
  RElev = np.array([[ np.cos(elev), 0, np.sin(elev)], [0, 1, 0],
                    [-np.sin(elev), 0, np.cos(elev)]])
  R = np.dot(RElev, RAzim)
  
  XRotated = np.dot(R, (aspectFactor*(X-center)).T).T
  
  #ax.plot(XRotated[:,0], XRotated[:,1], "r.", zs=XRotated[:,2])
  #ax.view_init(azim=0, elev=0)
  
  zOrderValue = XRotated[:,0]
  zOrderValue = ((zOrderValue - np.min(zOrderValue)) /
                 (np.max(zOrderValue) - np.min(zOrderValue)))
  
  return zOrderValue
