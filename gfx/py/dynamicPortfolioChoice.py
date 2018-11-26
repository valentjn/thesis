#!/usr/bin/python3
# number of output figures = 1

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.plot



def main():
  largeMargin = 0.5
  smallMargin = 0
  largeArrowWidth = 0.4
  smallArrowWidth = 0.2
  barWidth = 0.5
  barHeight = 1.8
  axisMarginX = 0.1
  axisMarginY = 0.1
  #choices = [
  #  1.0 * np.array([3, 2, 1.5, 1.5]),
  #  1.0 * np.array([3.1, 2.5, 2.0, 1.0]),
  #  0.24 * np.array([3.1, 2.5, 2.0, 1.0]),
  #  1.0 * np.array([0, 0, 0, 1.0]),
  #]
  choices = [
    1.0 * np.array([2.8, 0.5]),
    1.0 * np.array([3.05, 0.6]),
    0.52 * np.array([3.1, 1.0]),
    1.0 * np.array([0, 1.0]),
  ]
  T = len(choices)
  
  fig = Figure.create(figsize=(3.0, 1.7), scale=1.35, preamble=r"""
\contourlength{1pt}
  """)
  ax = fig.gca()
  
  x = 0
  
  for t in range(T):
    choice1, choice2 = choices[t], choices[(t+1)%T]
    c = np.sum(choices[0])
    choice1 *= barHeight / c
    choice2 *= barHeight / c
    choice1CumSum = np.hstack(([0], np.cumsum(choice1)))
    choice2CumSum = np.hstack(([0], np.cumsum(choice2)))
    tStr = (("T" if t == T-1 else "t+{}".format(t)) if t > 0 else "t")
    
    rectArgs = {"clip_on" : False, "ec" : "k"}
    #colors = ["C1", "C2", "C4", "C7"]
    colors = ["C1", "C2"]
    #labels = [r"$\bond_{{{}}}$", r"$\stock_{{{},1}}$",
    #          r"$\stock_{{{},2}}$", r"$\consume_{{{}}}$"]
    labels = [r"$\bond_{{{}}}$", r"$\consume_{{{}}}$"]
    contour = lambda x, c: r"\contour{{{}!60}}{{{}}}".format(c, x)
    
    y = choice1CumSum[-1]
    ax.add_artist(mpl.patches.Rectangle(
        (x, 0), barWidth, y, **rectArgs))
    ax.text(x+barWidth/2, y/2,
            contour(r"$\wealth_{{{}}}$".format(tStr), "C0"),
            ha="center", va="center")
    
    x += barWidth + smallMargin
    
    if t == T - 2:
      ax.plot(2 * [x-barWidth/2],
              [-axisMarginY-0.04, -axisMarginY+0.04], "k-", clip_on=False)
      ax.text(x-barWidth/2, -axisMarginY-0.08, "${}$".format(tStr),
              ha="center", va="top")
      ax.text(x+largeMargin, choice2CumSum[-1]/2, "$\cdots$",
              ha="center", va="center")
      ax.text(x+largeMargin, -axisMarginY-0.15, "$\cdots$",
              ha="center", va="center")
      x += 2 * largeMargin
      continue
    
    for y1, y2, label, color in zip(
          choice1CumSum[:-1], choice1CumSum[1:], labels, colors):
      if y2 - y1 > 0:
        ax.add_artist(mpl.patches.Rectangle(
            (x, y1), barWidth, y2 - y1, fc=color, **rectArgs))
        ax.text(x+barWidth/2, (y1+y2)/2, contour(label.format(tStr), color),
                ha="center", va="center")
    
    ax.plot(2 * [x-smallMargin/2],
            [-axisMarginY-0.04, -axisMarginY+0.04], "k-", clip_on=False)
    ax.text(x-smallMargin/2, -axisMarginY-0.08, "${}$".format(tStr),
            ha="center", va="top")
    
    y = barHeight
    helper.plot.plotArrow(ax, [x+barWidth/2, y2+0.1],
                          [x+barWidth/2, y2+0.35])
    ax.text(x+barWidth/2, y2+0.4,
            r"$\utilityfcn(\consume_{{{}}})$".format(tStr),
            ha="center", va="bottom")
    
    if t == T - 1:
      x += barWidth
      continue
    
    for y in [0, barHeight]:
      ax.plot([x - smallMargin, x], [y, y], "k--", clip_on=False)
    
    x += barWidth + largeMargin
    
    ax.plot([x - largeMargin, x], [0, 0], "k--", clip_on=False)
    ax.plot([x - largeMargin, x], [choice1CumSum[-2], choice2CumSum[-1]],
            "k--", clip_on=False)
    
    left = np.array([x - largeMargin, choice1CumSum[-2]/2])
    right = np.array([x, choice2CumSum[-1]/2])
    direction = right - left
    t = largeArrowWidth / largeMargin
    left  += (1-t)/2 * direction
    right -= (1-t)/2 * direction
    helper.plot.plotArrow(ax, left, right)
    
    for y in [0, choice2CumSum[-1]]:
      ax.plot([x - smallMargin, x], [y, y], "k--", clip_on=False)
  
  x += axisMarginX + 0.05
  helper.plot.plotArrow(ax, [-axisMarginX, -axisMarginY],
                        [x, -axisMarginY])
  
  ax.set_aspect("equal")
  ax.set_xlim(0, x)
  ax.set_ylim(-0.1, barHeight+0.1)
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
