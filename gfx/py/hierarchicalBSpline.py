#!/usr/bin/python3
# number of output figures = 4

import numpy as np

import pysgpp

import helper.basis
from helper.figure import Figure
import helper.grid

def plotSubspace(n, p, b, l, nodal=False, modified=False, clenshawCurtis=False):
  hInv = 2**l
  h = 1 / hInv
  I = (list(range(1, hInv, 2)) if l > 0 else [0, 1])
  plotI = (list(range(hInv + 1)) if nodal else I)
  maxY = 0
  
  if modified:
    modifiedScale = 1.0
    superscript = r"{},\mathrm{{mod}}".format("p")
  else:
    modifiedScale = 1.0
    superscript = r"{}".format("p")
  
  if clenshawCurtis:
    superscript += r",\mathrm{cc}"
    pointSuperscript = r"\mathrm{cc}"
  else:
    pointSuperscript = ""
  
  restriction = ("" if modified else r"|_{{D_{{{}}}^{{{}}}}}".format(n, "p"))
  spaceSuperscript = superscript
  
  for i in plotI:
    if clenshawCurtis and modified:
      if (l == 0) or ((l >= 3) and (1 < i < hInv - 1)): continue
      ls = "--"
    else:
      ls = "-"
    
    color = "C{}".format((i * 2**(n - l)) % 9)
    
    lb, ub = helper.basis.getSupport(b, l, i)
    xx = np.linspace(lb, ub, 200)
    yy = b.evaluate(l, i, xx)
    if (i == 1) or (i == hInv - 1): yy = [modifiedScale * y for y in yy]
    ax.plot(xx, yy, ls, clip_on=False, color=color)
    maxY = max(max(yy), maxY)
    
    if clenshawCurtis and modified: continue
    
    j = np.argmax(yy)
    x, y = xx[j], yy[j] * 1.05
    if modified:
      if l == 1:        x, y = 0.5, 1.02
      elif l == 2:
        if i == 1:      x, y = 0.32, 1
        if i == hInv-1: x, y = 0.73, 1
      elif l == 3:
        if i == 1:      x, y = 0.20, 1
        if i == hInv-1: x, y = 0.83, 1
    ax.text(x, y, "$\\varphi_{{{},{}}}^{{{}}}$".format(l, i, superscript),
            color=color, ha="center", va="bottom")
  
  if (not modified) and (not clenshawCurtis):
    D = [2**(-n) * (p-1)/2, 1 - 2**(-n) * (p-1)/2]
    ax.plot(D, [0, 0], "k-", clip_on=False, lw=2)
  
  if modified: maxY = 2
  maxY *= 1.1
  color = "k"
  
  L = l * np.ones_like(plotI)
  distribution = ("clenshawCurtis" if clenshawCurtis else "uniform")
  x = helper.grid.getCoordinates(L, plotI, distribution=distribution)
  ax.plot(x, 0*x, ".", c=color, clip_on=False)
  
  #if l > 0:
  #  x = np.hstack([np.linspace(h, (p-1)/2 * h, (p-1)/2),
  #                np.linspace(1 - (p-1)/2 * h, 1 - h, (p-1)/2)])
  #  ax.plot(x, 0*x, "x", c=color, clip_on=False)
  
  if not clenshawCurtis:
    if nodal:
      ax.text(1.05, maxY / 2,
              "$V_{{{}}}^{{{}}}{}$".format(l, spaceSuperscript, restriction),
              ha="left", va="center", color=color)
    else:
      x = (-0.05 if modified else -0.1)
      ax.text(x, maxY / 2,
              "$W_{{{}}}^{{{}}}{}$".format(l, spaceSuperscript, restriction),
              ha="right", va="center", color=color)
  
  ax.set_xlim((0, 1))
  ax.set_ylim((0, maxY))
  
  L = (hInv + 1) * [l]
  x = helper.grid.getCoordinates(L, list(range(hInv + 1)), distribution=distribution)
  ax.set_xticks(x)
  ax.set_xticklabels([("$x_{{{},{}}}^{{{}}}$".format(l, i, pointSuperscript)
                       if i in I else "")
                      for i in range(hInv + 1)])
  
  if modified: ax.set_yticks([0, 2])
  else:        ax.set_yticks([0])



n = 3
p = 3
b = helper.basis.HierarchicalBSpline(p)
tightLayout = {"h_pad" : 0, "pad" : 3}



fig = Figure.create(figsize=(3.22, 1.74), scale=1)
ax = fig.gca()

plotSubspace(n, p, b, n, nodal=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.3, 4.2), scale=1.0)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(n, p, b, l)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.3, 4.2), scale=1.0)
b = helper.basis.ModifiedHierarchicalBSpline(p)

for l in range(1, n+1):
  ax = fig.add_subplot(n, 1, l)
  plotSubspace(n, p, b, l, modified=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.8, 5.0), scale=1.0)
b = helper.basis.HierarchicalClenshawCurtisBSpline(p)
bMod = helper.basis.ModifiedHierarchicalBSpline(p, b=b)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(n, p, b, l, clenshawCurtis=True)
  plotSubspace(n, p, bMod, l, clenshawCurtis=True, modified=True)

fig.save(tightLayout=tightLayout)
