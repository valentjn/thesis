#!/usr/bin/python3
# number of output figures = 1
# dependencies = SG++

import matplotlib as mpl
import numpy as np

import pysgpp

from helper.figure import Figure

class BilinearFunction(pysgpp.OptScalarFunction):
  def __init__(self):
    super(BilinearFunction, self).__init__(2)
  
  def eval(self, *args):
    if len(args) == 1:
      x, = args
      return (8.0 * x[0]) * (8.0 * x[1]) / 10.0
    else:
      X, Y = args
      x = pysgpp.DataVector(X.getNcols())
      Y.resize(X.getNrows())
      
      for k in range(X.getNrows()):
        X.getRow(k, x)
        Y.set(k, self.eval(x))

def dv2np(x):
  return np.array([x[k] for k in range(x.getSize())])



d = 2

figureMarginLeft = 0.2
figureMarginRight = 0.2
figureMarginTop = 0.2
figureMarginBottom = 0.2
plotSize = 1
plotMargin = 0.2
colorbarMarginLeft = 0.1
colorbarMarginRight = 0.2
colorbarWidth = 0.2

figureScale = 1.45

figureWidth = (3 * plotSize + plotMargin + colorbarMarginLeft +
               colorbarWidth + colorbarMarginRight +
               figureMarginLeft + figureMarginRight)
figureHeight = (2 * plotSize + plotMargin + figureMarginTop +
                figureMarginBottom)



pysgpp.OptPrinter.getInstance().setVerbosity(-1)
pysgpp.OptRNG.getInstance().setSeed(1)
pysgpp.omp_set_num_threads(4)

f = BilinearFunction()

x0Fuzzy = pysgpp.OptTriangularFuzzyInterval(0.625, 0.75, 0.25, 0.125)
x1Fuzzy = pysgpp.OptTriangularFuzzyInterval(0.45, 0.55, 0.4, 0.4)
xFuzzy = pysgpp.OptFuzzyIntervalVector([x0Fuzzy, x1Fuzzy])

numberOfAlphaSegments = 4
numberOfAlphaLevels = numberOfAlphaSegments + 1

# extension principle with exact objective function
print("Applying exact extension principle (via optimization)...")
optimizer = pysgpp.OptMultiStart(f, 10000, 100)
extensionPrinciple = pysgpp.OptFuzzyExtensionPrincipleViaOptimization(
  optimizer, numberOfAlphaSegments)
yFuzzy = extensionPrinciple.apply(xFuzzy)
print("Done.")

yFuzzy = pysgpp.OptInterpolatedFuzzyInterval.tryDowncast(yFuzzy)

alphaLevels = dv2np(extensionPrinciple.getAlphaLevels())
allLowerBounds = extensionPrinciple.getOptimizationDomainsLowerBounds()
allUpperBounds = extensionPrinciple.getOptimizationDomainsUpperBounds()
minimumPoints = extensionPrinciple.getMinimumPoints()
minimumValues = dv2np(extensionPrinciple.getMinimumValues())
maximumPoints = extensionPrinciple.getMaximumPoints()
maximumValues = dv2np(extensionPrinciple.getMaximumValues())

#print(yFuzzy.getXData())
#print(yFuzzy.getAlphaData())



colorMu = "C0"
colorAlphaCut = "C1"
colorMinPoints = "C3"
colorMaxPoints = "C4"
colorOptimizationBox = "k"
colorSpine = "k"
colormap = mpl.cm.viridis

fig = Figure.create(figsize=(figureWidth, figureHeight), scale=figureScale,
                    fontSize=9, facecolor="none", preamble=r"""
\usepackage{{contour}}
\contourlength{{1.5pt}}
""")

left = (figureMarginLeft + plotSize + plotMargin) / figureWidth
bottom = figureMarginBottom / figureHeight
width = plotSize / figureWidth
height = plotSize / figureHeight
ax = fig.add_axes([left, bottom, width, height])
for spine in ax.spines.values(): spine.set_color(colorSpine)

nn = 65
xx0 = np.linspace(0, 1, nn)
xx1 = np.linspace(0, 1, nn)
[XX0, XX1] = np.meshgrid(xx0, xx1)
XX = pysgpp.DataMatrix(np.stack((XX0.flatten(), XX1.flatten()), axis=1))
NN = XX.getNrows()

YY = pysgpp.DataVector(NN)
f.eval(XX, YY)

YY = np.reshape(dv2np(YY), XX0.shape)
contourLevels = np.hstack(([0, 6.4], minimumValues, maximumValues))
contourLevels.sort()
ax.contour(XX0, XX1, YY, levels=contourLevels, cmap=colormap,
           vmin=min(contourLevels), vmax=max(contourLevels))

ax.text(0.05, 0.05, r"\contour{mittelblau!10}{$\objfun$}", size=16,
        ha="left", va="bottom", zorder=100)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])

x0Min, x0Max, x1Min, x1Max = [], [], [], []
numberOfAlphaLevelsToPlot = len(alphaLevels)

for j in range(numberOfAlphaLevelsToPlot):
  x0Domain = ((allUpperBounds[j][0] - allLowerBounds[j][0]) *
              np.array([0, 1, 1, 0, 0]) +
              allLowerBounds[j][0])
  x1Domain = ((allUpperBounds[j][1] - allLowerBounds[j][1]) *
              np.array([0, 0, 1, 1, 0]) +
              allLowerBounds[j][1])
  #print("[{}, {}] x [{}, {}]".format(
  #  allLowerBounds[j][0], allUpperBounds[j][0],
  #  allLowerBounds[j][1], allUpperBounds[j][1]))
  ax.plot(x0Domain, x1Domain, "-", c=colorOptimizationBox)
  
  x0Min.append(minimumPoints[j][0])
  x1Min.append(minimumPoints[j][1])
  x0Max.append(maximumPoints[j][0])
  x1Max.append(maximumPoints[j][1])

minHandle = ax.scatter(x0Min, x1Min, c=colorMinPoints, s=12)
maxHandle = ax.scatter(x0Max, x1Max, c=colorMaxPoints, s=12)
ax.legend([minHandle, maxHandle], ["min", "max"], ncol=2, borderpad=0.2,
          handletextpad=-0.5, columnspacing=0,
          loc=8, bbox_to_anchor=(0.48, -0.15), borderaxespad=0,
          edgecolor="none", facecolor="none")



left = (figureMarginLeft + 2 * plotSize +
        plotMargin + colorbarMarginLeft) / figureWidth
bottom = figureMarginBottom / figureHeight
width = colorbarWidth / figureWidth
height = plotSize / figureHeight
ax = fig.add_axes([left, bottom, width, height])
norm = mpl.colors.Normalize(vmin=min(contourLevels), vmax=max(contourLevels))
colorbar = mpl.colorbar.ColorbarBase(
    ax, cmap=colormap, norm=norm, ticks=list(range(7)),
    spacing="proportional")
colorbar.outline.set_edgecolor(colorSpine)



membershipFunctionClipping = 0.005 * figureScale
grayStyle = {"ls" : "--", "color" : 3*[0.5]}

clip = lambda y: np.maximum(np.minimum(y, 1 - membershipFunctionClipping),
                            membershipFunctionClipping)

for r in range(3):
  if r == 0:
    left = (figureMarginLeft + plotSize + plotMargin) / figureWidth
    bottom = (figureMarginBottom + plotSize + plotMargin) / figureHeight
    curFuzzy = x0Fuzzy
    curFuzzyName = r"\fuzzy{x}_1"
    curFuzzyBounds = (0, 1)
    s = lambda x, y: (x, clip(y))
  elif r == 1:
    left = figureMarginLeft / figureWidth
    bottom = figureMarginBottom / figureHeight
    curFuzzy = x1Fuzzy
    curFuzzyName = r"\fuzzy{x}_2"
    curFuzzyBounds = (0, 1)
    s = lambda x, y: (clip(y), x)
  else:
    left = (figureMarginLeft + 2 * plotSize + plotMargin + colorbarMarginLeft +
            colorbarWidth + colorbarMarginRight) / figureWidth
    bottom = figureMarginBottom / figureHeight
    curFuzzy = yFuzzy
    curFuzzyName = r"\fuzzy{y}"
    curFuzzyBounds = (min(contourLevels), max(contourLevels))
    s = lambda x, y: (clip(y), x)
  
  width = plotSize / figureWidth
  height = plotSize / figureHeight
  ax = fig.add_axes([left, bottom, width, height])
  for spine in ax.spines.values(): spine.set_color(colorSpine)
  
  xx = np.linspace(*curFuzzyBounds, 200)
  yy = np.array([curFuzzy.evaluateMembershipFunction(x) for x in xx])
  yy = np.minimum(yy, 1 - membershipFunctionClipping)
  yy = np.maximum(yy, membershipFunctionClipping)
  
  if (r < 2) or (r == 2):
    ax.plot(*s(xx, yy), "-", clip_on=False, c=colorMu)
  
  if r == 0:
    textPos = (0, 1)
  elif r == 1:
    textPos = (1, 1)
  else:
    textPos = (1, curFuzzyBounds[1])
  
  textPos = (textPos[0] + (-1 if r > 0 else 1) * 0.05, 0.95 * textPos[1])
  textAlign = {"ha" : ("left" if r < 2 else "right"), "va" : "top"}
  ax.text(*textPos,
      (r"\textcolor{{C0}}{{$\mu_{{{0}}}$}}, "
       r"\textcolor{{C1}}{{$({0})_\alpha$}}").format(curFuzzyName),
      **textAlign)
  
  if r == 0:
    ax.text(*s(-0.25, 0.5), "${}$".format(curFuzzyName),
            size=16, ha="right", va="center")
  elif r == 1:
    ax.text(*s(1.05, 0.5), "${}$".format(curFuzzyName),
            size=16, ha="center", va="bottom")
  else:
    ax.text(*s(curFuzzyBounds[1] * 1.05, 0.5), "${}$".format(curFuzzyName),
            size=16, ha="center", va="bottom")
  
  for j in range(numberOfAlphaLevelsToPlot):
    alphaLevel = alphaLevels[j]
    confIntervalLB = curFuzzy.evaluateConfidenceIntervalLowerBound(alphaLevel)
    confIntervalUB = curFuzzy.evaluateConfidenceIntervalUpperBound(alphaLevel)
    
    if j == 2:
      ax.plot(*s([0, confIntervalLB], [alphaLevel, alphaLevel]), **grayStyle)
    
    ax.plot(*s([confIntervalLB, confIntervalUB],
               [alphaLevel, alphaLevel]), ".-", c=colorAlphaCut)
    
    if j == 2:
      if r == 0:
        s2 = lambda x, y: (x, y - 1 - plotMargin / plotSize)
        p2LB = s2(allLowerBounds[j][0], allUpperBounds[j][1])
        p2UB = s2(allUpperBounds[j][0], allUpperBounds[j][1])
      elif r == 1:
        s2 = lambda x, y: (-x - plotMargin / plotSize, y)
        p2LB = s2(allLowerBounds[j][0], allLowerBounds[j][1])
        p2UB = s2(allLowerBounds[j][0], allUpperBounds[j][1])
      else:
        s2 = lambda x, y: (x - 1 - (colorbarMarginLeft + colorbarWidth +
                                    colorbarMarginRight) / plotSize, y)
        p2LB = s2(1, confIntervalLB)
        p2UB = s2(1, confIntervalUB)
      
      p1LB = s(confIntervalLB, alphaLevel)
      p1UB = s(confIntervalUB, alphaLevel)
      
      ax.plot(*list(zip(p1LB, p2LB)), clip_on=False, **grayStyle)
      ax.plot(*list(zip(p1UB, p2UB)), clip_on=False, **grayStyle)
  
  if r == 0:
    ax.set_xlim(*curFuzzyBounds)
    ax.set_ylim(0, 1)
    ax.set_xticks([0, 1])
    ax.set_yticks(alphaLevels)
    ax.set_yticklabels(["{:g}".format(x) for x in alphaLevels])
  else:
    ax.set_xlim(0, 1)
    ax.set_ylim(*curFuzzyBounds)
    ax.set_xticks(alphaLevels)
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["{:g}".format(x) for x in alphaLevels])
  
  if r == 2:
    ax.set_yticks(list(range(7)))
    ax.set_yticklabels(["" for x in ax.get_yticks()])
  
  if r == 1:
    ax.invert_xaxis()



fig.save(tightLayout=False, hideSpines=False)
