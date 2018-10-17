#!/usr/bin/python3
# number of output figures = 3

import numpy as np

from helper.figure import Figure
import helper.plot
import helper.topo_opt



def calculatePointwiseError(
      trafoStr, basisStr, p, sampleStatsName, statsName, NN):
  sampleStats = helper.topo_opt.Stats()
  sampleStats.loadScattered("data/topoOpt/stats/{}".format(sampleStatsName))
  XX = sampleStats.X
  d = XX.shape[1]
  YYExact = helper.topo_opt.Stats.pumpElasticityTensor(sampleStats.fX)
  #normsExact = np.linalg.norm(YYExact, ord=2, axis=(1, 2))
  
  XX = XX[:NN,:]
  YYExact = YYExact[:NN,:,:]
  
  stats = helper.topo_opt.Stats()
  stats.load("./data/topoOpt/stats/{}".format(statsName))
  stats.updateInterpolant(basisStr, d, p, 1)
  
  YYIntp = stats.evaluate(XX)
  YYIntp = helper.topo_opt.Stats.transformValues(
      YYIntp, stats.transformation,
      helper.topo_opt.Stats.Transformation.normal)
  normsDifference = np.linalg.norm(
      YYExact - helper.topo_opt.Stats.pumpElasticityTensor(YYIntp),
      ord=2, axis=(1, 2))
  
  for xy in [(0, 0), (0, 1), (1, 0), (1, 1)]:
    xy2 = stats.convertGridToDomainCoords(xy)
    k = np.argmin(np.sum((XX - xy2)**2, axis=1))
    XX = np.vstack((XX, xy2))
    #normsExact = np.append(normsExact, normsExact[k])
    normsDifference = np.append(normsDifference, normsDifference[k])
  
  xx, yy = stats.convertDomainToGridCoords(XX).T
  #zz = normsDifference / normsExact
  zz = normsDifference
  X = stats.convertDomainToGridCoords(stats.X)
  
  return xx, yy, zz, X



def main():
  d = 2
  basisStr, p = "bSpline", 3
  trafoStrs = ["normal", "cholesky"]
  tol = "0.001"
  
  sampleStatsName = "cross-sisc-samples-lb0.01-ub0.99-n100000"
  NN = 5000
  
  v = np.linspace(-6-1/4, -3+1/4, 15)
  
  for trafoStr in trafoStrs:
    fig = Figure.create(figsize=(3, 3), scale=0.925)
    ax = fig.gca()
    
    trafoName = {"cholesky" : "cholesky-", "normal" : ""}[trafoStr]
    basisName = {
      "bSpline"         : "bspl",
      "notAKnotBSpline" : "nakbspl"}[basisStr]
    majorName = ("sisc" if (basisName == "bspl") and (p == 3) and
                  trafoStr == "cholesky" else "thesis")
    statsName = "cross-{}-conv-tol{}-lb0.01-ub0.99-{}hier-{}{}".format(
        majorName, tol, trafoName, basisName, p)
    
    xx, yy, zz, X = calculatePointwiseError(
        trafoStr, basisStr, p, sampleStatsName, statsName, NN)
    
    #print(np.amin(zz), np.amax(zz))
    zz = np.clip(zz, 1.01*10**v[0], 0.99*10**v[-1])
    contour = ax.tricontourf(xx, yy, np.log10(zz), v, extend="min")
    helper.plot.removeWhiteLines(contour)
    
    backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
    K = np.argsort(np.sum(X, axis=1))
    X = X[K,:]
    ax.plot(*X.T, "k.", mec=backgroundColor, mew=0.5, ms=7,
            clip_on=False, zorder=100)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel(r"$x_1$", labelpad=-8)
    ax.set_ylabel(r"$x_2$", labelpad=-4)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    
    fig.save()
  
  
  
  fig = Figure.create(figsize=(2, 3))
  ax = fig.gca()
  fig.colorbar(contour, orientation="vertical", fraction=1, aspect=10,
               ticks=np.arange(-6, -3+0.01, 1), format="$10^{%u}$")
  ax.set_axis_off()
  fig.save()



if __name__ == "__main__":
  main()
