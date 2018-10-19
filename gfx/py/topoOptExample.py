#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np
import scipy.interpolate

from helper.figure import Figure
import helper.plot
import helper.topo_opt

def getVertices(line):
  if len(line) == 2:
    return np.column_stack((np.linspace(line[0][0], line[1][0], 200),
                            np.linspace(line[0][1], line[1][1], 200)))
  else:
    return helper.plot.getBezierCurve(np.array(line))


linesOuter = [
  [[0.00, 2.00], [0.60, 2.00]],
  [[0.60, 2.00], [0.90, 2.00], [1.50, 1.77], [2.10, 1.46]],
  [[2.10, 1.46], [2.40, 1.31], [3.00, 0.54], [3.00, 0.38]],
  [[3.00, 0.38], [3.00, 0.00]],
  [[3.00, 0.00], [0.00, 0.00]],
  [[0.00, 0.00], [0.00, 0.23]],
  [[0.00, 0.23], [0.75, 0.69], [1.50, 1.08], [1.65, 1.15]],
  [[1.65, 1.15], [1.43, 1.38], [0.38, 1.62], [0.00, 1.70]],
  [[0.00, 1.70], [0.00, 2.00]],
]

linesInner = [
  [[0.53, 0.15], [0.53, 0.23], [1.76, 1.00], [1.95, 1.00]],
  [[1.95, 1.00], [2.02, 1.00], [2.62, 0.23], [2.62, 0.15]],
  [[2.62, 0.15], [0.53, 0.15]],
]



A = helper.topo_opt.readH5("./data/topoOpt/results/560/oneload-40.h5")
np.set_printoptions(threshold=np.nan)
M1, M2 = 40, 26
displacementFactor = 0.005

displacement = np.reshape(A["displacement"], (M2+1, M1+1, 2))
displacement = np.transpose(displacement, (1, 0, 2))

fig = Figure.create(figsize=(5, 3), scale=0.6)
ax = fig.gca()

domainWidth, domainHeight = 3, 2
macroCellWidth, macroCellHeight = domainWidth / M1, domainHeight / M2

ax.add_patch(mpl.patches.Rectangle(
    (0, 0), domainWidth+0.016, domainHeight+0.016, edgecolor="none",
    facecolor=helper.plot.mixColors("mittelblau", 0.5)))

verticesOuter = np.vstack([getVertices(line) for line in linesOuter])
verticesInner = np.vstack([getVertices(line) for line in linesInner])

vertices = np.vstack((verticesOuter, verticesInner[::-1]))
codes = np.full((vertices.shape[0],), mpl.path.Path.LINETO)
codes[[0,verticesOuter.shape[0]]] = mpl.path.Path.MOVETO

path = mpl.path.Path(vertices, codes)
ax.add_patch(mpl.patches.PathPatch(
    path, edgecolor="mittelblau", facecolor="hellblau", clip_on=False))

splines = [scipy.interpolate.RectBivariateSpline(
              np.linspace(0, domainWidth,  M1+1),
              np.linspace(0, domainHeight, M2+1),
              displacement[:,:,t]) for t in range(2)]

verticesDisplaced = vertices + displacementFactor * np.array(
    [splines[t](vertices[:,0], vertices[:,1], grid=False)
     for t in range(2)]).T

pathDisplaced = mpl.path.Path(verticesDisplaced, codes)
ax.add_patch(mpl.patches.PathPatch(
    pathDisplaced, edgecolor="k", facecolor="none", ls="--", clip_on=False))

ax.plot(domainWidth, 0, "k.", clip_on=False)
helper.plot.plotArrow(ax, (domainWidth, 0), (domainWidth, -0.5))
ax.text(domainWidth + 0.06, -0.25, r"$\force$", ha="left", va="center")

hatchWidth = 0.3
hatchMargin = 0.2

ax.plot([0, 0], [-hatchMargin, domainHeight + hatchMargin], "k-",
        clip_on=False)
for y in np.linspace(-hatchMargin,
                     domainHeight + hatchMargin + hatchWidth, 20):
  xx, yy = [-hatchWidth, 0], [y - hatchWidth, y]
  if y - hatchWidth < -hatchMargin:
    xx, yy = [-y - hatchMargin, 0], [-hatchMargin, y]
  elif y > domainHeight + hatchMargin:
    xx = [-hatchWidth, domainHeight + hatchMargin - y]
    yy = [y - hatchWidth, domainHeight + hatchMargin]
  if (xx[0] > xx[1]) or (yy[0] > yy[1]): continue
  ax.plot(xx, yy, "k-", clip_on=False, solid_capstyle="butt")

ax.text(1.2, 1.6, r"$\densglobal(\tilde{\*x}) = 1$",
        ha="center", va="center", rotation=-22)
ax.text(0.65, 1.1, r"$\densglobal(\tilde{\*x}) = 0$",
        ha="center", va="center")
ax.text(domainWidth - 0.05, domainHeight - 0.05, r"$\domain$",
        ha="right", va="top")

ax.set_aspect("equal")
ax.set_xlim(-0.3, domainWidth + 0.1)
ax.set_ylim(0, domainHeight + 0.1)
ax.set_axis_off()

fig.save()
