#!/usr/bin/python3
# number of output figures = 3

import numpy as np

import helper.basis
from helper.figure import Figure

for p in [3, 5, 7]:
  fig = Figure.create(figsize=(2, 2), scale=1.15)
  ax = fig.gca()
  
  xx = np.linspace(0, 4.5, 361)
  
  for nu in range(3):
    basis = helper.basis.ModifiedHierarchicalFundamentalSpline(p, nu=nu)
    evalModParent = (lambda xx: basis.evaluate(2, 1, xx / 4) / 4**nu)
    yy = evalModParent(xx)
    ax.plot(xx, yy, "-", clip_on=False)
  
  ax.plot([1, 2, 3, 4], [1, 0, 0, 0], ".", clip_on=False, color="C0")
  
  ax.text(0.45, 1.8, r"$\varphi^{p,\mathrm{fs},\mathrm{mod}}$",
          color="C0", ha="left", va="bottom")
  ax.text(1.8, -0.8, r"$\tfrac{\mathop{}\!\mathrm{d}}{\mathop{}\!\mathrm{d}x} "
                  r"\varphi^{p,\mathrm{fs},\mathrm{mod}}$",
          color="C1", ha="left", va="top")
  ax.text(2.45, 1, r"$\tfrac{\mathop{}\!\mathrm{d}^2}{\mathop{}\!\mathrm{d}x^2} "
                  r"\varphi^{p,\mathrm{fs},\mathrm{mod}}$",
          color="C2", ha="left", va="bottom")
  
  ax.set_xticks(list(range(0, 5)))
  ax.set_xticklabels([""] + [str(k) for k in range(1, 5)])
  ax.set_xlim(0, 4.5)
  
  ax.set_ylim(-1.3, 2.3)
  
  ax.spines["bottom"].set_position("zero")
  ax.set_aspect("equal")
  
  fig.save()
