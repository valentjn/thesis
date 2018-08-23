#!/usr/bin/python3
# number of output figures = 1
# dependencies = cpp/optimizeFuzzy

import multiprocessing

from helper.figure import Figure
import helper.plot

import helperFuzzy



def processValue(n):
  fStr = "alpine02"
  d = 2
  gridType = "modifiedNotAKnotBSpline"
  gridGenerationType = "regular"
  N = 1000
  p = 3
  gamma = 0.9
  m = 100
  inputIndex = 0
  seed = 1
  
  results = helperFuzzy.optimizeFuzzy(
      fStr, d, gridType, gridGenerationType,
      N, p, gamma, n, m, inputIndex, seed)
  return results



def main():
  ns = list(range(2, 6))
  
  with multiprocessing.Pool() as pool:
    resultss = pool.map(processValue, ns)
  
  fig = Figure.create(figsize=(3.6, 3))
  ax = fig.gca()
  
  colors = {ns[i] : helper.plot.mixColors(
                "hellblau", i/(len(ns)-1), "mittelblau")
            for i in range(len(ns))}
  print(colors)
  
  lineStyles = {
    "objectiveFunction" : "-",
    "smoothInterpolant" : "-",
    "linearInterpolant" : "--",
  }
  xl = [-8, 7]
  
  for n, results in zip(ns, resultss):
    for s in ["smoothInterpolant", "linearInterpolant", "objectiveFunction"]:
      if s == "objectiveFunction":
        if (n != ns[-1]): continue
        color, lineWidth, extraArgs = "C1", 3, {"zorder" : -100}
      else:
        color, lineWidth, extraArgs = colors[n], 1, {}
      
      x, y = results[s]["yFuzzyXData"], results[s]["yFuzzyAlphaData"]
      eps = 5e-2 * lineWidth / 2
      x = [xl[0]+eps] + x + [xl[1]-eps]
      y = [0] + y + [0]
      ax.plot(x, y, lineStyles[s], color=color, lw=lineWidth,
              clip_on=False, **extraArgs)
  
  ax.set_xlim(*xl)
  ax.set_xticks([-6, -3, 0, 3, 6])
  
  ax.set_ylim(0, 1)
  ax.set_yticks([0, 1])
  ax.set_ylabel(r"$\memfun{y^\ast}(y)$", labelpad=-4)
  
  trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
  ax.text(*trafo(0.84, -0.05), r"$y$", ha="center", va="top")
  
  helper.plot.addCustomLegend(ax,
    [{
      "label"  : "$n = {}$".format(n),
      "ls"     : "-",
      "color"  : colors[n],
    } for n in ns] +
    [{
      "label"  : r"$\memfun[\sparse,p]{y}$",
      "ls"     : "-",
      "color"  : "k",
    }, {
      "label"  : r"$\memfun[\sparse,1]{y}$",
      "ls"     : "--",
      "color"  : "k",
    }, {
      "label"  : r"$\memfun[\reference]{y}$",
      "ls"     : "-",
      "lw"     : 3,
      "color"  : "C1",
    }],
  ncol=4, loc="upper center", outside=True, shift=(-0.03, 0.01))
  
  fig.save()
  
  
  fig = Figure.create(figsize=(3, 3))
  ax = fig.gca()
  
  lines = [[], []]
  
  for n, results in zip(ns, resultss):
    for line, s in zip(lines, ["smoothInterpolant", "linearInterpolant"]):
      line.append(results[s]["fuzzyError"])
  
  ax.plot(ns, lines[0], "-")
  ax.plot(ns, lines[1], "--")
  
  ax.set_yscale("log")
  
  fig.save()



if __name__ == "__main__":
  main()
