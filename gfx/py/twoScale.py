#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.plot
import helper.topo_opt



def plotZoomBox(ax, s1, s2):
  xCorners, yCorners = [0, 0, 1, 1], [0, 1, 0, 1]
  corners1 = s1(xCorners, yCorners)
  corners2 = s2(xCorners, yCorners)
  
  darkColor = "mittelblau"
  backgroundColor = helper.plot.mixColors(darkColor, 0.1)
  brightness = 0.8
  lightColor = helper.plot.mixColors(backgroundColor, 0.8, "k")
  
  for q in range(4):
    if q < 2:
      ax.plot([corners1[0][q], corners2[0][q]],
              [corners1[1][q], corners2[1][q]], "-",
              clip_on=False, color=darkColor, zorder=20)
    else:
      x = corners2[0][0]
      r = (x - corners1[0][q]) / (corners2[0][q] - corners1[0][q])
      y = corners1[1][q] + r * (corners2[1][q] - corners1[1][q])
      ax.plot([corners1[0][q], x], [corners1[1][q], y], "-",
              clip_on=False, color=darkColor, zorder=20)
      ax.plot([x, corners2[0][q]], [y, corners2[1][q]], "-",
              clip_on=False, color=lightColor)
  
  xSquare, ySquare = [0, 1, 1, 0, 0], [0, 0, 1, 1, 0]
  ax.plot(*s2(xSquare, ySquare), "-",
          clip_on=False, color=darkColor, zorder=20)

def plotCross(ax, s, param):
  for q in range(2):
    corners = (s([0, 1], [(1-param[0])/2, (1+param[0])/2]) if q == 0 else
              s([(1-param[1])/2, (1+param[1])/2], [0, 1]))
    x, y = corners[0][0], corners[1][0]
    width = corners[0][1] - corners[0][0]
    height = corners[1][1] - corners[1][0]
    ax.add_patch(mpl.patches.Rectangle((x, y), width, height,
      edgecolor="none", facecolor="k", zorder=10))

def plotMeasureLines(
      ax, s, center, direction, totalLength, gapLength, whiskerLength):
  center = np.array(center)
  direction = np.array(direction) / np.linalg.norm(direction)
  leftStart  = s(*(center - totalLength/2 * direction))
  leftEnd    = s(*(center - gapLength/2 * direction))
  rightStart = s(*(center + gapLength/2 * direction))
  rightEnd   = s(*(center + totalLength/2 * direction))
  
  realDirection = np.array(rightEnd) - np.array(leftStart)
  realDirection /= np.linalg.norm(realDirection)
  realNormal = np.array([-realDirection[1], realDirection[0]])
  leftWhiskerStart  = leftStart - whiskerLength/2 * realNormal
  leftWhiskerEnd    = leftStart + whiskerLength/2 * realNormal
  rightWhiskerStart = rightEnd  - whiskerLength/2 * realNormal
  rightWhiskerEnd   = rightEnd  + whiskerLength/2 * realNormal
  
  kwargs = {
    "clip_on" : False,
    "solid_capstyle" : "butt",
  }
  ax.plot(*list(zip(leftStart,  leftEnd)),  "k-", **kwargs)
  ax.plot(*list(zip(rightStart, rightEnd)), "k-", **kwargs)
  ax.plot(*list(zip(leftWhiskerStart,  leftWhiskerEnd)),  "k-", **kwargs)
  ax.plot(*list(zip(rightWhiskerStart, rightWhiskerEnd)), "k-", **kwargs)



A = helper.topo_opt.readDensityFile(
    "./data/topoOpt/results/650/thesis-2d-cantilever.density.xml")
M1, M2 = A.shape[:2]

newM1, newM2 = 16, 8
newA = np.full((newM1, newM2, 2), np.nan)

for newJ1 in range(newM1):
  if newJ1 == newM1 - 1:
    r1, j1 = 1, M1 - 2
  else:
    j1 = (newJ1 / (newM1 - 1)) * (M1 - 1)
    r1, j1 = j1 - int(j1), int(j1)
  
  for newJ2 in range(newM2):
    if newJ2 == newM2 - 1:
      r2, j2 = 1, M2 - 2
    else:
      j2 = (newJ2 / (newM2 - 1)) * (M2 - 1)
      r2, j2 = j2 - int(j2), int(j2)
    
    newA[newJ1,newJ2,:] = (
      (1-r1)*(1-r2)*A[j1,  j2,  0,:,1] +
      (1-r1)*r2    *A[j1,  j2+1,0,:,1] +
      r1    *(1-r2)*A[j1+1,j2,  0,:,1] +
      r1    *r2    *A[j1+1,j2+1,0,:,1])

A = newA
M1, M2 = newM1, newM2
V = ((A[:,:,0] - 0.01) / 0.98 +
     (A[:,:,1] - 0.01) / 0.98 -
     ((A[:,:,0] - 0.01) / 0.98) * ((A[:,:,1] - 0.01) / 0.98))



fig = Figure.create(figsize=(5, 3), scale=1.2)
ax = fig.gca()

domainWidth, domainHeight = 4, 2
jp1, jp2 = 11, 4
macroCellMargin = 0.5
macroCellSize = 1.5
macroCellInnerMargin = 0.1
macroCellN = 11
kp1, kp2 = 7, 5
microCellMargin = 0.5
microCellSize = 1.5
edgeColor = "mittelblau"
backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
textMargin = 0.05

xSquare, ySquare = [0, 1, 1, 0, 0], [0, 0, 1, 1, 0]
macroCellWidth, macroCellHeight = domainWidth / M1, domainHeight / M2

for j1 in range(M1):
  x = j1 * macroCellWidth
  for j2 in range(M2):
    y = j2 * macroCellHeight
    color = helper.plot.mixColors("k", V[j1,j2], backgroundColor)
    ax.add_patch(mpl.patches.Rectangle(
      (x, y), macroCellWidth, macroCellHeight,
      edgecolor="none", facecolor=color))

for j1 in range(M1+1):
  x = j1 * macroCellWidth
  ax.plot([x, x], [0, domainHeight], "-", color=edgeColor, clip_on=False)

for j2 in range(M2+1):
  y = j2 * macroCellHeight
  ax.plot([0, domainWidth], [y, y], "-", color=edgeColor, clip_on=False)

ax.text(M1/2 * macroCellWidth, domainHeight + textMargin,
        r"\textbf{Domain} $\objdomain$", ha="center", va="bottom")
ax.text(M1/2 * macroCellWidth, -textMargin,
        r"$M_1$ macro-cells", ha="center", va="top")
ax.text(-textMargin, M2/2 * macroCellHeight,
        r"$M_2$ macro-cells", ha="right", va="center", rotation=90)

s1 = (lambda xx, yy :
    ((jp1 + np.array(xx)) * macroCellWidth,
     (jp2 + np.array(yy)) * macroCellHeight))
s2 = (lambda xx, yy :
    (domainWidth + macroCellMargin + np.array(xx) * macroCellSize,
    (domainHeight - macroCellSize) / 2 + np.array(yy) * macroCellSize))
plotZoomBox(ax, s1, s2)
ax.text(*s2(0.5, macroCellInnerMargin/2), r"$\dots$",
        ha="center", va="center")
ax.text(*s2(0.5, 1-macroCellInnerMargin/2), r"$\dots$",
        ha="center", va="center")
ax.text(*s2(macroCellInnerMargin/2, 0.55), r"$\vdots$",
        ha="center", va="center")
ax.text(*s2(1-macroCellInnerMargin/2, 0.55), r"$\vdots$",
        ha="center", va="center")

ax.text(*(s2(0.5, 1) + np.array([0, textMargin])),
        r"\textbf{Macro-cell}", ha="center", va="bottom")

s3 = (lambda xx, yy : s2(0.8 * np.array(xx) + macroCellInnerMargin,
                         0.8 * np.array(yy) + macroCellInnerMargin))
param = A[jp1,jp2,:]

for j1 in range(macroCellN):
  x = j1 / macroCellN
  
  for j2 in range(macroCellN):
    y = j2 / macroCellN
    s4 = (lambda xx, yy : s3(x + np.array(xx) / macroCellN,
                             y + np.array(yy) / macroCellN))
    plotCross(ax, s4, param)

x = kp1 / macroCellN
y = kp2 / macroCellN
s4 = (lambda xx, yy : s3(x + np.array(xx) / macroCellN,
                         y + np.array(yy) / macroCellN))
ax.plot(*s4(xSquare, ySquare), "-", color=edgeColor)

s5 = (lambda xx, yy :
    (domainWidth + macroCellMargin + macroCellSize + microCellMargin +
     np.array(xx) * microCellSize,
    (domainHeight - microCellSize) / 2 + np.array(yy) * microCellSize))
plotZoomBox(ax, s4, s5)
plotCross(ax, s5, param)

ax.text(*(s5(0.5, 1) + np.array([0, textMargin])),
        r"\textbf{Micro-cell}", ha="center", va="bottom")
ax.text(*(s5(0.5, 0) + np.array([0, -textMargin])),
        r"$x_2$", ha="center", va="top")
ax.text(*(s5(1, 0.5) + np.array([textMargin, 0])),
        r"$x_1$", ha="left", va="center", rotation=270)
plotMeasureLines(ax, s5, [0.5,  -0.07], [1, 0], param[1], 0.20, 0.1)
plotMeasureLines(ax, s5, [1.10, 0.5],   [0, 1], param[0], 0.20, 0.1)

ax.set_aspect("equal")
ax.set_xlim(0, domainWidth + macroCellMargin + macroCellSize +
               microCellMargin + microCellSize)
ax.set_ylim(0, domainHeight)
ax.set_axis_off()

fig.save()
