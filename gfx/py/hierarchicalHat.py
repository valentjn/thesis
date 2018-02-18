#!/usr/bin/python3
# number of output figures = 3

import numpy as np

import helper.basis
from helper.figure import Figure
import helper.grid

def plotSubspace(n, p, b, l, modified=False, showSubspaces=False):
  hInv = 2**l
  h = 1 / hInv
  I = (list(range(1, hInv, 2)) if l > 0 else [0, 1])
  plotI = I
  maxY = 0
  
  if modified:
    modifiedScale = 1.0
    superscript = r"{},\mathrm{{mod}}".format(p)
    spaceSuperscript = superscript
  else:
    modifiedScale = 1.0
    superscript = r"{}".format(p)
    spaceSuperscript = superscript
    #superscript = (r"\textcolor{white}{\mathsf{mod}}" if l == 0 else "")
    #spaceSuperscript = r"\textcolor{white}{\mathsf{mod}}" 
  
  for i in plotI:
    color = "C{}".format((i * 2**(n - l)) % 9)
    
    lb, ub = b.getSupport(l, i)
    xx = np.linspace(lb, ub, 100)
    yy = b.evaluate(l, i, xx)
    if (i == 1) or (i == hInv - 1): yy = [modifiedScale * y for y in yy]
    ax.plot(xx, yy, "-", clip_on=False, color=color)
    maxY = max(max(yy), maxY)
    
    j = np.argmax(yy)
    x, y = xx[j], yy[j]
    if modified:
      if l == 1:        x, y = 0.5, 1
      elif l == 2:
        if i == 1:      x, y = 0.32, 1
        if i == hInv-1: x, y = 0.73, 1
      elif l == 3:
        if i == 1:      x, y = 0.20, 1
        if i == hInv-1: x, y = 0.83, 1
    y *= 1.3
    ax.text(x, y, "$\\varphi_{{{},{}}}^{{{}}}$".format(l, i, superscript),
            color=color, ha="center")
  
  maxY *= 1.1
  color = "k"
  if modified: maxY = 2
  
  x = h * np.array(plotI)
  ax.plot(x, 0*x, ".", c=color, clip_on=False)
  
  if l > 0:
    x = np.hstack([np.linspace(h, (p-1)/2 * h, (p-1)/2),
                  np.linspace(1 - (p-1)/2 * h, 1 - h, (p-1)/2)])
    ax.plot(x, 0*x, "x", c=color, clip_on=False)
  
  if showSubspaces:
    ax.text(1.05, maxY / 2, "$W_{{{}}}^{{{}}}$".format(l, spaceSuperscript),
            ha="left", va="center", color=color)
  
  maxY /= 1.1
  ax.set_xlim((0, 1))
  ax.set_ylim((0, maxY))
  
  ax.set_xticks([h*i for i in range(hInv + 1)])
  
  ax.set_xticklabels([("$x_{{{},{}}}$".format(l, i) if i in I else "")
                      for i in range(hInv + 1)])
  
  yt = ([0, 1, 2] if modified else [0, 1])
  ax.set_yticks(yt)



n = 3
p = 1
b = helper.basis.HierarchicalBSpline(p)
tightLayout = {"h_pad" : 0.5, "pad" : 3.5}



fig = Figure.create(figsize=(3.3, 4.2), scale=1.0)

for l in range(n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(n, p, b, l, showSubspaces=True)

fig.save(tightLayout=tightLayout)



fig = Figure.create(figsize=(3.3, 2.0), scale=1.0)
ax = fig.gca()
c = [0.3, 0.8, 0.7, 0.7, 0.5, 0.9, 0.8, 0.7, 0.2]
hInv = 2**n
X = helper.grid.getCoordinates(l, list(range(hInv + 1)))
xtl = ["$x_{{{},{}}}$".format(l, i) for i in range(hInv + 1)]

for l in range(n+1):
  I = helper.grid.getHierarchicalIndices1D(l)
  
  for i in I:
    k = i * 2**(n-l)
    kl = (i+1) * 2**(n-l)
    kr = (i-1) * 2**(n-l)
    color = "C{}".format(k % 9)
    
    if l > 0:
      x = [X[kl], X[k], X[kr]]
      y = [c[kl], c[k], c[kr]]
    else:
      if i == 1: continue
      x = [X[0], X[-1]]
      y = [c[0], c[-1]]
    
    ax.plot(x, y, "-", color=color, clip_on=False)

line, = ax.plot(X, c, "k.--", clip_on=False)
line.set_dashes([3, 3])
ax.text(0.85, 0.85, r"$f_3$", color="k", ha="center", va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0, 0.9)
ax.set_xticks(X)
ax.set_xticklabels(xtl)
ax.set_yticks([0])

fig.save(tightLayout={"pad" : 2})



b = helper.basis.ModifiedHierarchicalBSpline(p)
fig = Figure.create(figsize=(3.3, 5.0), scale=1.0)

for l in range(1, n+1):
  ax = fig.add_subplot(n+1, 1, l+1)
  plotSubspace(n, p, b, l, modified=True)

fig.save(tightLayout=tightLayout)
