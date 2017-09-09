import os

import matplotlib
import matplotlib.pyplot as plt
import matplotlib2tikz
from mpl_toolkits.mplot3d import Axes3D

from . import *



TEX_PREAMBLE = r"""
\documentclass{article}

\usepackage[ngerman,american]{babel}

\usepackage{mathtools}

\usepackage[utf8]{luainputenc}
%\usepackage[scale=0.9]{GoMono}
\usepackage[T1]{fontenc}
\usepackage[bitstream-charter]{mathdesign}

%\usepackage{xcolor}

\usepackage{pgfplots}
\pgfplotsset{compat=1.15}
\usepgfplotslibrary{groupplots}
\usepackage[margin=0mm]{geometry}

\begin{document}
  \pagenumbering{gobble}
"""

TEX_POSTAMBLE = r"""
\end{document}
"""



#def pop_kwarg(kwargs, name, default):
#  if name in kwargs:
#    value = kwargs[name]
#    del kwargs[name]
#  else:
#    value = default
#  
#  return value



class Figure(matplotlib.figure.Figure):
  def __init__(self, *args, **kwargs):
    super(Figure, self).__init__(*args, **kwargs)
  
  def save(self, graphics_number, width=None, height=None):
    if width is not None:  width  = "{}mm".format(width)
    if height is not None: height = "{}mm".format(height)
    
    filename = os.path.join(build_dir, "{}_{}.tex".format(graphics_basename, graphics_number))
    print("Saving {}...".format(os.path.split(filename)[1]))
    
    tex = matplotlib2tikz.get_tikz_code(
      "UNUSED",
      figure=self,
      figurewidth=width,
      figureheight=height,
      show_info=False,
    )
    
    tex = TEX_PREAMBLE + tex + TEX_POSTAMBLE
    
    with open(filename, "w") as f: f.write(tex)
