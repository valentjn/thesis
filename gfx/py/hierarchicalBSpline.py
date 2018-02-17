#!/usr/bin/python3
# number of output figures = 7

import numpy as np

import pysgpp

import helper.basis
from helper.figure import Figure
import helper.grid

def plotSubspace(basis, l, n, nodal=False, modified=False, clenshawCurtis=False,
                 notAKnot=False, natural=False,
                 drawModifiedOnTop=False, showSubspaces=False):
  if modified and (l == 0): return
  
  p = basis.p
  hInv = 2**l
  h = 1 / hInv
  I = (list(range(1, hInv, 2)) if l > 0 else [0, 1])
  plotI = (list(range(hInv + 1)) if nodal else I)
  maxY = 0
  
  superscript = "p"
  if modified:        superscript += r",\mathrm{{mod}}".format("p")
  if clenshawCurtis:  superscript += r",\mathrm{cc}"
  if notAKnot:        superscript += r",\mathrm{nak}"
  if natural:         superscript += r",\mathrm{nat}"
  
  pointSuperscript = (r"\mathrm{cc}" if clenshawCurtis else "")
  
  for i in plotI:
    if drawModifiedOnTop:
      if (l == 0) or ((l >= 3) and (1 < i < hInv - 1)): continue
      ls = "--"
    else:
      ls = "-"
    
    color = "C{}".format((i * 2**(n - l)) % 9)
    
    lb, ub = basis.getSupport(l, i)
    xx = np.linspace(lb, ub, 200)
    yy = basis.evaluate(l, i, xx)
    ax.plot(xx, yy, ls, clip_on=False, color=color)
    maxY = max(max(yy), maxY)
    
    if drawModifiedOnTop: continue
    
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
  
  if showSubspaces:
    D = [2**(-n) * (p-1)/2, 1 - 2**(-n) * (p-1)/2]
    ax.plot(D, [0, 0], "k-", clip_on=False, lw=2)
  
  maxY *= 1.1
  color = "k"
  
  distribution = ("clenshawCurtis" if clenshawCurtis else "uniform")
  x = helper.grid.getCoordinates(l, plotI, distribution=distribution)
  ax.plot(x, 0*x, ".", c=color, clip_on=False)
  
  if notAKnot and (l > 0):
    nakI = list(range(1, (p+1)//2)) + list(range(hInv - (p-1)//2, hInv))
    x = helper.grid.getCoordinates(l, nakI, distribution=distribution)
    ax.plot(x, 0*x, "x", c=color, clip_on=False)
  
  if showSubspaces:
    restriction = ("" if modified else r"|_{{D_{{{}}}^{{{}}}}}".format(n, "p"))
    spaceSuperscript = superscript
    
    if nodal:
      ax.text(1.05, maxY / 2,
              "$V_{{{}}}^{{{}}}{}$".format(l, spaceSuperscript, restriction),
              ha="left", va="center", color=color)
    else:
      x = (-0.05 if modified else -0.1)
      ax.text(x, maxY / 2,
              "$W_{{{}}}^{{{}}}{}$".format(l, spaceSuperscript, restriction),
              ha="right", va="center", color=color)
  
  L = (hInv + 1) * [l]
  x = helper.grid.getCoordinates(L, list(range(hInv + 1)), distribution=distribution)
  ax.set_xticks(x)
  ax.set_xticklabels([("$x_{{{},{}}}^{{{}}}$".format(l, i, pointSuperscript)
                       if i in I else "")
                      for i in range(hInv + 1)])
  
  ax.set_xlim(0, 1)
  
  #print(maxY)
  ax.set_yticks([0, 1, 2])
  ax.set_ylim(0, maxY)



n = 3
p = 3
basis = helper.basis.HierarchicalBSpline(p)
tightLayout = {"h_pad" : 0, "pad" : 3}



fig = Figure.create(figsize=(3.22, 1.74), scale=1)
ax = fig.gca()

plotSubspace(basis, n, n, nodal=True, showSubspaces=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.3, 4.2), scale=1.0)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(basis, l, n, showSubspaces=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.3, 4.2), scale=1.0)
basis = helper.basis.ModifiedHierarchicalBSpline(p)

for l in range(1, n+1):
  ax = fig.add_subplot(n, 1, l)
  plotSubspace(basis, l, n, modified=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.8, 5.0), scale=1.0)
basis = helper.basis.HierarchicalClenshawCurtisBSpline(p)
basisModified = helper.basis.ModifiedHierarchicalClenshawCurtisBSpline(p)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(basis, l, n, clenshawCurtis=True)
  plotSubspace(basisModified, l, n, modified=True, clenshawCurtis=True, drawModifiedOnTop=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.8, 5.0), scale=1.0)
basis = helper.basis.HierarchicalNotAKnotBSpline(p)
basisModified = helper.basis.ModifiedHierarchicalNotAKnotBSpline(p)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(basis, l, n, notAKnot=True)
  plotSubspace(basisModified, l, n, modified=True, drawModifiedOnTop=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.8, 5.0), scale=1.0)
basis = helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(p)
basisModified = helper.basis.ModifiedHierarchicalClenshawCurtisNotAKnotBSpline(p)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(basis, l, n, clenshawCurtis=True, notAKnot=True)
  plotSubspace(basisModified, l, n, modified=True, clenshawCurtis=True, drawModifiedOnTop=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.8, 5.0), scale=1.0)
basis = helper.basis.HierarchicalNaturalBSpline(p)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(basis, l, n, natural=True)

fig.save(tightLayout=tightLayout)
