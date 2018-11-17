#!/usr/bin/python3
# number of output figures = 5

import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



def main():
  idsss = [
      [list(range(  0,   7)), list(range( 70,  85))],
      [list(range( 30,  37)), list(range( 90, 105))],
      [list(range( 40,  45)), list(range(130, 146))],
      [list(range( 50,  53)), list(range(150, 156))],
  ]
  
  for d, idss in zip(list(range(1, 5)), idsss):
    fig = Figure.create(figsize=(1.8, 2.5))
    ax = fig.gca()
    
    errorss = []
    
    for i, ids in enumerate(idss):
      if ids is None: continue
      errors = []
      
      for id_ in ids:
        resultsPath = "data/finance/results/{:04}".format(id_)
        
        policiesMat = scipy.io.loadmat(
            "{}/policies_serialized.mat".format(resultsPath))
        interpPolicy = policiesMat["interpPolicy"]
        t, discreteStateName = 0, "Alive"
        policyNames = (["DeltaNormNormS{}Buy".format(t+1)  for t in range(d)] +
                      ["DeltaNormNormS{}Sell".format(t+1) for t in range(d)] +
                      ["normNormB"])
        N = np.mean([helper.finance.createPolicyInterpolant(interpPolicy,
                        t, discreteStateName, policyName).X.shape[0]
                    for policyName in policyNames])
        
        errorsMat = scipy.io.loadmat("{}/euler_errors.mat".format(resultsPath))
        error = errorsMat["errors"][t,0]["L2"][0,1]
        errors.append((N, error))
      
      errors.sort(key=lambda x: x[0])
      errors = np.array(errors)
      ax.plot(*errors.T, ".-", color="C{}".format(i), clip_on=False)
      errorss.append(errors)
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    
    allNs = [N for errors in errorss for N in errors[:,0]]
    xl = [min(allNs), max(allNs)]
    if d > 1: xl[1] = max(xl[1], 1.01e4)
    ax.set_xlim(*xl)
    xt = [x for x in [1e2, 1e3, 1e4] if xl[0] <= x <= xl[1]]
    ax.set_xticks(xt)
    
    allErrors = [error for errors in errorss for error in errors[:,1]]
    yl = [min(allErrors), max(allErrors)]
    yl = [yl[0], 10**(np.log10(yl[1]) +
                      0.15 * (np.log10(yl[1]) - np.log10(yl[0])))]
    ax.set_ylim(*yl)
    
    yt = ax.get_yticks()
    ytl = [r"$10^{{{:.0f}}}$".format(np.log10(y)) for y in yt]
    ax.set_yticklabels(ytl, va="center", rotation=60)
    ax.tick_params(axis="y", pad=-5)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.04, 1.0),
            r"$\weightedeulererrorLtwo_t$", ha="left", va="top")
    _, y = trafo(1e3, -0.05)
    ax.text(10**(2.5 if d == 1 else 3.5), y, r"$\ngp_t$",
            ha="center", va="top")
    
    fig.save()
  
  
  
  fig = Figure.create(figsize=(6, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax,
    [{
      "label"  : "Regular",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C0",
    }, {
      "label"  : "Spatially adaptive",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C1",
    }],
  ncol=4, columnspacing=1, loc="upper center", outside=True)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
