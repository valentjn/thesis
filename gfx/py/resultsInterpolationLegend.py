#!/usr/bin/python3
# number of output figures = 1

from helper.figure import Figure
import helper.plot



ps = [1, 3, 5]
markerStyles = {1 : ".", 3 : "^",  5 : "v"}
lineStyles   = {1 : "-", 3 : "--", 5 : ":"}



fig = Figure.create(figsize=(5, 2))
ax = fig.gca()

functionNames = ["Bra02", "GoP", "Sch06", "Ack", "Alp02", "Sch22"]

helper.plot.addCustomLegend(ax, (
  [{
    "label"  : functionNames[r],
    "ls"     : "-",
    "color"  : "C{}".format(r),
  } for r in range(len(functionNames))] +
  [{
    "label"  : "$p = {}$".format(p),
    "marker" : {1 : ".", 3 : "^", 5 : "v"}[p],
    "ms"     : (4.5 if p == 1 else 2.5),
    "ls"     : lineStyles[p],
    "color"  : "k",
  } for p in ps]
), ncol=6, loc="upper center", outside=True)

ax.set_axis_off()

fig.save()



fig = Figure.create(figsize=(5, 5))
ax = fig.gca()

basisNames = [
  #r"B-splines $\bspl{\*l,\*i}{p}$",
  #r"NAK B-splines $\bspl[\nak]{\*l,\*i}{p}$",
  #r"Mod. B-splines $\bspl[\modified]{\*l,\*i}{p}$",
  #r"Mod. NAK B-splines $\bspl[\modified,\nak]{\*l,\*i}{p}$",
  #r"Fund. splines $\bspl[\fs]{\*l,\*i}{p}$",
  #r"Fund. NAK splines $\bspl[\fs,\nak]{\*l,\*i}{p}$",
  #r"WF splines $\bspl[\wfs]{\*l,\*i}{p}$",
  #r"WFNAK splines $\bspl[\wfs,\nak]{\*l,\*i}{p}$",
  r"$\bspl{\*l,\*i}{p}$",
  r"$\bspl[\nak]{\*l,\*i}{p}$",
  r"$\bspl[\modified]{\*l,\*i}{p}$",
  r"$\bspl[\modified,\nak]{\*l,\*i}{p}$",
  r"$\bspl[\fs]{\*l,\*i}{p}$",
  r"$\bspl[\fs,\nak]{\*l,\*i}{p}$",
  r"$\bspl[\wfs]{\*l,\*i}{p}$",
  r"$\bspl[\wfs,\nak]{\*l,\*i}{p}$",
]

helper.plot.addCustomLegend(ax, (
  [{
    "label"  : basisNames[r],
    "ls"     : "-",
    "color"  : "C{}".format(r),
  } for r in range(len(basisNames))] +
  [{
    "label"  : "$p = {}$".format(p),
    "marker" : {1 : ".", 3 : "^", 5 : "v"}[p],
    "ms"     : (4.5 if p == 1 else 2.5),
    "ls"     : lineStyles[p],
    "color"  : "k",
  } for p in ps]
), ncol=4, loc="upper center", outside=True)

ax.set_axis_off()

fig.save()
