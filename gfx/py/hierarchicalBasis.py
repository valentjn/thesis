#!/usr/bin/python3
# number of output figures = 16

import multiprocessing

import numpy as np

import helper.basis
from helper.figure import Figure
import helper.grid

def plotSubspace(ax, basis, l, n,
                 nodal=False, modified=False, clenshawCurtis=False,
                 notAKnot=False, natural=False, drawModifiedOnTop=False,
                 showSubspaces=False, whiteCC=False, showD=False,
                 basisSymbol=r"\varphi", superscript=None):
  if modified and (l == 0): return
  
  try:    p = basis.p
  except: p = None
  
  hInv = 2**l
  h = 1 / hInv
  I = (list(range(1, hInv, 2)) if l > 0 else [0, 1])
  plotI = (list(range(hInv + 1)) if nodal else I)
  maxY = 0
  
  if superscript is None: superscript = ("p" if p > 1 else "1")
  if modified:        superscript += r",\mathrm{{mod}}".format("p")
  if clenshawCurtis:  superscript += r",\mathrm{cc}"
  if notAKnot:        superscript += r",\mathrm{nak}"
  if superscript != "": superscript = r"^{{{}}}".format(superscript)
  
  if clenshawCurtis: pointSuperscript = r"^{\mathrm{cc}}"
  elif whiteCC:      pointSuperscript = r"^{\vphantom{\mathrm{cc}}}"
  else:              pointSuperscript = ""
  
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
      if l == 1:     x, y = 0.5, 1.02
      elif l == 2:
        if   i == 1: x, y = 0.32, 1
        elif i == 3: x, y = 0.73, 1
      elif l == 3:
        if   i == 1: x, y = 0.20, 1
        elif i == 3: x += 0.03
        elif i == 5: pass
        elif i == 7: x, y = 0.83, 1
    if notAKnot:
      if nodal:
        if   i == 2: x -= 0.03
        elif i == 5: x += 0.05
        elif i == 6: x += 0.03
      else:
        if ((not modified) and (not clenshawCurtis) and
            ("{fs}" not in superscript)):
          if (l == 3) and (i == 3): x += 0.03
          if (l == 3) and (i == 5): x -= 0.03
    ax.text(x, y, "${}_{{{},{}}}{}$".format(basisSymbol, l, i, superscript),
            color=color, ha="center", va="bottom")
  
  if showD:
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
    ax.plot(x, 0*x, "x", c=color, clip_on=False, ms=5)
  
  if showSubspaces:
    restriction = (r"|_{{D_{{{}}}^{{{}}}}}".format(n, "p") if showD else "")
    spaceSuperscript = superscript
    
    if nodal:
      ax.text(1.05, maxY / 2,
              "$V_{{{}}}{}{}$".format(l, spaceSuperscript, restriction),
              ha="left", va="center", color=color)
    else:
      x = (-0.05 if modified else -0.1)
      ax.text(x, maxY / 2,
              "$W_{{{}}}{}{}$".format(l, spaceSuperscript, restriction),
              ha="right", va="center", color=color)
  
  L = (hInv + 1) * [l]
  x = helper.grid.getCoordinates(L, list(range(hInv + 1)), distribution=distribution)
  ax.set_xticks(x)
  ax.set_xticklabels([("$x_{{{},{}}}{}$".format(l, i, pointSuperscript)
                       if i in plotI else "")
                      for i in range(hInv + 1)])
  
  ax.set_xlim(0, 1)
  
  ax.set_yticks([0, 1, 2])
  ax.set_ylim(0, maxY)



def plotNodalHatFunctions(q):
  fig = Figure.create(figsize=(3.5, 1.9), scale=1)
  basis = helper.basis.HierarchicalBSpline(1)
  ax = fig.gca()
  plotSubspace(ax, basis, n, n, nodal=True, showSubspaces=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalHatFunctions(q):
  fig = Figure.create(figsize=(3.2, 4.2), scale=1.0)
  basis = helper.basis.HierarchicalBSpline(1)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, showSubspaces=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotModifiedHierarchicalHatFunctions(q):
  fig = Figure.create(figsize=(3.2, 4.2), scale=1.0)
  basis = helper.basis.ModifiedHierarchicalBSpline(1)
  for l in range(1, n+1):
    ax = fig.add_subplot(n, 1, l)
    plotSubspace(ax, basis, l, n, modified=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotNodalUniformBSplines(q):
  fig = Figure.create(figsize=(3.2, 1.74), scale=1.0)
  basis = helper.basis.HierarchicalBSpline(p)
  ax = fig.gca()
  plotSubspace(ax, basis, n, n, nodal=True, showSubspaces=True, showD=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalUniformBSplines(q):
  fig = Figure.create(figsize=(3.2, 4.2), scale=1.0)
  basis = helper.basis.HierarchicalBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, showSubspaces=True, showD=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotModifiedHierarchicalBSplines(q):
  fig = Figure.create(figsize=(3.2, 4.2), scale=1.0)
  basis = helper.basis.ModifiedHierarchicalBSpline(p)
  for l in range(1, n+1):
    ax = fig.add_subplot(n, 1, l)
    plotSubspace(ax, basis, l, n, modified=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalClenshawCurtisBSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  basis = helper.basis.HierarchicalClenshawCurtisBSpline(p)
  basisModified = helper.basis.ModifiedHierarchicalClenshawCurtisBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, clenshawCurtis=True)
    plotSubspace(ax, basisModified, l, n, modified=True, clenshawCurtis=True,
                 drawModifiedOnTop=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotNodalNotAKnotBSplines(q):
  fig = Figure.create(figsize=(3.2, 1.74), scale=1)
  basis = helper.basis.HierarchicalNotAKnotBSpline(p)
  ax = fig.gca()
  plotSubspace(ax, basis, n, n, nodal=True, notAKnot=True, showSubspaces=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalNotAKnotBSplines(q):
  fig = Figure.create(figsize=(3.2, 4.2), scale=1.0)
  basis = helper.basis.HierarchicalNotAKnotBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, notAKnot=True, showSubspaces=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotModifiedHierarchicalNotAKnotBSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  basis = helper.basis.HierarchicalNotAKnotBSpline(p)
  basisModified = helper.basis.ModifiedHierarchicalNotAKnotBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, notAKnot=True, whiteCC=True)
    plotSubspace(ax, basisModified, l, n, modified=True, drawModifiedOnTop=True,
                 whiteCC=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalClenshawCurtisNotAKnotBSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  basis = helper.basis.HierarchicalClenshawCurtisNotAKnotBSpline(p)
  basisModified = helper.basis.ModifiedHierarchicalClenshawCurtisNotAKnotBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, clenshawCurtis=True, notAKnot=True)
    plotSubspace(ax, basisModified, l, n, modified=True, clenshawCurtis=True,
                 drawModifiedOnTop=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalNaturalBSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  basis = helper.basis.HierarchicalNaturalBSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, superscript=r"p,\mathrm{nat}")
  myTightLayout = dict(tightLayout)
  myTightLayout["h_pad"] = 0.5
  fig.save(tightLayout=myTightLayout, graphicsNumber=q+1)

def plotHierarchicalLagrangePolynomials(q):
  fig = Figure.create(figsize=(3.0, 4.0), scale=1.0)
  basis = helper.basis.HierarchicalLagrangePolynomial()
  n = 2
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, basisSymbol="L", superscript="")
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalFundamentalTransformedBSplines(q):
  fig = Figure.create(figsize=(3.2, 4.6), scale=1.0)
  origBasis = helper.basis.HierarchicalBSpline(p)
  basis = helper.basis.HierarchicalFundamentalTransformed(origBasis)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, superscript=r"p,\mathrm{hft}")
  myTightLayout = dict(tightLayout)
  myTightLayout["h_pad"] = 0.5
  fig.save(tightLayout=myTightLayout, graphicsNumber=q+1)

def plotHierarchicalFundamentalSplines(q):
  fig = Figure.create(figsize=(3.7, 5.2), scale=1.0)
  basis = helper.basis.HierarchicalFundamentalSpline(p)
  basisModified = helper.basis.ModifiedHierarchicalFundamentalSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, superscript=r"p,\mathrm{fs}")
    plotSubspace(ax, basisModified, l, n, superscript=r"p,\mathrm{fs}",
                 modified=True, drawModifiedOnTop=True)
  fig.save(tightLayout=tightLayout, graphicsNumber=q+1)

def plotHierarchicalFundamentalNotAKnotSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  origBasis = helper.basis.HierarchicalNotAKnotBSpline(p)
  basis = helper.basis.NodalFundamentalTransformed(origBasis)
  basis.p = p
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, notAKnot=True, superscript=r"p,\mathrm{fs}")
  myTightLayout = dict(tightLayout)
  myTightLayout["h_pad"] = 0.5
  fig.save(tightLayout=myTightLayout, graphicsNumber=q+1)

def plotHierarchicalWeaklyFundamentalSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  basis = helper.basis.HierarchicalWeaklyFundamentalSpline(p)
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, superscript=r"p,\mathrm{wfs}")
  myTightLayout = dict(tightLayout)
  myTightLayout["h_pad"] = 0.5
  fig.save(tightLayout=myTightLayout, graphicsNumber=q+1)

def plotHierarchicalWeaklyFundamentalNotAKnotSplines(q):
  fig = Figure.create(figsize=(3.7, 5.0), scale=1.0)
  origBasis = helper.basis.HierarchicalNotAKnotBSpline(p)
  basis = helper.basis.NodalWeaklyFundamentalTransformed(origBasis)
  basis.p = p
  for l in range(n+1):
    ax = fig.add_subplot(n+1, 1, l+1)
    plotSubspace(ax, basis, l, n, notAKnot=True, superscript=r"p,\mathrm{wfs}")
  myTightLayout = dict(tightLayout)
  myTightLayout["h_pad"] = 0.5
  fig.save(tightLayout=myTightLayout, graphicsNumber=q+1)



def callMethod(qAndMethod):
  q, method = qAndMethod
  method(q)

def main():
  methods = [
    plotNodalHatFunctions,
    plotHierarchicalHatFunctions,
    plotModifiedHierarchicalHatFunctions,
    plotNodalUniformBSplines,
    plotHierarchicalUniformBSplines,
    plotModifiedHierarchicalBSplines,
    plotHierarchicalClenshawCurtisBSplines,
    plotNodalNotAKnotBSplines,
    plotHierarchicalNotAKnotBSplines,
    plotModifiedHierarchicalNotAKnotBSplines,
    plotHierarchicalClenshawCurtisNotAKnotBSplines,
    plotHierarchicalNaturalBSplines,
    plotHierarchicalLagrangePolynomials,
    plotHierarchicalFundamentalTransformedBSplines,
    plotHierarchicalFundamentalSplines,
    plotHierarchicalFundamentalNotAKnotSplines,
    plotHierarchicalWeaklyFundamentalSplines,
    plotHierarchicalWeaklyFundamentalNotAKnotSplines,
  ]
  
  with multiprocessing.Pool() as pool:
    pool.map(callMethod, enumerate(methods))



if __name__ == "__main__":
  n = 3
  p = 3
  tightLayout = {"h_pad" : 0, "pad" : 3}
  main()
