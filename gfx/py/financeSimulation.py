#!/usr/bin/python3
# number of output figures = 4

import matplotlib as mpl
import numpy as np
import scipy.io

from helper.figure import Figure
import helper.finance
import helper.plot



def plotPolygon(ax, ts, ys, label, color, opacity):
  if len(ys) == 1: ys = [np.zeros(ys[0].shape)] + ys
  yLower = sum(ys[:-1])
  yUpper = yLower + ys[-1]
  vertices = ([(t, y) for t, y in zip(ts, yLower)] +
              [(t, y) for t, y in zip(ts[::-1], yUpper[::-1])])
  backgroundColor = helper.plot.mixColors("mittelblau", 0.1)
  lightColor = helper.plot.mixColors(color, opacity, backgroundColor)
  ax.add_patch(mpl.patches.Polygon(vertices, fc=lightColor, ec=lightColor))
  label = r"\contour{{mittelblau!10}}{{{}}}".format(label)
  ax.text(ts[1], (yLower[1] + yUpper[1]) / 2 - 0.01, label, color=color,
          ha="center", va="center")



def main():
  ids = [145, 153, 502, 145]
  ts = list(range(7))
  isStackeds = [False, False, False, True]
  tac = 0.01
  
  #stockLabel = (lambda o: (r"$(\stock_{{t,{0}}} + \normbuy_{{t,{0}}} - "
  #                         r"\normsell_{{t,{0}}}) \wealth_t$").format(o))
  #bondLabel    = r"$\normbond_t \wealth_t$"
  #consumeLabel = r"$\normconsume_t \wealth_t$"
  #wealthLabel  = r"$\wealth_t$"
  
  stockLabel = (lambda o: r"$\acute{{\stock}}_{{t,{}}}$".format(o))
  bondLabel    = r"$\bond_t$"
  consumeLabel = r"$\consume_t$"
  wealthLabel  = r"$\wealth_t$"
  errorLabel   = r"$\weightedeulererrorLtwo_t$"
  
  stockDashes = (lambda o: ((o*[1, 0.7]) + [1, 3]))
  stockMarker = (lambda o: [".", "s", "^", "v", "x"][o])
  stockMarkerSize = (lambda o: (6 if stockMarker(o) == "." else 3))
  
  for q, (id_, isStacked) in enumerate(zip(ids, isStackeds)):
    width = (1.85 if isStacked else 2.2)
    fig = Figure.create(figsize=(width, 2.2))
    ax1 = fig.gca()
    
    resultsPath = "data/finance/results/{:04}".format(id_)
    simulationMat = scipy.io.loadmat("{}/simulation.mat".format(resultsPath))
    simulation = simulationMat["simulation"]
    
    state = list(simulation[0,0]["state"][0,0].tolist())
    state = np.stack(state, axis=0)
    d = state.shape[0] - 1
    normStock = state[:d,:,:]
    wealth    = state[ d,:,:]
    
    policy = list(simulation[0,0]["policy"][0,0].tolist())
    policy = np.stack(policy, axis=0)
    normBuy  = policy[ :d,  :,:]
    normSell = policy[d:2*d,:,:]
    normBond = policy[  2*d,:,:]
    
    newStock = (normStock[:,:,:-1] + normBuy - normSell) * wealth[:,:-1]
    bond = normBond * wealth[:,:-1]
    consume = ((1 - np.sum(normStock[:,:,:-1], axis=0)) - normBond -
               np.sum(normBuy, axis=0) +
               np.sum(normSell, axis=0)) * wealth[:,:-1]
    
    newStock = np.mean(newStock, axis=1)
    wealth   = np.mean(wealth, axis=0)
    bond     = np.mean(bond, axis=0)
    consume  = np.mean(consume, axis=0)
    
    print("d = {}".format(d))
    print("stdev(c_t) = {}".format(np.std(consume)))
    print("stdev(c_t)/mean(c_t) = {}".format(
        np.std(consume) / np.mean(consume)))
    
    for t in ts[:-1]:
      print("stock weightes for t = {}: [{}]".format(t, ", ".join([
          "{:.5f}".format(x)
          for x in newStock[:,t] / np.sum(newStock[:,t])])))
    
    if isStacked:
      ys = []
      
      for o in range(d):
        ys.append(newStock[o,ts])
        plotPolygon(ax1, ts, ys, stockLabel(o+1), "C1", 0.3+o*0.1)
      
      ys.append(bond[ts])
      plotPolygon(ax1, ts, ys, bondLabel,    "C3", 0.6)
      ys.append(consume[ts])
      plotPolygon(ax1, ts, ys, consumeLabel, "C4", 0.6)
      ax1.plot(ts, wealth[ts], ".-", clip_on=False, color="C0")
      ax1.text(ts[1], wealth[ts[1]] + 0.04, wealthLabel,
              color="C0", ha="center", va="bottom")
    else:
      for o in range(d):
        ax1.plot(ts, newStock[o,ts], "-", clip_on=False, color="C1",
                 marker=stockMarker(o), ms=stockMarkerSize(o),
                 dashes=stockDashes(o))
      
      ax1.plot(ts, bond[ts],    ".-", clip_on=False, color="C3")
      ax1.plot(ts, consume[ts], ".-", clip_on=False, color="C4")
      ax1.plot(ts, wealth[ts],  ".-", clip_on=False, color="C0")
    
    #print(np.sum(newStock[:,ts], axis=0) + bond[ts] + consume[ts])
    #print(wealth[ts])
    
    ax1.set_xlim(ts[0], ts[-1])
    ax1.set_ylim(0, 1)
    ax1.set_xticks(ts)
    ax1.set_xticklabels([(r"${}$".format(t) if t % 2 == 0 else "")
                         for t in ts])
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax1)
    ax1.text(*trafo( 0.90, -0.05), r"$t$", ha="center", va="top")
    ax1.text(*trafo(-0.10,  0.90), r"\$",  ha="right",  va="center")
    
    ax1.spines["right"].set_visible(False)
    ax1.spines["top"].set_visible(False)
    
    if not isStacked:
      ax2 = ax1.twinx()
      
      errorsMat = scipy.io.loadmat("{}/euler_errors.mat".format(resultsPath))
      errors = ([errorsMat["errors"][t,0]["L2"][0,1] for t in ts[:-1]] +
                [1e-100])
      ax2.plot(ts, errors, "--", color="C8")
      ax2.plot(ts, errors, ".", color="C8", clip_on=False)
      
      ax2.set_yscale("log")
      yl = [10**np.floor(np.log10(min(errors[:-1]))),
            10**np.ceil(np.log10(max(errors[:-1])))]
      ax2.set_ylim(*yl)
      mpl.pyplot.setp(ax2.get_yminorticklabels(), visible=False)
      ax2.set_ylabel(errorLabel, labelpad=-20)
      
      ax2.spines["left"].set_visible(False)
      ax2.spines["bottom"].set_visible(False)
      ax2.spines["top"].set_visible(False)
      ax2.spines["right"].set_color("C8")
      ax2.yaxis.label.set_color("C8")
      ax2.tick_params(axis="y", which="both", colors="C8")
    
    fig.save(hideSpines=False)
  
  
  
  fig = Figure.create(figsize=(6, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax,
    [{
      "label"  : wealthLabel,
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C0",
    }, {
      "label"  : bondLabel,
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C3",
    }, {
      "label"  : consumeLabel,
      "marker" : ".",
      "ls"     : "-",
      "color"  : "C4",
    }] +
    [{
      "label"  : stockLabel(o+1),
      "marker" : stockMarker(o),
      "ms"     : stockMarkerSize(o),
      "dashes" : stockDashes(o),
      "color"  : "C1",
    } for o in range(5)] +
    [{
      "label"  : errorLabel,
      "marker" : ".",
      "ls"     : "--",
      "color"  : "C8",
    }],
  ncol=9, columnspacing=0.5, loc="upper center", outside=True)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
