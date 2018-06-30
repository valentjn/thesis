#!/usr/bin/python3
# number of output figures = 3

import numpy as np

from helper.figure import Figure



for q in range(3):
  width = (2 if q < 2 else 2.5)
  fig = Figure.create(figsize=(width, 2), scale=1)
  ax = fig.gca()
  
  alpha = 0.4
  xAlpha = [1.4, 5.2, 5.8, 7.6]
  xAlpha0 = [0, 1.9, 2.1, 3.9, 4.1, 6.9, 7.1, 8]
  cropHeight = 0.008
  c = lambda yy: np.maximum(yy, cropHeight)
  
  if q == 0:
    ax.plot([0, 1, 2, 3,   4, 5.5,  7, 8, 9],
            c([0, 0, 1, 0.5, 1, 0.25, 1, 0, 0]), "-",
            clip_on=False, color="C0")
    ax.text(5.3, 0.75, r"$\mu_{\tilde{x}}$",
            color="C0", ha="center", va="center")
  elif q == 1:
    #ax.plot([3, 3], [0, 1], "-", clip_on=False, color=3*[0.7])
    #ax.plot([5, 5], [0, 1], "-", clip_on=False, color=3*[0.7])
    
    xx = np.linspace(0.5, 3, 200)
    
    # f(x) = ax^2 + bx + c
    # f'(x) = 2ax + b
    # 
    # f(0.5) = 0, f(3) = 1, f'(3) = 0.1
    # 
    # 0.25a + 0.5b + c = 0
    # 9a + 3b + c = 1
    # 6a + b = 0.1
    yy = -0.12 * xx**2 + 0.82 * xx - 0.38
    
    xx = np.hstack(([-0.5, 0.5], xx, [3, 5, 5.8, 6.8, 7.2]))
    yy = np.hstack(([0, 0], yy, [1, 1, 0.75, 0.7, 0.5]))
    ax.plot(xx, c(yy), "-", clip_on=False, color="C0")
    ax.plot([7.2, 8, 9], c([0.3, 0, 0]), "-", clip_on=False, color="C0")
    ax.plot(7.2, 0.5, "o", fillstyle="none", ms=5, color="C0")
    ax.plot(7.2, 0.3, ".", ms=8, color="C0")
    ax.text(1.2, 0.8, r"$\mu_{\tilde{x}}$", color="C0", ha="center", va="center")
  else:
    ax.plot([0, 0.5, 2, 3, 9], c([0, 0, 1, 0, 0]), "-", clip_on=False)
    ax.plot([0, 1.5, 3, 4, 6.5, 9], c([0, 0, 1, 1, 0, 0]), "-", clip_on=False)
    mu, sigma = 5.5, 1
    xx = np.linspace(0, 9, 201)
    yy = np.exp(-(xx - mu)**2 / (2*sigma**2))
    ax.plot(xx, c(yy), "-", clip_on=False)
    yy[yy < 0.2] = 0
    ax.plot(xx, c(yy), "--", clip_on=False, dashes=(3, 3))
    ax.text(1.45, 0.8,  "TFN",  ha="right", va="center", color="C0")
    ax.text(3,    0.8,  "TFI",  ha="left",  va="center", color="C1")
    ax.text(6.5,  0.8,  "GFN",  ha="left",  va="center", color="C2")
    ax.text(6.7,  0.68, "QGFN", ha="left",  va="center", color="C3")
  
  if q == 0:
    ax.plot([0, 8], [alpha, alpha], "-", clip_on=False, color=3*[0.7])
    ax.text(4, alpha - 0.04, r"$(\tilde{x})_\alpha$", color="C1",
            ha="center", va="top")
    
    for k in range(len(xAlpha) // 2):
      ax.plot(
          [xAlpha[2*k]-0.05, xAlpha[2*k], xAlpha[2*k], xAlpha[2*k+1]-0.05],
          4 * [alpha], "-", color="C1")
  
  ax.set_xlim([-0.5, 9] if q == 1 else [0, 9])
  ax.set_ylim([0, 1])
  ax.set_xticks([])
  
  if q == 0:
    ax.set_yticks([cropHeight, alpha, 1])
    ax.set_yticklabels(["$0$", r"$\alpha$", "$1$"])
  else:
    ax.set_yticks([cropHeight, 1])
    ax.set_yticklabels(["$0$", r"\textcolor{white}{$\alpha$}\llap{$1$}"])
  
  fig.save()
