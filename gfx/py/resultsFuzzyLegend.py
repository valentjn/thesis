#!/usr/bin/python3
# number of output figures = 1

from helper.figure import Figure
import helper.plot



lineNames = ["B-spl. surrogate", "Linear surrogate"]
markerStyles = [".", "^"]
lineStyles   = ["-", "--"]

fig = Figure.create(figsize=(5, 2))
ax = fig.gca()

functionNames = ["Bra02", "GoP", "Sch06", "Ack", "Alp02", "Sch22"]

lines = [{
    "label"  : r"\rlap{{{}}}".format(lineNames[r]),
    "marker" : markerStyles[r],
    "ms"     : (6 if markerStyles[r] == "." else 3),
    "ls"     : lineStyles[r],
    "color"  : "k",
  } for r in range(len(lineNames))]
lines = [(lines[r//2] if r % 2 == 0 else None)
         for r in range(2 * len(lines))]

helper.plot.addCustomLegend(ax, (
  [{
    "label"  : functionNames[r],
    "ls"     : "-",
    "color"  : "C{}".format(r),
  } for r in range(len(functionNames))] +
  lines
), ncol=6, loc="upper center", outside=True)

ax.set_axis_off()

fig.save()



lineNames = ["B-spl. (adap.)", "Linear (adap.)",
             "B-spl. (reg.)",  "Linear (reg.)"]
markerStyles = [".", "^",  ".", "^"]
lineStyles   = ["-", "--", "-", "--"]
faceColors = ["k", "k", "none", "none"]

fig = Figure.create(figsize=(6, 2))
ax = fig.gca()

functionNames = ["Ack", "Alp02", "Sch22"]

lines = [{
    "label"  : (r"\rlap{{{}}}".format(lineNames[r]) if r == 0 else
                lineNames[r]),
    "marker" : markerStyles[r],
    "ms"     : (1 if r < 2 else 2) * (6 if markerStyles[r] == "." else 3),
    "ls"     : lineStyles[r],
    "color"  : helper.plot.mixColors("k", (1 if r < 2 else 0.5),
                   helper.plot.mixColors("mittelblau", 0.1)),
    "mfc"    : faceColors[r],
  } for r in range(len(lineNames))]
lines = lines[:1] + [None] + lines[1:]

helper.plot.addCustomLegend(ax, (
  [{
    "label"  : functionNames[r],
    "ls"     : "-",
    "color"  : "C{}".format(r+3),
  } for r in range(len(functionNames))] + (2 * [None]) +
  lines
), ncol=5, loc="upper center", outside=True)

ax.set_axis_off()

fig.save()
