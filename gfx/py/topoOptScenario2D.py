#!/usr/bin/python3
# number of output figures = 2

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.grid
import helper.plot
import helper.topo_opt



def plotHatchedRectangle(ax, corner, size, spacing=0.1, color="k"):
  # y = x + c
  # c = y - x
  # x = y - c
  cRange = [corner[1] - (corner[0] + size[0]),
            (corner[1] + size[1]) - corner[0]]
  cs = np.arange(cRange[0] + spacing/2, cRange[1], spacing)
  
  for c in cs:
    point1 = [corner[0], corner[0] + c]
    if point1[1] < corner[1]:
      point1 = [corner[1] - c, corner[1]]
    
    point2 = [corner[0] + size[0], (corner[0] + size[0]) + c]
    if point2[1] > corner[1] + size[1]:
      point2 = [(corner[1] + size[1]) - c, corner[1] + size[1]]
    
    ax.plot(*list(zip(point1, point2)), "-", clip_on=False, color=color,
            solid_capstyle="butt", zorder=-10)



def main():
  for q in range(2):
    if q == 0:
      width, height, scale = 1.5, 0.75, 4/3
      xt, yt = [0, width], [0, height]
      forcePoint1 = [width, 0]
      h5Path = "./data/topoOpt/results/626/thesis-2d-cantilever.h5"
      nn = np.array([64, 32])
    else:
      width, height, scale = 1.5, 1.5, 10/3
      xt, yt = [0, 0.4*width, width], [0, 0.4*height, height]
      forcePoint1 = [width, 0.4 * height]
      h5Path = "./data/topoOpt/results/620/thesis-2d-L.h5"
      nn = np.array([50, 50])
    
    fig = Figure.create(figsize=(3, 3), scale=0.9)
    ax = fig.gca()
    
    hatchSize, hatchSpacing = 0.06 * width, 0.04 * width
    forceLength = 0.2 * width
    
    data = helper.topo_opt.readH5(h5Path)
    microparams = data["microparams"]["smart"]
    
    XXYY = data["nodes"][:,:2] / scale
    
    if q == 0:
      VV = np.reshape(microparams[:,0] + microparams[:,1] -
                      microparams[:,0] * microparams[:,1], nn[::-1])
    else:
      _, _, XXYY = helper.grid.generateMeshGrid(nn+1)
      XXYY = width * XXYY
      VV = (microparams[:,0] + microparams[:,1] -
            microparams[:,0] * microparams[:,1])
      vector = np.array([1] + 29 * [np.nan])
      
      for i in range(50*20+20, 50*50, 50):
        vector = (np.array([1] + 29 * [np.nan]) if i > 50*20+20 else
                  np.ones((30,)))
        VV = np.insert(VV, i, vector, axis=0)
      
      VV = np.reshape(VV, nn[::-1])
    
    XX = np.reshape(XXYY[:,0], nn[::-1]+1)
    YY = np.reshape(XXYY[:,1], nn[::-1]+1)
    
    VV = np.hstack((np.vstack((VV, VV[-1,:])),
                    np.reshape(np.append(VV[:,-1], VV[-1,-1]), (-1, 1))))
    ax.contourf(
        XX, YY, VV, [0.25, 1], colors=[helper.plot.mixColors(
            "mittelblau", 0.5, helper.plot.mixColors("mittelblau", 0.1))])
    ax.contour(XX, YY, VV, [0.25], colors="mittelblau")
    
    if q == 0:
      ax.plot(width * np.array([0, 1, 1, 0]),
              height * np.array([0, 0, 1, 1]), "k-", clip_on=False)
      ax.plot([0, 0], [0, height], "-", color="C1", clip_on=False)
      plotHatchedRectangle(ax, [-hatchSize, 0], [hatchSize, height],
                           spacing=hatchSpacing, color="C1")
      ax.text(width/2, -0.05*width, r"$\tilde{x}_1$", ha="center", va="top")
      ax.text(-0.05*width, height/2,
              r"\contour{mittelblau!10}{$\tilde{x}_2$}",
              ha="right", va="center")
    else:
      ax.plot(width * np.array([0, 0, 1, 1, 0.4, 0.4]),
              height * np.array([1, 0, 0, 0.4, 0.4, 1]), "k-",
              clip_on=False)
      ax.plot([0, 0.4*width], [height, height], "-", color="C1",
              clip_on=False)
      plotHatchedRectangle(ax, [0, height], [0.4 * width, hatchSize],
                           spacing=hatchSpacing, color="C1")
      ax.text(0.7*width, -0.05*width, r"$\tilde{x}_1$", ha="center", va="top")
      ax.text(-0.05*width, 0.7*height, r"$\tilde{x}_2$",
              ha="right", va="center")
    
    forcePoint2 = [forcePoint1[0] + 0.05 * width, forcePoint1[1]]
    ax.plot(*forcePoint1, "k.", clip_on=False)
    ax.plot(*list(zip(forcePoint1, forcePoint2)), "k-", clip_on=False)
    helper.plot.plotArrow(
        ax, forcePoint2, [forcePoint2[0], forcePoint2[1] - forceLength])
    ax.text(forcePoint2[0] + 0.025 * width, forcePoint2[1] - 0.5 * forceLength,
            r"$\force$", ha="left", va="center")
    
    ax.set_aspect("equal")
    ax.set_xlim([0, 1.1*width])
    ax.set_ylim([0, height])
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    
    ax.spines["left"].set_color("none")
    ax.spines["bottom"].set_color("none")
    
    ax.set_xticklabels([r"${:.0f}$".format(scale * x) for x in xt])
    ax.set_yticklabels([r"${:.0f}$".format(scale * y) for y in yt])
    
    if q == 0:
      ax.set_yticklabels([r"\contour{mittelblau!10}{$0$}",
                          r"\contour{mittelblau!10}{$1$}"])
    
    fig.save()



if __name__ == "__main__":
  main()
