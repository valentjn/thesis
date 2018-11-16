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
  ids = [145, 153, 187, 145]
  ts = list(range(7))
  isStackeds = [False, False, False, True]
  tac = 0.01
  
  #stockLabel = (lambda o: (r"$(\stock_{{t,{0}}} + \normbuy_{{t,{0}}} + "
  #                         r"\normsell_{{t,{0}}}) \wealth_t$").format(o))
  #bondLabel    = r"$\normbond_t \wealth_t$"
  #consumeLabel = r"$\normconsume_t \wealth_t$"
  #wealthLabel  = r"$\wealth_t$"
  
  stockLabel = (lambda o: r"$\acute{{\stock}}_{{t,{}}}$".format(o))
  bondLabel    = r"$\bond_t$"
  consumeLabel = r"$\consume_t$"
  wealthLabel  = r"$\wealth_t$"
  
  stockDashes = (lambda o: ((o*[1, 0.7]) + [1, 3]))
  stockMarker = (lambda o: [".", "s", "^", "v", "x"][o])
  stockMarkerSize = (lambda o: (6 if stockMarker(o) == "." else 3))
  
  for q, (id_, isStacked) in enumerate(zip(ids, isStackeds)):
    fig = Figure.create(figsize=(2.2, 2.2))
    ax = fig.gca()
    
    simulationMat = scipy.io.loadmat(
        "data/finance/results/{:04}/simulation.mat".format(id_))
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
    
    if isStacked:
      ys = []
      
      for o in range(d):
        ys.append(newStock[o,ts])
        plotPolygon(ax, ts, ys, stockLabel(o+1), "C1", 0.3+o*0.1)
      
      ys.append(bond[ts]);    plotPolygon(ax, ts, ys, bondLabel,    "C3", 0.6)
      ys.append(consume[ts]); plotPolygon(ax, ts, ys, consumeLabel, "C4", 0.6)
      ax.plot(ts, wealth[ts], ".-", clip_on=False, color="C0")
      ax.text(ts[1], wealth[ts[1]] + 0.04, wealthLabel,
              color="C0", ha="center", va="bottom")
    else:
      for o in range(d):
        ax.plot(ts, newStock[o,ts], "-", clip_on=False, color="C1",
                marker=stockMarker(o), ms=stockMarkerSize(o),
                dashes=stockDashes(o))
      
      ax.plot(ts, bond[ts],    ".-", clip_on=False, color="C3")
      ax.plot(ts, consume[ts], ".-", clip_on=False, color="C4")
      ax.plot(ts, wealth[ts],  ".-", clip_on=False, color="C0")
    
    #print(np.sum(newStock[:,ts], axis=0) + bond[ts] + consume[ts])
    #print(wealth[ts])
    
    ax.set_xlim(ts[0], ts[-1])
    ax.set_ylim(0, 1)
    ax.set_xticks(ts)
    ax.set_xticklabels([(r"${}$".format(t) if t % 2 == 0 else "")
                        for t in ts])
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax)
    ax.text(*trafo( 0.90, -0.05), r"$t$", ha="center", va="top")
    ax.text(*trafo(-0.10,  0.90), r"\$",  ha="right",  va="center")
    
    fig.save()
  
  
  
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
    } for o in range(5)],
  ncol=8, columnspacing=1, loc="upper center", outside=True)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
