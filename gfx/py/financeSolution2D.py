#!/usr/bin/python3
# number of output figures = 12

import functools
#import multiprocessing

import matplotlib as mpl
import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



def plotJOrPolicy(solution, interpPolicy, discreteStateName, t, isSparseGrid,
                  parameters):
  q, name, interpolant = parameters
  
  fig = Figure.create(figsize=(3, 3), scale=(0.73 if isSparseGrid else 0.77))
  
  if isSparseGrid: ax = fig.gca()
  else:            ax = fig.add_subplot(111, projection="3d")
  
  if name == "J":
    zl = (0.0775, 0.0783)
    zt = [0.0776, 0.0782]
    zLabel = r"$\normcetvaluefcn_t$"
  elif name.endswith("Buy"):
    zl = (0, 0.18)
    zt = [0, 0.15]
    zLabel = r"$\normbuy[\opt]_{{t,{}}}$".format(name[-4])
  elif name.endswith("Sell"):
    zl = (0, 0.75)
    zt = [0, 0.6]
    zLabel = r"$\normsell[\opt]_{{t,{}}}$".format(name[-5])
  else:
    zl = (0.35, 0.55)
    zt = [0, 0.4]
    zLabel = r"$\normbond_t^{\opt}$"
  
  nn = (65, 65)
  xBreak = 0.25
  
  if name in ["DeltaNormNormS1Buy", "normNormB"]:
    xx0 = np.linspace(0, xBreak, (nn[0]+1)//2)
    xx0 = np.append(xx0, np.linspace(xBreak, 1, (nn[0]+1)//2)[1:])
  else:
    xx0 = np.linspace(0, 1, nn[0])
  
  if name in ["DeltaNormNormS2Buy", "normNormB"]:
    xx1 = np.linspace(0, xBreak, (nn[0]+1)//2)
    xx1 = np.append(xx1, np.linspace(xBreak, 1, (nn[1]+1)//2)[1:])
  else:
    xx1 = np.linspace(0, 1, nn[1])
  
  XX0, XX1 = np.meshgrid(xx0, xx1)
  XX = np.column_stack([XX0.flatten(), XX1.flatten()])
  XX = (interpolant.bounds[0] +
        (interpolant.bounds[1] - interpolant.bounds[0]) * XX)
  XX0 = np.reshape(XX[:,0], nn)
  XX1 = np.reshape(XX[:,1], nn)
  YY = np.reshape(interpolant.evaluate(XX), nn)
  
  if isSparseGrid:
    v = 20
    contour = ax.contourf(XX0, XX1, YY, v, vmin=zl[0], vmax=zl[1])
    helper.plot.removeWhiteLines(contour)
    
    backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
    X = interpolant.X
    K = np.argsort(np.sum(X, axis=1))
    X = X[K,:]
    ax.plot(*X.T, "k.", clip_on=False,
            mec=backgroundColor, mew=0.5, ms=7)
  else:
    light = mpl.colors.LightSource(315, 45)
    faceColors = light.shade(YY, cmap=mpl.cm.viridis, vmin=zl[0], vmax=zl[1],
                            blend_mode="soft")
    surf = ax.plot_surface(XX0, XX1, YY, facecolors=faceColors)
  
  ax.set_xlim(0, 1)
  ax.set_ylim(0, 1)
  
  if isSparseGrid:
    xt = [0, 0.25, 0.5, 0.75, 1]
    xtl = ["$0$", "", "$0.5$", "", "$1$"]
    yt, ytl = xt, xtl
    ax.set_xticks(xt)
    ax.set_xticklabels(xtl)
    ax.set_yticks(yt)
    ax.set_yticklabels(ytl)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo( 0.85, -0.07), r"$\stock_{t,1}$", ha="center", va="top")
    ax.text(*trafo(-0.05,  0.82), r"$\stock_{t,2}$", ha="right",  va="center")
  else:
    ax.view_init(60, -120)
    
    ax.set_zlim(*zl)
    
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    
    ax.text(0,   -0.1, zl[0], r"$0$", ha="center", va="top")
    ax.text(1,   -0.1, zl[0], r"$1$", ha="center", va="top")
    ax.text(-0.1, 0,   zl[0], r"$0$", ha="right",  va="center")
    ax.text(-0.1, 0.9, zl[0], r"$1$", ha="right",  va="center")
    
    if name == "J":
      for z in zt:
        ax.text(-0.03, 1, z + 0.07 * (zl[1] - zl[0]), r"${}$".format(z),
                ha="right", va="top", zdir=(1, 0, 0.001))
    else:
      for z, va in zip(zt, ["bottom", "center"]):
        ax.text(-0.1, 1, z, r"${}$".format(z), ha="right", va=va)
    
    ax.text(0.5,  -0.23, zl[0], r"$\stock_{t,1}$", ha="center", va="top")
    ax.text(-0.15, 0.45,  zl[0], r"$\stock_{t,2}$", ha="right", va="center")
    ax.text(-0.1, 1, zl[1] + 0.2 * (zl[1] - zl[0]), zLabel,
            ha="center", va="bottom")
  
  fig.save(graphicsNumber=q+1)



def main():
  ids = [14, 116]
  isSparseGrids = [False, True]
  
  q0 = 0
  
  for isSparseGrid, id_ in zip(isSparseGrids, ids):
    d = 2
    discreteStateName = "Alive"
    policyNames = (["DeltaNormNormS{}Buy".format(t+1)  for t in range(d)] +
                   ["DeltaNormNormS{}Sell".format(t+1) for t in range(d)] +
                   ["normNormB"])
    names = ["J"] + policyNames
    t = 0
    qs = list(range(q0, q0 + len(names)))
    q0 += len(names)
    
    policiesMat = scipy.io.loadmat(
        "data/finance/results/{:04}/policies_serialized.mat".format(id_))
    solution     = policiesMat["solution"]
    interpPolicy = policiesMat["interpPolicy"]
    
    interpolants = [(
        helper.finance.createJInterpolant(
          solution, t, discreteStateName, name="interpJ") if name == "J" else
        helper.finance.createPolicyInterpolant(
          interpPolicy, t, discreteStateName, name)) for name in names]
    parameterss = list(zip(qs, names, interpolants))
    
    #with multiprocessing.Pool() as pool:
    #  pool.map(functools.partial(plotJOrPolicy,
    #        solution, interpPolicy, discreteStateName, t, isSparseGrid),
    #      parameterss)
    
    for parameters in parameterss:
      plotJOrPolicy(solution, interpPolicy, discreteStateName, t,
                    isSparseGrid, parameters)



if __name__ == "__main__":
  main()
