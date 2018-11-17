#!/usr/bin/python3
# number of output figures = 3

import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



def main():
  ids = [91, 96, 101]
  t = 0
  d = 2
  discreteStateName = "Alive"
  
  v = np.linspace(-8, -5/3, 20)
  vClip = [v[0] + 0.01 * (v[-1] - v[0]), v[-1] - 0.01 * (v[-1] - v[0])]
  
  xt = [0, 0.25, 0.5, 0.75, 1]
  xtl = ["$0$", "", "$0.5$", "", "$1$"]
  yt, ytl = xt, xtl
  
  
  
  for id_ in ids:
    fig = Figure.create(figsize=(3, 3), scale=0.75)
    ax = fig.gca()
    
    resultsPath  = "data/finance/results/{:04}".format(id_)
    errorsMat = scipy.io.loadmat("{}/euler_errors.mat".format(resultsPath))
    errors = errorsMat["errors"]
    XX = errors[t,0]["points"]
    YY = errors[t,0]["All"][:,1]
    
    for point in [(0, 0), (0, 1), (1, 0)]:
      k = np.argmin(np.sum((XX - point)**2, axis=1))
      XX = np.vstack((XX, point))
      YY = np.append(YY, YY[k])
    
    YY = np.log10(np.abs(YY))
    print(np.amin(YY), np.amax(YY))
    YY = np.clip(YY, *vClip)
    contour = ax.tricontourf(*XX.T, YY, v)
    helper.plot.removeWhiteLines(contour)
    
    ax.set_xticks(xt)
    ax.set_xticklabels(xtl)
    ax.set_yticks(yt)
    ax.set_yticklabels(ytl)
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo( 0.85, -0.07), r"$\stock_{t,1}$", ha="center", va="top")
    ax.text(*trafo(-0.05,  0.82), r"$\stock_{t,2}$", ha="right",  va="center")
    
    fig.save()
  
  
  
  fig = Figure.create(figsize=(5, 2))
  ax = fig.gca()
  fig.colorbar(contour, orientation="horizontal", fraction=1, extend="min",
              ticks=np.arange(v[0], v[-1]+0.01, 1), format="$10^{%u}$")
  ax.set_axis_off()
  fig.save()
  
  
  
  #import helper.grid
  #idRef =  14
  #idSG  = 104
  #t = 0
  #d = 2
  #discreteStateName = "Alive"
  #
  #resultsRefPath = "data/finance/results/{:04}".format(idRef)
  #resultsSGPath  = "data/finance/results/{:04}".format(idSG)
  #
  #v = np.linspace(-9, -2, 17)
  #vClip = [v[0] + 0.01 * (v[-1] - v[0]), v[-1] - 0.01 * (v[-1] - v[0])]
  #
  #policyNames = (["DeltaNormNormS{}Buy".format(t+1)  for t in range(d)] +
  #               ["DeltaNormNormS{}Sell".format(t+1) for t in range(d)] +
  #               ["normNormB"])
  #nn = (129, 129)
  #XX0, XX1, XX = helper.grid.generateMeshGrid(nn)
  #
  #for policyName in policyNames:
  #  fig = Figure.create(figsize=(3, 3))
  #  ax = fig.gca()
  #  
  #  policiesRefMat = scipy.io.loadmat(
  #      "{}/policies_serialized.mat".format(resultsRefPath))
  #  interpPolicyRef = policiesRefMat["interpPolicy"]
  #  interpolantRef = helper.finance.createPolicyInterpolant(
  #      interpPolicyRef, t, discreteStateName, policyName)
  #  YYRef = interpolantRef.evaluate(XX)
  #  del interpolantRef
  #  del interpPolicyRef
  #  del policiesRefMat
  #  
  #  policiesSGMat = scipy.io.loadmat(
  #      "{}/policies_serialized.mat".format(resultsSGPath))
  #  interpPolicySG = policiesSGMat["interpPolicy"]
  #  interpolantSG = helper.finance.createPolicyInterpolant(
  #      interpPolicySG, t, discreteStateName, policyName)
  #  YYSG  = interpolantSG.evaluate(XX)
  #  
  #  YY = np.reshape(np.log10(np.maximum(np.abs(YYRef - YYSG), 1e-100)),
  #                  XX0.shape)
  #  YY = np.clip(YY, *vClip)
  #  contour = ax.contourf(XX0, XX1, YY, v)
  #  helper.plot.removeWhiteLines(contour)
  #  
  #  fig.save()



if __name__ == "__main__":
  main()
