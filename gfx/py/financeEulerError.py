#!/usr/bin/python3
# number of output figures = 4

import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



def main():
  idsss = [
      [list(range(  0,   7)),                  None, list(range( 70,  85))],
      [list(range( 10,  15)), list(range( 30,  37)), list(range( 90, 105))],
      [list(range( 20,  23)), list(range( 40,  45)), list(range(130, 146))],
  ]
  
  for d, idss in zip(list(range(1, 5)), idsss):
    fig = Figure.create(figsize=(2.2, 2.5))
    ax = fig.gca()
    
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
        N = np.mean([helper.finance.createPolicyInterpolant(
                        interpPolicy, t, discreteStateName, policyName).X.shape[0]
                    for policyName in policyNames])
        
        errorsMat = scipy.io.loadmat("{}/euler_errors.mat".format(resultsPath))
        error = errorsMat["errors"][0,t]["L2"][0,1]
        errors.append((N, error))
      
      errors.sort(key=lambda x: x[0])
      errors = np.array(errors)
      ax.plot(*errors.T, ".-", color="C{}".format(i))
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    
    if   d == 1: ax.set_ylim(2e-9, 2e-4)
    elif d == 2: ax.set_ylim(2e-6, 2e-2)
    elif d == 3: ax.set_ylim(4e-4, 2e-1)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.04, 1.0),
            r"$\normLtwo{\weightedeulererror_0}$",
            ha="left", va="top")
    if   d == 1: x = 0.6
    elif d == 2: x = 0.7
    elif d == 3: x = 0.65
    ax.text(*trafo(x, -0.05), r"$\ngp$",
            ha="center", va="top")
    
    fig.save()
  
  
  
  fig = Figure.create(figsize=(6, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax,
    [{
      "label"  : "Full grid",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C0",
    }, {
      "label"  : "Regular sparse grid",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C1",
    }, {
      "label"  : "Spatially adaptive sparse grid",
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C2",
    }],
  ncol=4, columnspacing=1, loc="upper center", outside=True)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
