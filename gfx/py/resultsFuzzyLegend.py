#!/usr/bin/python3
# number of output figures = 1

from helper.figure import Figure
import helper.plot



lineNames = ["B-spl. surrogate", "Linear surrogate"]
markerStyles = [".", "^",  "v"]
lineStyles   = ["-", "--", ":"]



fig = Figure.create(figsize=(5, 2))
ax = fig.gca()

functionNames = ["Bra02", "GoP", "Sch06", "Ack", "Alp02", "Sch22"]

lines = [{
    "label"  : r"\rlap{{{}}}".format(lineNames[r]),
    "marker" : markerStyles[r],
    "ms"     : (6 if r == 0 else 3),
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
