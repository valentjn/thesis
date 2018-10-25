#!/usr/bin/python3
# number of output figures = 4

import functools
import multiprocessing

import numpy as np

from helper.figure import Figure
import helper.hpc
import helper.plot
import helper.topo_opt



@helper.hpc.cacheToFile
def calculateL2Error(trafoStr, basisStr, p, sampleStatsName, statsName):
  sampleStats = helper.topo_opt.Stats()
  sampleStats.loadScattered("data/topoOpt/stats/{}".format(sampleStatsName))
  XX = sampleStats.X
  NN, d = XX.shape
  YYExact = sampleStats.fX
  
  if sampleStatsName.startswith("cross-3d"):
    K = [98892]
  elif sampleStatsName.startswith("sheared-cross-3d"):
    K = [34931]
  else:
    K = []
  
  for k in K:
    XX = np.delete(XX, k, axis=0)
    YYExact = np.delete(YYExact, k, axis=0)
  
  normsExact = np.linalg.norm(
      helper.topo_opt.Stats.pumpElasticityTensor(YYExact),
      ord=1, axis=(1, 2))
  #normsExact = YYExact[:,5]
  denominator = np.sqrt(np.sum(normsExact**2)/NN)
  
  stats = helper.topo_opt.Stats()
  stats.load("./data/topoOpt/stats/{}".format(statsName))
  stats.updateInterpolant(basisStr, d, p, 1)
  
  #stats = helper.topo_opt.Stats()
  #stats.load("./data/topoOpt/stats/{}".format(statsName))
  #stats.updateInterpolant(basisStr, d, p, 1)
  #print(stats.N)
  
  #stats2 = helper.topo_opt.Stats()
  #stats2.load("./data/topoOpt/stats/cross-{}-conv-"
  #    "tol{}-lb0.01-ub0.99-{}hier-{}{}".format(
  #        "sisc", tol, "cholesky-", "bspl", 3))
  #stats2.updateInterpolant("bSpline", d, 3, 1)
  #fX = stats2.evaluate(stats2.X)
  #stats2.fX = np.array(fX)
  #stats2.isHierarchized = False
  #stats2.hierarchize(basisStr, d, p, 1)
  #print(np.amax(np.abs(stats.fX - stats2.fX), axis=0))
  #stats.fX = np.array(stats2.fX)
  #stats.updateInterpolant(basisStr, d, p, 1)
  
  YYIntp = stats.evaluate(XX)
  YYIntp = helper.topo_opt.Stats.transformValues(
      YYIntp, stats.transformation,
      helper.topo_opt.Stats.Transformation.normal)
  normsDifference = np.linalg.norm(
      helper.topo_opt.Stats.pumpElasticityTensor(YYExact) -
      helper.topo_opt.Stats.pumpElasticityTensor(YYIntp),
      ord=1, axis=(1, 2))
  
  #print(YYExact[0,:])
  #print(YYIntp[0,:])
  #print(np.sort(normsDifference))
  #print(np.argsort(normsDifference))
  
  N = stats.N
  error = np.sqrt(np.sum(normsDifference**2)/NN) / denominator
  
  return N, error
  
  #if tol == tols[-1]:
  #  import matplotlib.pyplot as plt
  #  from mpl_toolkits.mplot3d import Axes3D
  #  fig = plt.figure()
  #  ax = fig.gca(projection="3d")
  #  ax.scatter(XX[:1000,0], XX[:1000,1], normsDifference[:1000], c="b")
  #  ax.scatter(stats.X[:,0], stats.X[:,1], fX[:,5], c="r")
  #  plt.show()



def main():
  d = 2
  basisTypes = [
    ("bSpline", 1),
    ("bSpline", 3),
    #("notAKnotBSpline", 3),
    ("bSpline", 5),
    #("notAKnotBSpline", 5),
  ]
  trafoStrs = ["cholesky", "normal"]
  
  #basisTypes = [("notAKnotBSpline", 5)]
  #trafos = ["cholesky"]
  
  #tols = ["0.464159", "0.215443", "0.1", "0.0464159", "0.0215443", "0.01",
  #        "0.00464159", "0.00215443", "0.001", "0.000464159", "0.000215443",
  #        "0.0001", "4.64159e-05", "2.15443e-05", "1e-05", "4.64159e-06",
  #        "2.15443e-06", "1e-06", "4.64159e-07", "2.15443e-07", "1e-07"]
  tols = ["0.215443", "0.1", "0.0464159", "0.0215443", "0.01", "0.00464159",
          "0.00215443", "0.001", "0.000464159", "0.000215443", "0.0001",
          "4.64159e-05", "2.15443e-05"]
  #tols = ["0.215443", "0.1", "0.0464159", "0.0215443", "0.01", "0.00464159"]
  
  sampleStatsName = "cross-sisc-samples-lb0.01-ub0.99-n100000"
  
  fig = Figure.create(figsize=(3, 2.3))
  ax = fig.gca()
  
  for trafoStr in trafoStrs:
    for basisStr, p in basisTypes:
      statsNames = []
      
      for tol in tols:
        trafoName = {"cholesky" : "cholesky-", "normal" : ""}[trafoStr]
        basisName = {
          "bSpline"         : "bspl",
          "notAKnotBSpline" : "nakbspl"}[basisStr]
        majorName = ("sisc" if (basisName == "bspl") and (p == 3) and
                      trafoStr == "cholesky" else "thesis")
        statsName = "cross-{}-conv-tol{}-lb0.01-ub0.99-{}hier-{}{}".format(
            majorName, tol, trafoName, basisName, p)
        statsNames.append(statsName)
      
      with multiprocessing.Pool() as pool:
        results = pool.map(functools.partial(
            calculateL2Error, trafoStr, basisStr, p, sampleStatsName),
            statsNames)
      
      x, y = list(zip(*results))
      lineStyle = {1 : ".-", 3 : "^--", 5 : "v:"}[p]
      markerSize = (6 if p == 1 else 3)
      color = {"normal" : "C0", "cholesky" : "C1"}[trafoStr]
      print(y)
      ax.plot(x, y, lineStyle, color=color, ms=markerSize)
  
  ax.set_xscale("log")
  ax.set_yscale("log")
  ax.set_ylim(1e-5, 3e-2)
  ax.set_ylabel(r"Relative $\Ltwo$ spectral error")
  
  trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
  ax.text(*trafo(0.76, -0.05), r"$\ngp$", ha="center", va="top")
  
  fig.save()
  
  
  
  models = ["framed-cross", "sheared-cross", "sheared-framed-cross",
            "cross-3d", "sheared-cross-3d"]
  basisStr, p = "bSpline", 3
  trafoStr = "cholesky"
  
  fig = Figure.create(figsize=(3, 2.3))
  ax = fig.gca()
  
  for model in models:
    if model == "framed-cross":
      tols = ["5.01187", "3.98107", "3.16228", "2.51189", "1.99526",
              "1.58489", "1.25893", "1", "0.794328", "0.630957", "0.501187"]
      majorName = "sga16"
      boundsName = "lb0.01-ub0.99"
      sampleStatsName = "framed-cross-thesis-samples-lb0.01-ub0.99-n100000"
    elif model == "sheared-cross":
      tols = ["0.316228", "0.215443", "0.14678", "0.1", "0.0681292",
              "0.0464159", "0.0316228", "0.0215443", "0.014678", "0.01",
              "0.00681292", "0.00464159"]
      majorName = "sisc"
      boundsName = "lb0.01,0.15-ub0.99,0.85"
      sampleStatsName = ("sheared-cross-sisc-samples-"
                         "lb0.01,0.15-ub0.99,0.85-n100000")
    elif model == "sheared-framed-cross":
      tols = ["31.6228", "25.1189", "19.9526", "15.8489", "12.5893", "10",
              "7.94328", "6.30957", "5.01187", "3.98107", "3.16228"]
      majorName = "sga16"
      boundsName = "lb0.01,0.15-ub0.99,0.85"
      sampleStatsName = ("sheared-framed-cross-thesis-samples-"
                         "lb0.01,0.15-ub0.99,0.85-n100000")
    elif model == "cross-3d":
      tols = ["1", "0.794328", "0.630957", "0.501187", "0.398107", "0.316228",
              "0.251189", "0.199526", "0.158489", "0.125893", "0.1",
              "0.0794328"]
      majorName = "sga16"
      boundsName = "lb0.01-ub0.99"
      sampleStatsName = "cross-3d-thesis-samples-lb0.01-ub0.99-n100000"
    elif model == "sheared-cross-3d":
      tols = ["50.1187", "39.8107", "31.6228", "25.1189", "19.9526",
              "15.8489", "12.5893", "10", "7.94328", "6.30957", "5.01187"]
      majorName = "sga16"
      boundsName = "lb0.01,0.15-ub0.99,0.85"
      sampleStatsName = ("sheared-cross-3d-thesis-samples-"
                         "lb0.01,0.15-ub0.99,0.85-n100000")
    
    statsNames = []
    
    for tol in tols:
      trafoName = {"cholesky" : "cholesky-", "normal" : ""}[trafoStr]
      basisName = {
        "bSpline"         : "bspl",
        "notAKnotBSpline" : "nakbspl"}[basisStr]
      statsName = "{}-{}-conv-tol{}-{}-{}hier-{}{}".format(
          model, majorName, tol, boundsName, trafoName, basisName, p)
      statsNames.append(statsName)
    
    #if model != "sheared-cross-3d": continue
    #statsNames = [statsNames[0]]
    
    with multiprocessing.Pool() as pool:
      results = pool.map(functools.partial(
          calculateL2Error, trafoStr, basisStr, p, sampleStatsName),
          statsNames)
    
    x, y = list(zip(*results))
    lineStyle = {1 : ".-", 3 : "^--", 5 : "v:"}[p]
    markerSize = (6 if p == 1 else 3)
    color = {"framed-cross"         : "C2",
             "sheared-cross"        : "C3",
             "sheared-framed-cross" : "C4",
             "cross-3d"             : "C5",
             "sheared-cross-3d"     : "C6"}[model]
    print(y)
    ax.plot(x, y, lineStyle, color=color, ms=markerSize)
  
  ax.set_xscale("log")
  ax.set_yscale("log")
  ax.set_ylim(1e-3, 1e-1)
  ax.set_ylabel(r"Relative $\Ltwo$ spectral error")
  
  trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
  ax.text(*trafo(1, -0.05), r"$\ngp$", ha="right", va="top")
  
  fig.save()
  
  
  
  fig = Figure.create(figsize=(5, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax, [
      {
        "label" : r"\rlap{2D-C ($\delta^{\sparse}$)}",
        "ls"    : "-",
        "color" : "C0",
      },
      None,
      {
        "label" : r"\rlap{2D-C ($\delta^{\chol,\sparse}$)}",
        "ls"    : "-",
        "color" : "C1",
      },
      None,
      {
        "label"  : r"$p = 1$\hspace*{2mm}",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "k",
        "ms"     : 6,
      },
      {
        "label"  : r"\rlap{$p = 3$}",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "k",
        "ms"     : 3,
      },
      None,
      {
        "label"  : r"$p = 5$\hspace*{2mm}",
        "ls"     : ":",
        "marker" : "v",
        "color"  : "k",
        "ms"     : 3,
      },
    ], ncol=4, loc="upper center", outside=True, columnspacing=0.5)
  
  ax.set_axis_off()
  
  fig.save()
  
  
  
  fig = Figure.create(figsize=(5, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax, [
      {
        "label"  : "2D-FC",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C2",
        "ms"     : 3,
      },
      {
        "label"  : "2D-SC",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C3",
        "ms"     : 3,
      },
      {
        "label"  : "2D-SFC",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C4",
        "ms"     : 3,
      },
      {
        "label"  : "3D-C",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C5",
        "ms"     : 3,
      },
      {
        "label"  : "3D-SC",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C6",
        "ms"     : 3,
      },
    ], ncol=3, loc="upper center", outside=True, columnspacing=1)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
