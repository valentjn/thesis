#!/usr/bin/python3
# number of output figures = 16

import functools
#import multiprocessing

import matplotlib as mpl
import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



# [0.0799766874430739, 0.08072246694422885]
# => [0.07997, 0.08073]

# [-0.0001096208936957018, 0.24599289767182117]
# [0.0, 0.0]
# [-0.0017463921461824987, 0.046543738359753]
# [-0.0033269233122418217, 0.10812555581028431]
# [-0.003458789681274944, 0.18618537173449765]
# => [-0.01, 0.25]

# [-0.008138312904481245, 0.41993021741271347]
# [-0.007155007789828884, 0.5239357160801648]
# [-0.016213665974931818, 0.501343836021499]
# [-0.0319476674370214, 0.5057203369231993]
# [-0.01061945123224955, 0.4867600705683158]
# => [-0.04, 0.53]

# [-0.0003118428508431817, 0.19680021889283394]
# =>  [-0.01, 0.20]

def plotJOrPolicy(solution, interpPolicy, discreteStateName, t, parameters):
  q, name, interpolant, slicePoint, sliceDims = parameters
  o0, o1 = sliceDims
  d = len(slicePoint)
  
  fig = Figure.create(figsize=(3, 3), scale=0.57)
  ax = fig.gca()
  
  if name == "J":
    zl = (0.07997, 0.08073)
    zLabel = r"$\normcetvalueintp[1]_t$"
  elif name.endswith("Buy"):
    zl = (-0.01, 0.12)
    zLabel = r"$\normbuy[\opt,\sparse,1]_{{t,{}}}$".format(name[-4])
  elif name.endswith("Sell"):
    zl = (-0.04, 0.66)
    zLabel = r"$\normsell[\opt,\sparse,1]_{{t,{}}}$".format(name[-5])
  else:
    zl = (-0.20, 0.30)
    zLabel = r"$\normbond_t^{\opt,\sparse,1}$"
  
  nn = (65, 65)
  xBreak = 0.25
  
  #if name in ["DeltaNormNormS1Buy", "normNormB"]:
  #  xxo0 = np.linspace(0, xBreak, (nn[0]+1)//2)
  #  xxo0 = np.append(xxo0, np.linspace(xBreak, 1, (nn[0]+1)//2)[1:])
  #else:
  xxo0 = np.linspace(0, 1, nn[0])
  
  #if name in ["DeltaNormNormS2Buy", "normNormB"]:
  #  xxo1 = np.linspace(0, xBreak, (nn[0]+1)//2)
  #  xxo1 = np.append(xxo1, np.linspace(xBreak, 1, (nn[1]+1)//2)[1:])
  #else:
  xxo1 = np.linspace(0, 1, nn[1])
  
  XXo0, XXo1 = np.meshgrid(xxo0, xxo1)
  XXo01 = np.column_stack([XXo0.flatten(), XXo1.flatten()])
  XXo01 = (interpolant.bounds[0,[o0,o1]] +
           (interpolant.bounds[1,[o0,o1]] -
            interpolant.bounds[0,[o0,o1]]) * XXo01)
  NN = XXo01.shape[0]
  XXo0 = np.reshape(XXo01[:,0], nn)
  XXo1 = np.reshape(XXo01[:,1], nn)
  XX = np.tile(np.reshape(slicePoint, (1, -1)), (NN, 1))
  XX[:,o0] = XXo01[:,0]
  XX[:,o1] = XXo01[:,1]
  YY = np.reshape(interpolant.evaluate(XX), nn)
  
  #zl = [np.amin(YY), np.amax(YY)]
  print([np.amin(YY), np.amax(YY)])
  v = 20
  contour = ax.contourf(XXo0, XXo1, YY, v, vmin=zl[0], vmax=zl[1])
  helper.plot.removeWhiteLines(contour)
  
  X = interpolant.X
  K = np.argsort(np.sum(X, axis=1))
  X = X[K,:]
  
  #on01 = [o for o in range(d) if o not in [o0, o1]]
  #K = np.all(np.equal(X[:,on01], slicePoint[on01]), axis=1)
  #X = X[K,:]
  #X = X[:,[o0,o1]]
  X = X[:,[o0,o1]]
  
  X = np.unique(X, axis=0)
  
  backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
  ax.plot(*X.T, "k.", clip_on=False,
          mec=backgroundColor, mew=0.5, ms=7)
  
  ax.set_xlim(0, 1)
  ax.set_ylim(0, 1)
  
  xt = [0, 0.25, 0.5, 0.75, 1]
  xtl = ["$0$", "", "", "", "$1$"]
  yt, ytl = xt, xtl
  ax.set_xticks(xt)
  ax.set_xticklabels(xtl)
  ax.set_yticks(yt)
  ax.set_yticklabels(ytl)
  
  trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
  ax.text(*trafo( 0.5, -0.07), r"$\stock_{{t,{}}}$".format(o0+1),
          ha="center", va="top")
  ax.text(*trafo(-0.05,  0.5), r"$\stock_{{t,{}}}$".format(o1+1),
          ha="right",  va="center", rotation=90)
  ax.text(*trafo(0.97, 0.95),
          r"\contour{{mittelblau!10}}{{{}}}".format(zLabel),
          ha="right", va="top")
  
  fig.save(graphicsNumber=q+1)



def main():
  ids = [502]
  q0 = 0
  
  for id_ in ids:
    d = 5
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
    
    a = 0.1
    slicePoints = np.array([
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
        [a, a, a, a, a],
    ])
    
    sliceDimss = [
      (0, 1),
      (0, 1),
      (1, 2),
      (2, 3),
      (3, 4),
      (4, 0),
      (0, 1),
      (1, 2),
      (2, 3),
      (3, 4),
      (4, 0),
      (0, 1),
    ]
    
    interpolants = [(
        helper.finance.createJInterpolant(
          solution, t, discreteStateName, name="interpJ") if name == "J" else
        helper.finance.createPolicyInterpolant(
          interpPolicy, t, discreteStateName, name)) for name in names]
    parameterss = list(zip(qs, names, interpolants, slicePoints, sliceDimss))
    
    #with multiprocessing.Pool() as pool:
    #  pool.map(functools.partial(plotJOrPolicy,
    #        solution, interpPolicy, discreteStateName, t, isSparseGrid),
    #      parameterss)
    
    for parameters in parameterss:
      plotJOrPolicy(solution, interpPolicy, discreteStateName, t, parameters)
  
  
  
  for q in range(4):
    v = [(0.07997, 0.08073), (-0.01, 0.25),
         (-0.04, 0.53), (-0.01, 0.20)][q]
    labels = [r"$\normcetvalueintp[1]_t$", r"$\normbuy[\sparse,1]_{t,o}$",
             r"$\normsell[\sparse,1]_{t,o}$", r"$\normbond_t^{\sparse,1}$"]
    label = labels[q]
    label += "".join([r"\vphantom{{{}}}".format(x) for x in labels])
    width = [1.83, 1.58, 1.57, 1.63][q]
    
    fig = Figure.create(figsize=(width, 0.75))
    ax = fig.gca()
    
    colorMap = mpl.cm.viridis
    norm = mpl.colors.Normalize(v[0], v[-1])
    xt = ([0, 0.1*np.floor(10*v[-1])] if q > 0 else [0.0800, 0.0807])
    colorBar = mpl.colorbar.ColorbarBase(
      ax, cmap=colorMap, ticks=xt, norm=norm, orientation="horizontal")
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo(0.5, -0.07), label, ha="center", va="top")
    
    fig.save(graphicsNumber=q0+q+1)



if __name__ == "__main__":
  main()
