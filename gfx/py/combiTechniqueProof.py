#!/usr/bin/python3
# number of output figures = 1

import numpy as np
import matplotlib.patches

from helper.figure import Figure
import helper.grid

def plotNodalSpace(l, pos, size,
                   color="k", borderColor="k", contourColor="white"):
  xSquare = np.array([0, 1, 1, 0, 0])
  ySquare = np.array([0, 0, 1, 1, 0])
  s = lambda x, y: (pos[0] + size * np.array(x), pos[1] + size * np.array(y))
  
  ax.plot(*s(xSquare, ySquare), "-", clip_on=False, color=borderColor)
  ax.text(*s(0.5, 0),
          "\\contour{{{}}}{{$V_{{({},{})}}$}}".format(contourColor, l[0], l[1]),
          color=color, ha="center", va="bottom")
  
  X = helper.grid.getCoordinates(l, helper.grid.getNodalIndices(l))
  ax.plot(*s(X[:,0], X[:,1]), ".", clip_on=False, color=color)
  
  return s



n = 3
d = 2

subspaceSize = 1
subspaceMargin = 0.2

xl = (2, 1)
xi = (1, 1)

allL = [(i, n-i) for i in range(n+1)] + [(i, n-i-1) for i in range(n)]
L = [l for l in allL if not ((l[0] >= xl[0]) and (l[1] >= xl[1]))]

equivClasses = []

for l in L:
  added = False
  
  for equivClass in equivClasses:
    l2 = equivClass[0]
    T = [t for t in range(d) if l[t] == l2[t]]
    isEquivalent = all([min(l[t], l2[t]) >= xl[t] for t in range(d) if t not in T])
    
    if isEquivalent:
      equivClass.append(l)
      added = True
      break
  
  if not added: equivClasses.append([l])

#print(L)
#print(equivClasses)



brightness = 0.4
schemeSize = (n + 1) * (subspaceSize + subspaceMargin) - subspaceMargin
xOffsetGlobal = 0
yOffsetGlobal = schemeSize

xSquare = np.array([0, 1, 1, 0, 0])
ySquare = np.array([0, 0, 1, 1, 0])

I = helper.grid.getNodalIndices1D
x = helper.grid.getCoordinates(xl, xi)

figureScale = 1.4
fig = Figure.create(figsize=(3, 3), scale=figureScale, facecolor="none", preamble=r"""
\usepackage{contour}
\contourlength{1.5pt}
""")
ax = fig.gca()

for l in allL:
  xOffset = xOffsetGlobal + l[0] * (subspaceSize + subspaceMargin)
  yOffset = yOffsetGlobal - l[1] * (subspaceSize + subspaceMargin) - subspaceSize
  
  J = [j for j, equivClass in enumerate(equivClasses) if l in equivClass]
  
  if len(J) == 0:
    j = None
    contourColor = "white"
    color = "k"
  else:
    j = J[0]
    colorIndices = [2, 5, 7]
    contourColor = "C{}".format(colorIndices[j])
    color = [brightness * x for x in matplotlib.colors.to_rgba(contourColor)[:3]]
  
  rect = matplotlib.patches.Rectangle(
    (xOffset, yOffset), subspaceSize, subspaceSize, edgecolor="none",
    facecolor=contourColor)
  ax.add_patch(rect)
  
  borderColor = color
  
  s = plotNodalSpace(l, (xOffset, yOffset), subspaceSize,
                     color, borderColor, contourColor)
  
  ax.plot(*s(x[0], x[1]), "x", clip_on=False, color=color, markeredgewidth=2)
  
  if j is not None:
    lAst = list(l)
    
    for l2 in equivClasses[j]:
      lAst = [(None if lAst[t] is None else
               (lAst[t] if l2[t] == lAst[t] else None)) for t in range(d)]
    
    T = [t for t in range(d) if lAst[t] is not None]
    
    if T[0] == 0:
      ax.plot(*s([0, 1], [x[1], x[1]]), "-", clip_on=False, color=color)
    else:
      ax.plot(*s([x[0], x[0]], [0, 1]), "-", clip_on=False, color=color)

ax.set_xlim([0, xOffsetGlobal + schemeSize])
ax.set_ylim([0, yOffsetGlobal])
ax.set_axis_off()

fig.save()



#fig = Figure.create(figsize=(2, 2), scale=1.8, facecolor="none", preamble=r"""
#\usepackage{contour}
#\contourlength{1.5pt}
#""")
#ax = fig.gca()

#contourColor = "C5"
#color = [brightness * x for x in matplotlib.colors.to_rgba(contourColor)[:3]]

#rect = matplotlib.patches.Rectangle((0, 2.5), 2, 2, edgecolor="none", facecolor=contourColor)
#ax.add_patch(rect)

#rect = matplotlib.patches.Rectangle((0, 0), 2, 2, edgecolor="none", facecolor=contourColor)
#ax.add_patch(rect)

#borderColor = color

#s = plotNodalSpace((1, 1), (0, 2.5), 2,
                   #color, borderColor, contourColor)
#ax.plot(*s(x[0], x[1]), "x", clip_on=False, color="C1", markeredgewidth=2)
#ax.plot(*s([0, 1], [x[1], x[1]]), "-", clip_on=False, color="C1")

#s = plotNodalSpace((1, 2), (0, 0), 2,
                   #color, borderColor, contourColor)
#ax.plot(*s(x[0], x[1]), "x", clip_on=False, color="C1", markeredgewidth=2)
#ax.plot(*s([0, 1], [x[1], x[1]]), "-", clip_on=False, color="C1")

#ax.set_aspect("equal")
#ax.set_axis_off()

#fig.save()
