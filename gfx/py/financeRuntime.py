#!/usr/bin/python3
# number of output figures = 7

import numpy as np
import scipy.io

from helper.figure import Figure
import helper.plot



def readRuntimeData(id_):
  resultsPath = "data/finance/results/{:04}".format(id_)
  errorsMat   = scipy.io.loadmat(
      "{}/euler_errors.mat".format(resultsPath))
  resultsMat  = scipy.io.loadmat(
      "{}/results_serialized.mat".format(resultsPath))
  
  errors   = errorsMat["errors"]
  solution = resultsMat["solution"]
  info     = resultsMat["Info"]
  data = {}
  discreteStateName = "Alive"
  
  t = 0
  data["error"] = errors[t,0]["L2"][0,1]
  data["N"] = solution[0,t]["gridPoints"][0,0][discreteStateName].shape[0]
  
  ts = list(range(solution.size))
  
  numberOfJCalls        = info[0,0]["Calls"][0,0]["J"][0,0]
  numberOfGradJCalls    = info[0,0]["Calls"][0,0]["gradJ"][0,0]
  numberOfEvalCalls     = info[0,0]["Calls"][0,0]["Evaluate"][0,0]["J"][0,0]
  numberOfGradEvalCalls = info[0,0]["Calls"][0,0]["Evaluate"][0,0]["gradJ"][0,0]
  
  if numberOfGradJCalls > 0:
    data["numberOfIt"]   = numberOfGradJCalls
    data["numberOfEval"] = numberOfGradEvalCalls
  else:
    data["numberOfIt"]   = numberOfJCalls
    data["numberOfEval"] = numberOfEvalCalls
  
  data["numberOfOpt"] = sum([
      solution[0,t]["gridPoints"][0,0][discreteStateName].shape[0]
      for t in ts[:-1]])
  data["numberOfItPerOpt"]  = data["numberOfIt"] / data["numberOfOpt"]
  data["numberOfEvalPerIt"] = data["numberOfEval"] / data["numberOfIt"]
  
  data["timeTotal"] = info[0,0]["Time"][0,0]["optimizer"][0,0]
  data["timePerOpt"]  = data["timeTotal"] / data["numberOfOpt"]
  data["timePerIt"]   = data["timeTotal"] / data["numberOfIt"]
  data["timePerEval"] = data["timeTotal"] / data["numberOfEval"]
  
  return data



def main():
  idsss = [[list(range(300, 307)), list(range(310, 317)),
            list(range(400, 407)), list(range(410, 417))],
           [list(range(320, 326)), list(range(330, 336)),
            list(range(420, 426)), list(range(430, 436))],
           [list(range(340, 344)), list(range(350, 354)),
            list(range(440, 444)), list(range(450, 454))]]
  ds = [1, 2, 3]
  colors = ["C0", "C1", "C2", "C3"]
  
  for idss, d in zip(idsss, ds):
    fig1 = Figure.create(figsize=(2.2, 2.15), preamble=r"""
\usepackage{siunitx}
""")
    ax1 = fig1.gca()
    
    fig2 = Figure.create(figsize=(2.129, 2.15), preamble=r"""
\usepackage{siunitx}
""")
    ax2 = fig2.gca()
    
    for ids, color in zip(idss, colors):
      data = [readRuntimeData(id_) for id_ in ids]
      keys = sorted(list(data[0].keys()))
      data = {key : [x[key] for x in data] for key in keys}
      
      Ns = data["N"]
      ax1.plot(Ns, data["timeTotal"],   ".-", color=color, ms=6,
               clip_on=False)
      ax1.plot(Ns, data["timePerOpt"],  "s-", color=color, ms=3,
               clip_on=False)
      ax1.plot(Ns, data["timePerIt"],   "d-", color=color, ms=3,
               clip_on=False)
      ax1.plot(Ns, data["timePerEval"], "+-", color=color, ms=6,
               clip_on=False)
      
      ax2.plot(Ns, data["numberOfIt"],        "^-", color=color, ms=3,
               clip_on=False)
      ax2.plot(Ns, data["numberOfEval"],      "v-", color=color, ms=3,
               clip_on=False)
      ax2.plot(Ns, data["numberOfItPerOpt"],  "<-", color=color, ms=3,
               clip_on=False)
      ax2.plot(Ns, data["numberOfEvalPerIt"], ">-", color=color, ms=3,
               clip_on=False)
    
    xl = np.log10([min(Ns), max(Ns)])
    xl = 10**np.array([xl[0]-0.1*(xl[1]-xl[0]), xl[1]+0.1*(xl[1]-xl[0])])
    yls = [(0.999e-5, 1.001e6), (5e0,  3e9)]
    
    for ax, yl in zip([ax1, ax2], yls):
      ax.set_xscale("log")
      ax.set_yscale("log")
      ax.set_xlim(*xl)
      ax.set_ylim(*yl)
      yt = np.arange(np.floor(np.log10(yl[0]))+1, np.ceil(np.log10(yl[1])))
      ax.set_yticks(10**yt)
      ax.set_yticklabels([(r"$10^{{{:.0f}}}$".format(y) if y % 2 == 0 else "")
                          for y in yt])
    
    x = Ns[-1]
    
    if d == 1:   y = 2e-1
    elif d == 2: y = 4e-1
    elif d == 3: y = 9e-1
    helper.plot.plotConvergenceLine(ax1, x, y, -1, tx=0.6*x, ty=y)
    
    if d == 1:   y = 2e3
    elif d == 2: y = 6e3
    elif d == 3: y = 1e4
    helper.plot.plotConvergenceLine(ax1, x, y, -2, tx=0.6*x, ty=0.1*y)
    
    y = 2e5
    helper.plot.plotConvergenceLine(ax2, x, y, -1, tx=0.6*x, ty=0.18*y)
    
    trafo1 = helper.plot.getTransformationFromUnitCoordinates(ax1)
    trafo2 = helper.plot.getTransformationFromUnitCoordinates(ax2)
    
    if d == 1:   x = 0.69
    elif d == 2: x = 0.48
    elif d == 3: x = 0.48
    
    ax1.text(*trafo1(x, -0.05), r"$\ngp$", ha="center", va="top")
    ax1.text(*trafo1(0.05, 1), r"[\si{\second}]", ha="left",  va="top")
    
    ax2.text(*trafo2(x, -0.05), r"$\ngp$", ha="center", va="top")
    
    fig1.save()
    fig2.save()
  
  
  
  fig = Figure.create(figsize=(6, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax,
    [{
      "label"  : r"Total time",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 6,
    }, {
      "label"  : r"Time per opt.",
      "marker" : "s",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"Time per it.",
      "marker" : "d",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"Time per eval.",
      "marker" : "+",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 6,
    }, {
      "label"  : r"\#It.",
      "marker" : "^",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"\#Eval.",
      "marker" : "v",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"\#It./\#Opt.",
      "marker" : "<",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"\#Eval./\#It.",
      "marker" : ">",
      "ls"     : "-",
      "color"  : "k",
      "ms"     : 3,
    }, {
      "label"  : r"$p = 3$, $\nabla$",
      "marker" : "",
      "ls"     : "-",
      "color"  : colors[0],
    }, {
      "label"  : r"$p = 3$, FD",
      "marker" : "",
      "ls"     : "-",
      "color"  : colors[1],
    }, {
      "label"  : r"$p = 1$, $\nabla$",
      "marker" : "",
      "ls"     : "-",
      "color"  : colors[2],
    }, {
      "label"  : r"$p = 1$, FD",
      "marker" : "",
      "ls"     : "-",
      "color"  : colors[3],
    }],
  ncol=4, columnspacing=0.5, loc="upper center", outside=True)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
