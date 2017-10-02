#!/usr/bin/python3
# number of output figures = 2

import numpy as np

import helper.basis
import helper.figure

n = 3
p = 3
b = helper.basis.HierarchicalBSpline(p)



fig = helper.figure.create(figsize=(3,5))

for l in range(1, n+1):
  ax = fig.add_subplot(n, 1, l)
  h_inv = 2**l
  h = 1 / h_inv
  
  for i in range(1, h_inv, 2):
    xx = np.linspace(max((i - (p+1)/2) * h, 0),
                     min((i + (p+1)/2) * h, 1), 200)
    yy = b.evaluate(l, i, xx)
    ax.plot(xx, yy, "-")
  
  ax.set_xlim((0, 1))
  ax.set_ylim((0, 0.7))

fig.save(1)

fig = helper.figure.create()
ax = fig.gca()

for i in range(1, h_inv):
  xx = np.linspace(max((i - (p+1)/2) * h, 0),
                    min((i + (p+1)/2) * h, 1), 200)
  yy = b.evaluate(l, i, xx)
  ax.plot(xx, yy, "-")

ax.set_xlim((0, 1))
ax.set_ylim((0, 0.7))
fig.save(2)
