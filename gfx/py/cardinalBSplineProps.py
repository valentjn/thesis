#!/usr/bin/python3
# number of output figures = 1

import matplotlib.patches
import numpy as np

import helper.basis
from helper.figure import Figure
import helper.plot

globalScale = [1.2, 0.75]

def plotCircle(ax, center, radius, color, zorder=-1):
  ax.add_artist(matplotlib.patches.Circle(center, radius, ec="none", fc=color, zorder=zorder))

def plotSupport(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius +
                    center[0] - 0.05,
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius +
                    center[1])
  ax.plot(*t(xx, yy), "k-")
  ax.plot(*t([0, p+1], [0, 0]), "k-")
  ax.plot(*t([0, 0], [-0.07, 0]), "k-")
  ax.plot(*t([p+1, p+1], [-0.07, 0]), "k-")
  ax.text(*t(0, -0.12), "$0$", ha="center", va="top")
  ax.text(*t(p+1, -0.12), "$p+1$", ha="center", va="top")

def plotBoundsSymmetry(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius +
                    center[0] + 0.05,
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius +
                    center[1])
  ax.plot(*t(xx, yy), "k-")
  ax.plot(*t([0, p+1], [0, 0]), "k-")
  ax.plot(*t([0, 0], [0, 1]), "k-")
  ax.plot(*t([(p+1)/2, (p+1)/2], [0, 1]), "k--")
  ax.plot(*t([-0.1, 0], [0, 0]), "k-")
  ax.plot(*t([-0.1, 0], [1, 1]), "k-")
  ax.text(*t(-0.2, 0), "$0$", ha="right", va="center")
  ax.text(*t(-0.2, 1), "$1$", ha="right", va="center")
  ax.plot(*t([(p+1)/2, (p+1)/2], [-0.07, 0]), "k-")
  ax.text(*t((p+1)/2, -0.12), r"$\tfrac{p+1}{2}$", ha="center", va="top")

def plotRecursion(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius + center[0],
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + center[1])
  bPrev = helper.basis.CardinalBSpline(p-1)
  xxPrev = np.linspace(0, p, 100)
  yyPrev = bPrev.evaluate(xxPrev)
  ax.plot(*t(xxPrev, yyPrev), "-", color="C0")
  ax.plot(*t([0, 2], [0, 1]), "--", color="C0")
  ax.plot(*t(xxPrev+1, yyPrev), "-", color="C1")
  ax.plot(*t([1, 3], [1, 0]), "--", color="C1")
  ax.plot(*t(xx, yy), "k-")

def plotSpline(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius + center[0],
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + center[1])
  ax.plot(*t(xx, yy), "k-", lw=2)
  hIn, hOut = 0.4, 0.2
  xx0 = np.linspace(-hOut, 1 + hIn, 100)
  yy0 = xx0**2 / 2
  xx1 = np.linspace(1 - hIn, 2 + hIn, 100)
  yy1 = -xx1**2 + 3*xx1 - 1.5
  xx2 = np.linspace(2 - hIn, 3 + hOut, 100)
  yy2 = (3 - xx2)**2 / 2
  ax.plot(*t(xx0, yy0), "--", color="C0")
  ax.plot(*t(xx1, yy1), "--", color="C1")
  ax.plot(*t(xx2, yy2), "--", color="C2")
  
  h = 0.035
  bPrev = helper.basis.CardinalBSpline(p-1)
  bDeriv = lambda x: bPrev.evaluate(x) - bPrev.evaluate(x - 1)
  for x0 in range(p + 2):
    y0 = b.evaluate(x0)
    d0 = np.array((1, bDeriv(x0)))
    d0[0] *= globalScale[0] / max(xx)
    d0[1] *= globalScale[1] / max(yy)
    d0 /= np.sqrt(d0[0]**2 + d0[1]**2)
    d0 = h * np.array((-d0[1], d0[0]))
    x0, y0 = t(x0, y0)
    ax.plot([x0 - d0[0], x0 + d0[0]], [y0 - d0[1], y0 + d0[1]], "k-")

def plotDerivative(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius + center[0],
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + center[1])
  gradientFactor = 0.3
  dyy = np.gradient(yy, xx[1] - xx[0]) * gradientFactor
  bPrev = helper.basis.CardinalBSpline(p-1)
  xxPrev = np.linspace(0, p, 100)
  yyPrev = bPrev.evaluate(xxPrev) * gradientFactor
  ax.plot(*t(xx, yy), "k-")
  ax.plot(*t(xxPrev, yyPrev), "-", color="C0")
  ax.plot(*t(xxPrev+1, yyPrev), "-", color="C1")
  ax.plot(*t(xx, dyy), "k--")

def plotIntegral(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius + center[0],
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + center[1])
  xxyy = np.column_stack(t(np.hstack((xx, xx[::-1])),
                           np.hstack((np.zeros_like(yy), yy[::-1]))))
  fc = helper.plot.mixColors("C0", 0.5, smallCircleColor)
  ax.add_patch(matplotlib.patches.Polygon(xxyy, ec="none", fc=fc))
  ax.plot(*t(xx, yy), "k-")
  ax.text(*t((p+1)/2, max(yy) / 2 - 0.05), "$1$", ha="center", va="center")

def plotConvolution(ax, center, radius, p):
  b = helper.basis.CardinalBSpline(p)
  xx = np.linspace(0, p+1, 100)
  yy = b.evaluate(xx)
  t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius + center[0],
                    (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + center[1])
  bPrev = helper.basis.CardinalBSpline(p-1)
  xxPrev = np.linspace(0, p, 100)
  yyPrev = bPrev.evaluate(xxPrev)
  ax.plot(*t(xxPrev, yyPrev), "-", color="C0")
  ax.plot(*t(xx, yy), "k-")
  x = 1.7
  xxRect = np.linspace(max(x - 1, 0), x, 1000)
  yyRect = bPrev.evaluate(xxRect)
  xxyyRect = np.column_stack(t(np.hstack((xxRect, xxRect[::-1])),
                               np.hstack((np.zeros_like(yyRect), yyRect[::-1]))))
  fc = helper.plot.mixColors("C0", 0.5, smallCircleColor)
  ax.add_patch(matplotlib.patches.Polygon(xxyyRect, ec="none", fc=fc))
  ax.plot(*t(x, b.evaluate(x)), "k.")
  ax.plot(*t([x-1, x], [0, 0]), "k--")
  ax.text(*t(x-0.5, -0.05), "$1$", ha="center", va="top")

def plotGeneralization(ax, center, radius, p):
  r = 3
  
  for p in [10, 3, 2, 1]:
    c = np.sqrt((p+1) / 12)
    b = helper.basis.CardinalBSpline(p)
    xx = np.linspace(max(-r, -(p+1)/(2*c)), min(r, (p+1)/(2*c)), 100)
    yy = c * b.evaluate(c * xx + (p+1)/2)
    t = lambda x, y: (np.array(x) / (2*r) * 1.0 *
                      globalScale[0] * smallCircleRadius + center[0],
                      (np.array(y) * np.sqrt(6) - 0.5) *
                      globalScale[1] * smallCircleRadius + center[1])
    ax.plot(*t(xx, yy), "-", color=("C0" if p == 1 else "k"))
  
  xx = np.linspace(-r, r, 100)
  yy = np.exp(-xx**2 / 2) / np.sqrt(2*np.pi)
  ax.plot(*t(xx, yy), "-", color="C1")

p = 2
largeCircleRadius = 1.5
smallCircleCenters = [
  (3, 3),
  (4, 2),
  (4, 1),
  (3, 0),
  (2, 0),
  (1, 1),
  (1, 2),
  (2, 3),
]
smallCircleRadius = 0.8
smallCircleColor = helper.plot.mixColors("mittelblau", 0.3)
tinyCircleRadius = 0.2
tinyCircleColor = "mittelblau"
plotFunctions = [
  plotSupport,
  plotBoundsSymmetry,
  plotRecursion,
  plotSpline,
  plotDerivative,
  plotIntegral,
  plotConvolution,
  plotGeneralization,
]

fig = Figure.create(figsize=(4, 8), scale=1.725)
ax = fig.gca()

for k in range(8):
  plotFunction = plotFunctions[k]
  t = 5 * np.pi / 8 - (2 * np.pi) * (k / 8)
  smallCircleCenter = largeCircleRadius * np.array((np.cos(t), np.sin(t)))
  tinyCircleCenter = smallCircleCenter * (1 + smallCircleRadius / largeCircleRadius)
  plotCircle(ax, smallCircleCenter, smallCircleRadius, smallCircleColor)
  plotCircle(ax, tinyCircleCenter, tinyCircleRadius, tinyCircleColor, zorder=10)
  plotFunction(ax, smallCircleCenter, smallCircleRadius, p)
  ax.text(*tinyCircleCenter, r"$\mathbf{{{}}}$".format(k+1),
          color="w", ha="center", va="center",
          size=20, zorder=11)

plotCircle(ax, (0, 0), largeCircleRadius - smallCircleRadius, "mittelblau")
b = helper.basis.CardinalBSpline(p)
xx = np.linspace(0, p+1, 100)
yy = b.evaluate(xx)
t = lambda x, y: ((np.array(x) / max(xx) - 0.5) * globalScale[0] * smallCircleRadius,
                  (np.array(y) / max(yy) - 0.5) * globalScale[1] * smallCircleRadius + 0.1)
ax.plot(*t(xx, yy), "w-")
ax.text(0, 0, r"$\cardbspl{p}$", color="w", ha="center", va="center", size=20)

ax.set_axis_off()
ax.set_xlim(-largeCircleRadius - smallCircleRadius - tinyCircleRadius,
            largeCircleRadius + smallCircleRadius + tinyCircleRadius)
ax.set_ylim(-largeCircleRadius - smallCircleRadius - tinyCircleRadius,
            largeCircleRadius + smallCircleRadius + tinyCircleRadius)
ax.set_aspect("equal")
fig.save()
