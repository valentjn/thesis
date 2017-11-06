#!/usr/bin/python3
# number of output figures = 1

import numpy as np

import helper.basis
import helper.figure
import helper.grid

d = 2
n = 3
p = 3
l = (1, 1)
i = (1, 1)

texts = {
  (0.5, 0.5) :
"""About the Church of B-Splines
by Julian Valentin""",
  (0.375, 0.5) :
"""From the B-ible of B-splines
("On Calculating with B-Splines"):
"In the beginning, there was the
B-spline. Then God came along...""",
  (0.5, 0.625) :
"""de Boor is the Pope of B-Splines
(or short B-ope) and Höllig is the
Cardinal of B-Splines.""",
  (0.625, 0.5) :
"""Disciples of the Church of
B-Splines call themselves Priests
of B-Splines (or short B-riests).""",
  (0.5, 0.75) :
"""B-ropagate the good B-spline news
all around the world: Stuttgart, Bonn
Frankfurt, Miami, Sydney, Canberra,
Los Angeles have already been
B-rainwashed...""",
  (0.5, 0.375) :
"""Good followers of the Church of
B-Splines will come to the B-Spline
Heavens: It starts with the 3rd
(Degree) Heaven, but very faithful
followers will reach the 5th Heaven,
7th Heaven, and so on.""",
  (0.5, 0.75) :
"""The ultimate goal of every Priest of
B-Splines is to reach the
Infinite Heaven of B-ell Curves!""",
  (0.25, 0.5) :
"""The B-Spline Hell is for all those
who call B-splines of degree 1
"hat functions" and for all those who
try to use even-degree B-splines
for sparse grids...""",
  (0.25, 0.75) :
"""The central hub for all B-ropagation
activities is bsplines.org!""",
  (0.5, 0.875) :
"""Don't think about what B-splines
can do for you, think about what you
can do for B-splines.""",
  (0.75, 0.5) :
"""In talks, always think about how to
sneak B-splines into the seemingly
unrelated topic.""",
  (0.125, 0.5) : "",
  (0.25, 0.25) : "",
  (0.5, 0.125) : "",
  (0.5, 0.25) : "",
  (0.75, 0.25) : "",
  (0.875, 0.5) : "",
  (0.75, 0.75) : "Thank you for reading!",
}

b = helper.basis.HierarchicalBSpline(p)
grid = helper.grid.RegularSparse()



fig = helper.figure.create()
ax = fig.add_subplot(111, projection="3d")



X, Xl, Xi = grid.generate(d, n)
N = X.shape[0]
Y = np.zeros((N,))

for k in range(N):
  x = X[k,:]
  Y[k] = np.prod([b.evaluate(l[t], i[t], X[k,t]) for t in range(d)])



xx1 = np.linspace(0, 1, 129)
xx2 = np.linspace(0, 1, 129)
XX1, XX2 = np.meshgrid(xx1, xx2)
XX = np.stack((XX1.flatten(), XX2.flatten()), axis=1)
NN = XX.shape[0]
YY = np.zeros((NN,))

for k in range(NN):
  YY[k] = np.prod([b.evaluate(l[t], i[t], XX[k,t]) for t in range(d)])

YY = np.reshape(YY, XX1.shape)

color1 = "k"
color2 = helper.figure.COLORS["anthrazit"]
text_color = (0.04, 0.04, 0.04)
text_size = 0.4

z = 0
ax.plot_surface(XX1, XX2, z, rstride=16, cstride=16, alpha=0, edgecolors=color2)
ax.plot(X[:,0], X[:,1], zs=z, marker="o", ls="", c=color2, zorder=-1)

ax.plot_surface(XX1, XX2, YY, rstride=16, cstride=16, alpha=0, edgecolors=color1)
ax.plot(X[:,0], X[:,1], zs=Y, marker="o", ls="", c=color1)

for pos, text in texts.items():
  for k in range(N):
    if (X[k,0] == pos[0]) and (X[k,1] == pos[1]):
      y = Y[k]
      break
  
  ax.text(pos[0], pos[1], y, text,
          ha="center", va="center", color=text_color, size=text_size)

ax.autoscale(tight=True)
ax.set_axis_off()

fig.save(1)
