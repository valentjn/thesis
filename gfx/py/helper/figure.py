import io
import os
import subprocess
import sys

import cycler
import matplotlib as mpl
mpl.use("pgf")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



COLORS = {
  "anthrazit" :  ( 62/255,  68/255,  76/255),
  "mittelblau" : (  0/255,  81/255, 158/255),
  "hellblau"   : (  0/255, 190/255, 255/255),
}



def create(*args, **kwargs):
  return plt.figure(*args, FigureClass=Figure, **kwargs)



class Figure(mpl.figure.Figure):
  counter = 0
  
  _TEX_PREAMBLE = r"""
\usepackage[ngerman,american]{babel}
\usepackage{mathtools}
\usepackage[utf8]{luainputenc}
\usepackage[T1]{fontenc}
\usepackage[bitstream-charter]{mathdesign}
"""
  
  _LINE_COLORS = [
    (0.000, 0.447, 0.741),
    (0.850, 0.325, 0.098),
    (0.929, 0.694, 0.125),
    (0.494, 0.184, 0.556),
    (0.466, 0.674, 0.188),
    (0.301, 0.745, 0.933),
    (0.635, 0.078, 0.184),
    (0.887, 0.465, 0.758),
    (0.496, 0.496, 0.496),
  ]
  
  def __init__(self, *args, **kwargs):
    super(Figure, self).__init__(*args, **kwargs)
    self.number = Figure.counter
    Figure.counter += 1
    mpl.rcParams.update({
      "axes.prop_cycle" : cycler.cycler(color=Figure._LINE_COLORS),
      "text.usetex" : True,
      "lines.linewidth" : 1,
      "pgf.texsystem" : "lualatex",
      "pgf.rcfonts" : False,
      "pgf.preamble" : Figure._TEX_PREAMBLE.splitlines(),
    })
  
  def _get_build_dir():
    return os.path.realpath(os.environ["BUILD_DIR"])
  
  def _get_graphics_basename():
    return os.path.splitext(os.path.split(os.path.realpath(sys.argv[0]))[1])[0]
  
  def save(self, graphics_number):
    plt.figure(self.number)
    
    for ax in self.axes:
      ax.spines["top"].set_visible(False)
      ax.spines["right"].set_visible(False)
    
    build_dir = Figure._get_build_dir()
    graphics_basename = Figure._get_graphics_basename()
    filename = os.path.join(build_dir, "{}_{}.pdf".format(graphics_basename, graphics_number))
    
    print("Saving {}...".format(os.path.split(filename)[1]))
    plt.savefig(filename)
    subprocess.run(["pdfcrop", filename, filename], check=True)
