#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np
import scipy.interpolate

from helper.figure import Figure
import helper.plot
import helper.topo_opt



h5Data = helper.topo_opt.readH5(
    "./data/topoOpt/results/650/thesis-2d-cantilever.h5")
np.set_printoptions(threshold=np.nan)
M1, M2 = 64, 32
displacementFactor = 0.003

displacement = np.reshape(h5Data["displacement"], (M2+1, M1+1, 2))
displacement = np.transpose(displacement, (1, 0, 2))

fig = Figure.create(figsize=(5, 3), scale=0.7)
ax = fig.gca()

domainWidth, domainHeight = 2, 1
macroCellWidth, macroCellHeight = domainWidth / M1, domainHeight / M2

ax.add_patch(mpl.patches.Rectangle(
    (0, 0), domainWidth+0.016, domainHeight+0.016, edgecolor="none",
    facecolor=helper.plot.mixColors("mittelblau", 0.5),
    zorder=-10))

microparams = h5Data["microparams"]["smart"]
nn = np.array((M1, M2))
VV = np.reshape(microparams[:,0] + microparams[:,1] -
                microparams[:,0] * microparams[:,1], nn[::-1])
XXYY = h5Data["nodes"][:,:2]
VV = np.hstack((np.vstack((VV, VV[-1,:])),
                np.reshape(np.append(VV[:,-1], VV[-1,-1]), (-1, 1))))
VV[0,:]  = 0
VV[-1,:] = 0
VV[:,0]  = 0
VV[:,-1] = 0
VV = VV.flatten()
triangulation = mpl.tri.Triangulation(XXYY[:,0], XXYY[:,1])
ax.tricontourf(triangulation, VV, [0.25, 1], colors="hellblau")
ax.tricontour(triangulation, VV, [0.25], colors="mittelblau")

splines = [scipy.interpolate.RectBivariateSpline(
              np.linspace(0, domainWidth,  M1+1),
              np.linspace(0, domainHeight, M2+1),
              displacement[:,:,t]) for t in range(2)]
XXYYDisplaced = XXYY + displacementFactor * np.array(
    [splines[t](XXYY[:,0], XXYY[:,1], grid=False) for t in range(2)]).T
triangulationDisplaced = mpl.tri.Triangulation(
    XXYYDisplaced[:,0], XXYYDisplaced[:,1])
ax.tricontour(triangulationDisplaced, VV, [0.25],
              colors=["k"], linestyles=["dashed"])

ax.plot(domainWidth, 0, "k.", clip_on=False)
helper.plot.plotArrow(ax, (domainWidth, 0), (domainWidth, -0.3))
ax.text(domainWidth + 0.06, -0.15, r"$\force$", ha="left", va="center")

ax.plot([0, 0], [0, domainHeight], "k-", clip_on=False)
helper.plot.plotHatchedRectangle(
    ax, [-0.2, 0], [0.2, domainHeight], spacing=0.08, color="k")

ax.text(0.6, 0.25, r"$\densglobal(\tilde{\*x}) = 1$",
        ha="center", va="center", rotation=20)
ax.text(0.03, 0.45, r"$\densglobal(\tilde{\*x}) = 0$",
        ha="left", va="center")
ax.text(domainWidth - 0.05, domainHeight - 0.05, r"$\objdomain$",
        ha="right", va="top")

ax.set_aspect("equal")
ax.set_xlim(-0.3, domainWidth)
ax.set_ylim(-0.35, domainHeight)
ax.set_axis_off()

fig.save()
