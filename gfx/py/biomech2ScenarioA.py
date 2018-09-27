#!/usr/bin/python3
# number of output figures = 5
# dependencies = SG++, cpp/applyBiomech2

import numpy as np

from helper.figure import Figure
import helper.plot

import helperBiomech2



def main():
  ts = [0, 1, 2, 3, 4]
  forceLoads = [22, 22, 22, 30, 40]
  targetAngles = [75, 75, 60, 60, 50]
  
  xtl = ["$t_{{{}}}$".format(t) for t in ts]
  
  figSize = (3.2, 2.45)
  
  
  
  fig = Figure.create(figsize=(figSize[0]-0.3, figSize[1]), preamble=r"""
\usepackage{siunitx}
""")
  ax1 = fig.gca()
  colors = ["C0", "C1"]
  
  ax1.plot(ts, forceLoads, "s-", color=colors[0], ms=3)
  ax1.set_xticks(ts)
  ax1.set_xticklabels(xtl)
  ax1.set_ylim(0, 100*(1+1/15))
  ax1.set_yticks([0, 20, 40, 60, 80, 100])
  ax1.set_xlabel(r"Time")
  ax1.set_ylabel(r"$\forceL$ [$\si{\newton}$]", color=colors[0], labelpad=0)
  ax1.spines["right"].set_visible(False)
  ax1.spines["left"].set_color(colors[0])
  ax1.tick_params(axis="y", which="both", colors=colors[0])
  
  ax2 = ax1.twinx()
  ax2.plot(ts, targetAngles, "s-", color=colors[1], ms=3)
  ax2.set_ylim(0, 80)
  ax2.set_yticks([0, 15, 30, 45, 60, 75])
  ax2.set_ylabel(r"$\tarelbang$ [${}^{\circ}]$", color=colors[1])
  ax2.spines["left"].set_visible(False)
  ax2.spines["bottom"].set_visible(False)
  ax2.spines["right"].set_color(colors[1])
  ax2.tick_params(axis="y", which="both", colors=colors[1])
  
  for ax in [ax1, ax2]:
    ax.spines["top"].set_visible(False)
  
  fig.save(hideSpines=False)
  
  
  
  action = "solveScenarioA"
  basisType, ps, forceLoad = "modifiedClenshawCurtisBSpline", [3, 1], 22
  XX = None
  
  A = {}
  A["fg"] = helperBiomech2.applyBiomech2Scattered(
      action, "fullGrid", basisType, ps[0], forceLoad, XX)
  
  for p in ps:
    A[p] = helperBiomech2.applyBiomech2Scattered(
        action, "sparseGrid", basisType, p, forceLoad, XX)
  
  
  
  lineStyles = {1 : "^--", 3 : ".-", "fg" : "v:"}
  markerSizes = {1 : 3, 3 : 6, "fg" : 3}
  
  fig = Figure.create(figsize=(figSize[0]-0.47, figSize[1]))
  ax = fig.gca()
  
  colors = ["C2", "C3"]
  
  for p in ps + ["fg"]:
    lineStyle, markerSize = lineStyles[p], markerSizes[p]
    actT, actB = A[p][:,1], A[p][:,2]
    ax.plot(ts, actT, lineStyle, color=colors[0], ms=markerSize,
            clip_on=False)
    ax.plot(ts, actB, lineStyle, color=colors[1], ms=markerSize,
            clip_on=False)
  
  ax.set_xticks(ts)
  ax.set_xticklabels(xtl)
  ax.set_ylim(0, 1)
  ax.set_xlabel(r"Time")
  ax.set_ylabel((r"\textcolor{{{}}}{{$\actT$}}, "
                 r"\textcolor{{{}}}{{$\actB$}}").format(*colors))
  
  fig.save()
  
  
  
  fig = Figure.create(figsize=figSize, preamble=r"""
\usepackage{siunitx}
\sisetup{inter-unit-product={\hspace{0.03em}}}
""")
  ax1 = fig.gca()
  ax2 = ax1.twinx()
  
  colors = ["C4", "C5"]
  
  for p in ps:
    lineStyle, markerSize = lineStyles[p], markerSizes[p]
    equilibriumAngle, equilibriumAngleRef = A[p][:,3], A[p][:,4]
    error = np.maximum(np.abs(equilibriumAngle    - targetAngles), 1e-100)
    ax1.plot(ts, error, lineStyle, color=colors[0], ms=markerSize)
    error = np.maximum(np.abs(equilibriumAngleRef - targetAngles), 1e-100)
    ax1.plot(ts, error, lineStyle[1:], color=colors[0], clip_on=False)
    ax1.plot(ts, error, lineStyle[0],
             color=helper.plot.mixColors("mittelblau", 0.1),
             mec=colors[0], ms=1.5*markerSize, clip_on=False)
    momentum = A[p][:,5]
    ax2.plot(ts, np.abs(momentum), lineStyle, color=colors[1],
             ms=markerSize, clip_on=False)
  
  ax1.text(2, 8e-1, r"$\abs{\equielbangref{\forceL} - \tarelbang}$",
           color=colors[0], ha="left", va="bottom")
  ax1.text(0, 3e-8, r"$\abs{\equielbangintp{\forceL} - \tarelbang}$",
           color=colors[0], ha="left", va="bottom")
  ax1.plot([2.9, 2.8], [1.5e0, 5e-1], "k-", clip_on=False)
  ax1.plot([3, 3.3], [1.5e0, 1.5e-2], "k-", clip_on=False)
  ax1.plot([0.9, 1.2], [3e-8, 3e-9], "k-", clip_on=False)
  ax1.plot([1, 1.8], [3e-8, 2e-9], "k-", clip_on=False)
  
  for ax in [ax1, ax2]:
    ax.set_yscale("log")
    ax.spines["top"].set_visible(False)
  
  ax1.set_ylim(1e-10, 1e0)
  ax2.set_ylim(5e-4, 1e0)
  ax1.set_xticks(ts)
  ax1.set_xticklabels(xtl)
  ax1.set_xlabel(r"Time")
  ax1.set_ylabel(r"$\abs{\equielbang{\forceL} - \tarelbang}$ [${}^{\circ}$]",
                 color=colors[0])
  ax1.spines["left"].set_color(colors[0])
  ax1.spines["right"].set_visible(False)
  ax1.tick_params(axis="y", which="both", colors=colors[0])
  ax2.spines["left"].set_visible(False)
  ax2.spines["bottom"].set_visible(False)
  ax2.spines["right"].set_color(colors[1])
  ax2.tick_params(axis="y", which="both", colors=colors[1])
  ax2.set_ylabel(r"$|\momentref|$ [\si{\newton\meter}]", color=colors[1])
  
  fig.save(hideSpines=False)
  
  
  
  fig = Figure.create(figsize=figSize)
  ax1 = fig.gca()
  ax2 = ax1.twinx()
  
  colors = ["C6", "C7"]
  
  for p in ps + ["fg"]:
    lineStyle, markerSize = lineStyles[p], markerSizes[p]
    numberOfEvaluations, numberOfNewtonIterations = A[p][:,6], A[p][:,7]
    ax1.plot(ts, numberOfEvaluations, lineStyle,
             color=colors[0], ms=markerSize)
    ax2.plot(ts, numberOfNewtonIterations / numberOfEvaluations, lineStyle,
             color=colors[1], ms=markerSize)
  
  for ax in [ax1, ax2]:
    ax.spines["top"].set_visible(False)
  
  ax1.set_yscale("log")
  ax1.set_ylim(5e2, 3e4)
  ax2.set_ylim(0, 6)
  ax1.set_xticks(ts)
  ax1.set_xticklabels(xtl)
  ax2.set_yticks(list(range(7)))
  ax1.set_xlabel(r"Time")
  ax1.set_ylabel(r"\#Evaluations",
                 color=colors[0])
  ax1.spines["left"].set_color(colors[0])
  ax1.spines["right"].set_visible(False)
  ax1.tick_params(axis="y", which="both", colors=colors[0])
  ax2.spines["left"].set_visible(False)
  ax2.spines["bottom"].set_visible(False)
  ax2.spines["right"].set_color(colors[1])
  ax2.tick_params(axis="y", which="both", colors=colors[1])
  ax2.set_ylabel(r"\#Newton iterations per eval.", color=colors[1])
  
  fig.save(hideSpines=False)
  
  
  
  fig = Figure.create(figsize=(5, 2))
  ax = fig.gca()
  
  labels = {
    1    : r"Using $\forceXintp[p,\cc]$, $p = 1$",
    3    : r"Using $\forceXintp[p,\cc]$, $p = 3$",
    "fg" : r"Using $\forceXref$",
  }
  
  helper.plot.addCustomLegend(ax, [
        {
          "label"  : labels[p],
          "ls"     : lineStyles[p][1:],
          "marker" : lineStyles[p][0],
          "color"  : "k",
          "ms"     : markerSizes[p],
        } for p in ps + ["fg"]
      ], ncol=3, loc="upper center", outside=True, columnspacing=1.5)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
