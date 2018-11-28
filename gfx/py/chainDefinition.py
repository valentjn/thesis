#!/usr/bin/python3
# number of output figures = 3

import matplotlib as mpl
import mpl_toolkits.mplot3d.art3d
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot



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



n, d, b = 3, 2, 1
x1Ds = [[[1, 0.5], [0, 0.5]], [[0, 0.25], [1, 0.75]]]
h = 0.125
hMargin = 0.05
l1, i1, l2, i2 = (1, 2), (1, 1), (2, 1), (3, 1)
brightness = 0.3

for q in range(2):
  fig = Figure.create(figsize=(2, 2), scale=1.3)
  ax = fig.gca()
  
  T = ([1, 0] if q == 0 else [0, 1])
  chain = getChain(l1, i1, l2, i2, T)
  rectangles = []
  
  for t, li in zip(T, chain[:-1]):
    x1D = helper.grid.getCoordinates(*li)[1-t]
    x, y, width, height = -hMargin, x1D-h*0.4, 1+2*hMargin, 0.8*h
    if t == 1: x, y, width, height = y, x, height, width
    color = helper.plot.mixColors("C{}".format(t), 1-brightness)
    rectangles.append(mpl.patches.Rectangle((x, y), width, height, color=color))
  
  for rectangle in rectangles[::-1]: ax.add_patch(rectangle)
  
  for j in range(2):
    x1 = helper.grid.getCoordinates(*chain[j])
    x2 = helper.grid.getCoordinates(*chain[j+1])
    tt = np.linspace(0.15, 0.85, 100)
    angle = (-1)**q * (30 / 180 * np.pi)
    XX = helper.plot.getQuadraticBezierCurveViaAngle(x1, x2, angle, tt)
    helper.plot.plotArrowPolygon(ax, XX[:,0], XX[:,1],
                                 ("k-" if q == 0 else "k--"), scaleHead=0.5)
  
  for j, li in enumerate(chain):
    if (q == 1) and (j == 1): continue
    x, y = helper.grid.getCoordinates(*li)
    if j == 0:   ha, va = (("center", "top") if q == 0 else ("right", "center"))
    elif j == 1: ha, va = (("right", "bottom") if q == 0 else ("left", "top"))
    else:        ha, va = (("left", "center") if q == 0 else ("center", "bottom"))
    if not ((q == 0) and (j == 1)):
      x += (-0.03 if ha == "right" else (0.03 if ha == "left" else 0))
      y += (-0.03 if va == "top" else (0.03 if va == "bottom" else 0))
    ax.text(x, y, r"$\chain{{{}}}$".format(j), ha=ha, va=va)
  
  ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k-")
  X, L, I = helper.grid.RegularSparseBoundary(n, d, b).generate()
  ax.plot(X[:,0], X[:,1], "k.")
  #if q == 1:
  #  ax.plot(*helper.grid.getCoordinates(*chain[1]), "kx", markeredgewidth=2, ms=5)
  
  helper.plot.plotArrow(ax, [0.15, 0.70], [0.27, 0.70], scaleHead=0.5)
  helper.plot.plotArrow(ax, [0.17, 0.68], [0.17, 0.80], scaleHead=0.5)
  ax.text(0.29, 0.70, r"$x_1$", ha="left", va="center")
  ax.text(0.17, 0.81, r"$x_2$", ha="center", va="bottom")
  
  ax.set_axis_off()
  
  fig.save()



fig = Figure.create(figsize=(2, 2), scale=1.7)
ax = fig.add_subplot(111, projection="3d")

l1, i1 = (2, 2, 0), (1, 3, 1)
l2, i2 = (2, 0, 2), (3, 0, 1)
T = [1, 2, 0]

x1 = helper.grid.getCoordinates(l1, i1)
x2 = helper.grid.getCoordinates(l2, i2)

xs = [[0, 1], [0, 0], [0, 0]]
ys = [[1, 1], [1, 0], [1, 1]]
zs = [[0, 0], [0, 0], [0, 1]]
for x, y, z in zip(xs, ys, zs):
  ax.plot(x, y, "k-", zs=z, color=helper.plot.mixColors("mittelblau", 0.5),
          clip_on=False, zorder=-10)

xs = [[1, 1], [0, 1], [0, 0], [0, 0], [0, 1], [1, 1], [0, 1], [1, 1], [1, 1]]
ys = [[0, 1], [0, 0], [0, 0], [0, 1], [1, 1], [0, 1], [0, 0], [0, 0], [1, 1]]
zs = [[0, 0], [0, 0], [0, 1], [1, 1], [1, 1], [1, 1], [1, 1], [0, 1], [0, 1]]
for x, y, z in zip(xs, ys, zs):
  ax.plot(x, y, "k-", zs=z, clip_on=False, zorder=10)

chain = getChain(l1, i1, l2, i2, T)
chain = helper.grid.getCoordinates(np.row_stack([l for l, i in chain]),
                                   np.row_stack([i for l, i in chain]))
width = 1.2
height = 0.2
heightDirections = [2, 0, 0]

for j, t in enumerate(T):
  vertices = []
  
  for t2 in range(3):
    if t2 == t:
      vertices.append([(1-width)/2, (1+width)/2,
                       (1+width)/2, (1-width)/2])
    else:
      newVertices = chain[j][t2] * np.ones((4,))
      if t2 == heightDirections[t]: newVertices += [-height/2, -height/2,
                                                    height/2, height/2]
      vertices.append(newVertices)
  
  vertices = list(zip(*vertices))
  faceColor = helper.plot.mixColors("C{}".format(j), 1-brightness)
  
  poly3DCollection = mpl_toolkits.mplot3d.art3d.Poly3DCollection(
      [vertices], facecolors=[faceColor])
  ax.add_collection3d(poly3DCollection)

vertices = [(0.15, 0.0, 1.0), (0.15, 0.0, 1.1),
            (0.35, 0.0, 1.1), (0.35, 0.0, 1.0)]
faceColor = helper.plot.mixColors("C1", 1-brightness)
poly3DCollection = mpl_toolkits.mplot3d.art3d.Poly3DCollection(
    [vertices], facecolors=[faceColor])
poly3DCollection.set_sort_zpos(2)
ax.add_collection3d(poly3DCollection)

for j, x in enumerate(chain):
  ax.plot([x[0]], [x[1]], ".", zs=[x[2]], color="k", clip_on=False,
          zorder=10)
  ax.text(x[0], x[1], x[2], r"\;\;$\chain{{{}}}$".format(j),
          ha="left", va="center", zorder=10)

ax.set_axis_off()

ax = fig.add_subplot(111)
X = np.array([[0.47, 0.83], [0.275, 0.68], [0.28, 0.32], [0.49, 0.25]])
angles = [-30, -20, -40]
tl = [[0.10, 0.93], [0.07, 0.95], [0.13, 0.93]]

for j in range(3):
  x1, x2, angle = X[j], X[j+1], angles[j] / 180 * np.pi
  tt = np.linspace(*tl[j], 100)
  XX = helper.plot.getQuadraticBezierCurveViaAngle(x1, x2, angle, tt)
  helper.plot.plotArrowPolygon(ax, XX[:,0], XX[:,1], "k-", scaleHead=0.5)

helper.plot.plotArrow(ax, [0.66, 0.435], [0.75, 0.405], scaleHead=0.5)
helper.plot.plotArrow(ax, [0.66, 0.42], [0.72, 0.48], scaleHead=0.5)
helper.plot.plotArrow(ax, [0.67, 0.42], [0.673, 0.53], scaleHead=0.5)
ax.text(0.765, 0.405, r"$x_1$", ha="left", va="center")
ax.text(0.73, 0.48,  r"$x_2$", ha="left", va="center")
ax.text(0.673, 0.535, r"$x_3$", ha="center", va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_axis_off()

fig.save()
