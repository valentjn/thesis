#!/usr/bin/python3
# number of output figures = 3

import numpy as np

from helper.figure import Figure
import helper.plot



def selectData(data, model, NMax):
  if data[model].size == 0: return 3 * [np.array([])]
  Ns, complianceApprs, complianceReals = data[model].T
  K = (Ns <= NMax)
  Ns = Ns[K]
  complianceApprs = complianceApprs[K]
  complianceReals = complianceReals[K]
  return Ns, complianceApprs, complianceReals

def main():
  data = {
    # ids = 720:739
    "cross" : np.array([
      (    49, 74.935233, 75.345620),
      (    61, 75.723657, 75.992673),
      (   109, 75.520636, 75.719787),
      (   231, 75.014781, 75.067794),
      (   299, 75.166566, 75.218740),
      (   477, 75.610664, 75.619868),
      (   785, 75.664990, 75.670996),
      (  1320, 75.930496, 75.933535),
      (  1987, 75.937185, 75.933732),
      (  3160, 75.079648, 75.077130),
      (  4997, 75.082615, 75.081772),
      (  7227, 75.074925, 75.074818),
      ( 10197, 74.974100, 74.974063),
      ( 14338, 74.973774, 74.973771),
      ( 21197, 75.183181, 75.185230),
      ( 29287, 75.106003, 75.106287),
      ( 39637, 76.037957, 76.038316),
      ( 54063, 75.042286, 75.042434),
      ( 74647, 75.039336, 75.039504),
      (109705, 74.973638, 74.973814)]),
    # ids = 750:760
    "framedCross" : np.array([
      (  361, 68.156315, 71.649763),
      (  398, 66.118012, 71.229265),
      ( 1364, 68.315331, 71.358734),
      ( 1787, 69.253265, 71.175666),
      ( 2413, 68.739374, 71.045458),
      ( 3585, 68.499258, 71.339686),
      ( 5487, 68.655327, 70.837648),
      ( 7377, 68.818690, 70.620592),
      (10502, 69.370388, 70.765719),
      (15525, 69.771498, 70.607431),
      (24307, 69.831259, 70.581350)]),
    # ids = 770:789
    "shearedCross" : np.array([
      (    81, 67.771177, 69.657442),
      (   129, 67.879234, 69.762924),
      (   165, 67.775287, 69.685372),
      (   448, 67.393314, 67.635797),
      (   807, 67.466213, 67.611968),
      (  1288, 67.712275, 67.768597),
      (  1926, 67.632001, 67.676240),
      (  3075, 67.643523, 67.667251),
      (  3958, 67.629523, 67.645602),
      (  5673, 67.715135, 67.730637),
      (  7647, 67.945400, 67.963278),
      ( 10723, 67.804206, 67.809414),
      ( 14464, 68.112317, 68.116193),
      ( 19669, 68.079534, 68.082777),
      ( 27652, 68.262504, 68.262435),
      ( 37005, 68.162664, 68.160912),
      ( 47689, 68.069078, 68.067204),
      ( 62376, 67.727316, 67.726562),
      ( 96422, 68.211481, 68.211418),
      (119518, 68.024424, 68.019930)]),
    # ids = 800:810
    "shearedFramedCross" : np.array([
      ( 1393, 65.149931, 69.363815),
      ( 1405, 65.502154, 69.182327),
      ( 1415, 65.483178, 69.334167),
      ( 1485, 64.457931, 69.540379),
      ( 1565, 65.523080, 69.611603),
      ( 1750, 64.560332, 69.489528),
      ( 2325, 63.369471, 69.585239),
      ( 5077, 63.201168, 69.131705),
      (10694, 65.201204, 68.602115),
      (17699, 65.585861, 68.477155),
      (29945, 65.582794, 67.956924)]),
    # ids = 820:831
    "cross3D" : np.array([
      ( 247, 249.132390, 252.116288),
      ( 259, 248.335435, 251.003219),
      ( 361, 247.617688, 249.698244),
      ( 511, 247.477562, 249.152016),
      ( 801, 247.621274, 248.169177),
      ( 999, 247.970263, 249.675624),
      (1650, 249.331196, 249.732645),
      (2379, 248.771911, 249.427211),
      (3019, 248.288778, 248.306970),
      (4788, 247.403886, 247.512642),
      (6627, 247.241640, 247.386703),
      (9207, 246.985843, 247.098534)]),
    # ids = 840:848
    "shearedCross3D" : np.array([
      ( 1405, 159.054602, 100),
      ( 1525, 141.746173, 100),
      ( 1597, 147.247356, 100),
      ( 1777, 147.448362, 159.438932),
      ( 2139, 162.575755, 168.403499),
      ( 3089, 158.539807, 164.896813),
      ( 4390, 153.099371, 100),
      ( 7438, 146.349278, 151.982760),
      (15389, 163.812531, 167.569728)]),
  }
  
  models = [["cross"], ["framedCross", "shearedCross", "shearedFramedCross",
                        "cross3D", "shearedCross3D"]]
  
  for q in range(2):
    fig = Figure.create(figsize=((3.35, 2.3) if q == 0 else (3.05, 2.3)))
    NMax = (20000 if q == 0 else 30000)
    
    if q == 0:
      ax1 = fig.gca()
      
      for model in models[q]:
        Ns, complianceApprs, complianceReals = selectData(data, model, NMax)
        ax1.plot(Ns, complianceApprs, "^--", color="C0", ms=3)
        ax1.plot(Ns, complianceReals, "v-", color="C0", ms=3)
      
      ax1.set_xscale("log")
      ax1.spines["top"].set_visible(False)
      ax1.spines["right"].set_visible(False)
      ax1.set_ylabel("Compliance value")
      
      ax1.spines["left"].set_color("C0")
      ax1.yaxis.label.set_color("C0")
      ax1.tick_params(axis="y", colors="C0")
      
      ax2 = ax1.twinx()
      
      ax2.spines["right"].set_color("C1")
      ax2.yaxis.label.set_color("C1")
      ax2.tick_params(axis="y", which="both", colors="C1")
    else:
      ax2 = fig.gca()
    
    for j, model in enumerate(models[q]):
      Ns, complianceApprs, complianceReals = selectData(data, model, NMax)
      color = "C{}".format(j+q+1)
      ax2.plot(Ns, np.abs(complianceReals - complianceApprs), ".-",
               color=color)
    
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    
    trafo = helper.plot.getTransformationFromUnitCoordinates(ax2)
    ax2.text(*trafo((0.73 if q == 0 else 0.95), -0.06), r"$\ngp$",
             ha="center", va="top")
    
    if q > 0:
      ax2.set_yticks([1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1])
      ax2.set_ylabel("Optimality-interpolation gap", labelpad=8)
    
    ax2.spines["top"].set_visible(False)
    
    if q == 0:
      ax2.spines["left"].set_visible(False)
      ax2.spines["bottom"].set_visible(False)
    else:
      ax2.spines["right"].set_visible(False)
    
    fig.save(hideSpines=False)
  
  
  
  fig = Figure.create(figsize=(6, 2))
  ax = fig.gca()
  
  helper.plot.addCustomLegend(ax, [
      {
        "label"  : r"$\compliance[\opt,\ast]$",
        "ls"     : "-",
        "marker" : "v",
        "color"  : "C0",
        "ms"     : 3,
      },
      {
        "label"  : r"$\complianceintp[\opt,\ast]$",
        "ls"     : "--",
        "marker" : "^",
        "color"  : "C0",
        "ms"     : 3,
      },
      None, None, None, None,
      {
        "label"  : "2D-C",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C1",
      },
      {
        "label"  : "2D-FC",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C2",
      },
      {
        "label"  : "2D-SC",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C3",
      },
      {
        "label"  : "2D-SFC",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C4",
      },
      {
        "label"  : "3D-C",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C5",
      },
      {
        "label"  : "3D-SC",
        "ls"     : "-",
        "marker" : ".",
        "color"  : "C6",
      },
    ], ncol=6, loc="upper center", outside=True, columnspacing=1)
  
  ax.set_axis_off()
  
  fig.save()



if __name__ == "__main__":
  main()
