import hashlib
import lzma
import os
import pathlib
import pickle
import platform
import subprocess
import sys
import warnings

import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.switch_backend("pgf")
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.axis3d import Axis



COLORS = {
  "anthrazit"  : ( 62/255,  68/255,  76/255),
  "mittelblau" : (  0/255,  81/255, 158/255),
  "hellblau"   : (  0/255, 190/255, 255/255),
}

LINE_COLORS = [
  (0.000, 0.447, 0.741),
  (0.850, 0.325, 0.098),
  (0.749, 0.561, 0.102),
  (0.494, 0.184, 0.556),
  (0.466, 0.674, 0.188),
  (0.301, 0.745, 0.933),
  (0.635, 0.078, 0.184),
  (0.887, 0.465, 0.758),
  (0.496, 0.496, 0.496),
]

mpl.rcParams.update({
  "axes.prop_cycle" : cycler.cycler(color=LINE_COLORS),
  "lines.linewidth" : 1,
  "pgf.texsystem" : "lualatex",
  "pgf.rcfonts" : False,
  "text.usetex" : True,
})

mpl.colors.ColorConverter.colors.update(COLORS)
mpl.colors.ColorConverter.cache.update(
  {(name, None) : color + (1,) for name, color in COLORS.items()})



class Figure(mpl.figure.Figure):
  _TEX_PREAMBLE_COMMON = r"""
\usepackage[ngerman,american]{babel}
\usepackage{mathtools}
\usepackage[utf8]{luainputenc}
\usepackage[T1]{fontenc}

\usepackage{xcolor}

\definecolor{anthrazit}{RGB}{62,68,76}
\definecolor{mittelblau}{RGB}{0,81,158}
\definecolor{hellblau}{RGB}{0,190,255}

\definecolor{C0}{rgb}{0.000,0.447,0.741}
\definecolor{C1}{rgb}{0.850,0.325,0.098}
\definecolor{C2}{rgb}{0.749,0.561,0.102}
\definecolor{C3}{rgb}{0.494,0.184,0.556}
\definecolor{C4}{rgb}{0.466,0.674,0.188}
\definecolor{C5}{rgb}{0.301,0.745,0.933}
\definecolor{C6}{rgb}{0.635,0.078,0.184}
\definecolor{C7}{rgb}{0.887,0.465,0.758}
\definecolor{C8}{rgb}{0.496,0.496,0.496}

\usepackage{contour}
\contourlength{1.5pt}

% prevent Matplotlib from loading fontspec as this resets the default text font
% (the default math font will be alright with the no-math option to fontspec,
% but the text font will still be CM...)
\makeatletter
\@namedef{ver@fontspec.sty}{}
\makeatother

%\PassOptionsToPackage{no-math}{fontspec}
"""
  
  _TEX_PREAMBLE_SPECIAL = {
    "beamer" : r"""
\usepackage[scaled]{helvet}
\renewcommand*{\familydefault}{\sfdefault}
\usepackage{sfmath}
""",
    "paper" : "",
    "thesis" : r"""
\usepackage[bitstream-charter]{mathdesign}

% set dummy values for necessary switches to enable loading of
% glossary/notation
\usepackage{etoolbox}
\newtoggle{partialCompileMode}
\toggletrue{partialCompileMode}
\newtoggle{showGlossaryDefinitionsMode}
\togglefalse{showGlossaryDefinitionsMode}

% needed for some of the notation definitions
\usepackage{xstring}

\makeatletter
  % prepare loading of notation
  \input{preamble/settings/glossary}
  
  % automatically replace "l" with \ell in math mode
  \mathcode`l="8000
  \begingroup
  \lccode`\~=`\l
  \DeclareMathSymbol{\lsb@l}{\mathalpha}{letters}{`l}
  \lowercase{\gdef~{\ifnum\the\mathgroup=\m@ne \ell \else \lsb@l \fi}}%
  \endgroup
\makeatother

\input{preamble/notation}
""",
    "defense" : r"""
\usepackage[bitstream-charter]{mathdesign}

% needed for some of the notation definitions
\usepackage{xstring}

\makeatletter
  % automatically replace "l" with \ell in math mode
  \mathcode`l="8000
  \begingroup
  \lccode`\~=`\l
  \DeclareMathSymbol{\lsb@l}{\mathalpha}{letters}{`l}
  \lowercase{\gdef~{\ifnum\the\mathgroup=\m@ne \ell \else \lsb@l \fi}}%
  \endgroup
\makeatother

\input{preamble/notation}
""",
    "beamer2" : r"""
\usepackage[bitstream-charter]{mathdesign}

% needed for some of the notation definitions
\usepackage{xstring}

\makeatletter
  % automatically replace "l" with \ell in math mode
  \mathcode`l="8000
  \begingroup
  \lccode`\~=`\l
  \DeclareMathSymbol{\lsb@l}{\mathalpha}{letters}{`l}
  \lowercase{\gdef~{\ifnum\the\mathgroup=\m@ne \ell \else \lsb@l \fi}}%
  \endgroup
\makeatother

\renewcommand*{\vec}[1]{{\boldsymbol{#1}}}
\def\*#1{\vec{#1}}
""",
  }
  
  graphicsCounter = 0
  
  def __init__(self, *args, fontSize=None, preamble="", mode=None, **kwargs):
    super(Figure, self).__init__(*args, **kwargs)
    
    if mode is None:
      if "talk" in Figure._getBuildDir():
        self.mode = "beamer"
      elif "thesis" in Figure._getBuildDir():
        self.mode = "thesis"
      elif "defense" in Figure._getBuildDir():
        self.mode = "defense"
      else:
        self.mode = "paper"
    else:
      self.mode = mode
    
    if self.mode != "thesis":
      # patch mplot3d such that margins near xy-plane edges vanishs
      # (from https://stackoverflow.com/a/16496436)
      if not hasattr(Axis, "_get_coord_info_old"):
        def _get_coord_info_new(self, renderer):
          mins, maxs, centers, deltas, tc, highs = self._get_coord_info_old(renderer)
          mins += deltas / 4
          maxs -= deltas / 4
          return mins, maxs, centers, deltas, tc, highs
        Axis._get_coord_info_old = Axis._get_coord_info
        Axis._get_coord_info = _get_coord_info_new
    
    fontFamily = ("sans-serif" if self.mode == "beamer" else "serif")
    defaultFontSize = (9 if self.mode in ["defense", "beamer2"] else 11)
    if fontSize is None: fontSize = defaultFontSize
    preamble = (Figure._TEX_PREAMBLE_COMMON +
                Figure._TEX_PREAMBLE_SPECIAL[self.mode] +
                preamble)
    
    mpl.rcParams.update({
      "font.family" : fontFamily,
      "font.size" : fontSize,
      "pgf.preamble" : preamble.splitlines(),
    })
    
    if self.mode in ["defense", "beamer2"]:
      mpl.rcParams.update({
        "lines.linewidth" : 0.8,
        "lines.markersize" : 4
      })
    
    self._saveDisabled = (platform.node() == "neon")
  
  @staticmethod
  def create(*args, scale=1, **kwargs):
    if "figsize" in kwargs: kwargs["figsize"] = [scale * x for x in kwargs["figsize"]]
    return plt.figure(*args, FigureClass=Figure, **kwargs)
  
  @staticmethod
  def _getBuildDir():
    if "BUILD_DIR" not in os.environ:
      warnings.warn("Environment variable BUILD_DIR not set. "
                    "Writing graphic files to the current directory.")
    return os.path.realpath(os.environ.get("BUILD_DIR", "."))
  
  @staticmethod
  def _getGraphicsBasename():
    return os.path.splitext(os.path.split(os.path.realpath(sys.argv[0]))[1])[0]
  
  @staticmethod
  def _computeHash(path):
    try:
      with open(path, "rb") as f: return hashlib.md5(f.read()).digest()
    except:
      return None
  
  @staticmethod
  def load(datPath=None):
    Figure.graphicsCounter += 1
    graphicsNumber = Figure.graphicsCounter
    
    if datPath is None:
      buildDir = Figure._getBuildDir()
      graphicsBasename = Figure._getGraphicsBasename()
      basename = os.path.join(buildDir, "{}_{}".format(graphicsBasename, graphicsNumber))
      datPath = "{}.pickle.dat".format(basename)
    
    print("Loading {}...".format(datPath))
    with lzma.open(datPath, "rb") as f: return pickle.load(f)
  
  def disableSave(self):
    self._saveDisabled = True
  
  def enableSave(self):
    self._saveDisabled = False
  
  def save(self, graphicsNumber=None, appendGraphicsNumber=True,
           hideSpines=True, tightLayout=True, crop=True, close=True,
           transparent=True, fix3DTransparency=True,
           fixColorbarHairlines=True):
    plt.figure(self.number)
    
    if graphicsNumber is None:
      Figure.graphicsCounter += 1
      graphicsNumber = Figure.graphicsCounter
    else:
      Figure.graphicsCounter = graphicsNumber
    
    if self._saveDisabled:
      if close: plt.close(self)
      return
    
    if tightLayout is not False:
      if tightLayout is True: tightLayout = {}
      self.tight_layout(**tightLayout)
    
    if hideSpines:
      for ax in self.axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    
    # remove transparency in background panes (not allowed in PDF/X)
    if fix3DTransparency:
      for ax in self.axes:
        if isinstance(ax, Axes3D):
          # left pane
          ax.w_xaxis.set_pane_color((0.96, 0.96, 0.96, 1.0))
          # right pane
          ax.w_yaxis.set_pane_color((0.92, 0.92, 0.92, 1.0))
          # bottom pane
          ax.w_zaxis.set_pane_color((0.94, 0.94, 0.94, 1.0))
    
    # remove hairlines in colorbars (leads to errors in Preflight),
    # see matplotlib's ColorbarBase._config_axes; not sure why they
    # use a line width of 0.01. Also, it would be nice to specifically
    # detect axes that correspond to colorbars, but I'm not sure if that's
    # possible at all.
    if fixColorbarHairlines:
      for ax in self.get_axes():
        for child in ax.get_children():
          if isinstance(child, mpl.patches.Polygon):
            if child.get_linewidth() == 0.01: child.set_edgecolor("none")
    
    if graphicsNumber is None: graphicsNumber = self.number
    
    buildDir = Figure._getBuildDir()
    graphicsBasename = Figure._getGraphicsBasename()
    
    basename = graphicsBasename
    if appendGraphicsNumber: basename += "_{}".format(graphicsNumber)
    basename = os.path.join(buildDir, basename)
    
    if transparent:
      savefigFcn = (
        lambda path: plt.savefig(path, facecolor="none", transparent=True))
    else:
      savefigFcn = (
        lambda path: plt.savefig(path, facecolor=self.get_facecolor()))
    
    pgfPath = "{}.pgf".format(basename)
    print("Saving {}...".format(os.path.split(pgfPath)[1]), flush=True)
    savefigFcn(pgfPath)
    
    pgfXzPath = "{}.pgf.xz".format(basename)
    oldHash = Figure._computeHash(pgfXzPath)
    with open(pgfPath, "rb") as f: pgf = f.read()
    with lzma.open(pgfXzPath, "wb") as f: pickle.dump(pgf, f)
    os.remove(pgfPath)
    newHash = Figure._computeHash(pgfXzPath)
    
    pdfPath = "{}.pdf".format(basename)
    
    if (oldHash == newHash) and os.path.isfile(pdfPath):
      print("No changes since last run.", flush=True)
      pathlib.Path(pdfPath).touch()
    else:
      print("Compiling to {}...".format(os.path.split(pdfPath)[1]), flush=True)
      savefigFcn(pdfPath)
      if crop: subprocess.run(["pdfcrop", pdfPath, pdfPath], check=True)
      
      datPath = "{}.pickle.xz".format(basename)
      print("Saving {}...".format(os.path.split(datPath)[1]), flush=True)
      with lzma.open(datPath, "wb") as f: pickle.dump(self, f)
    
    if close: plt.close(self)
