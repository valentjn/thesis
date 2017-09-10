import io
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import matplotlib2tikz
from mpl_toolkits.mplot3d import Axes3D



#def pop_kwarg(kwargs, name, default):
#  if name in kwargs:
#    value = kwargs[name]
#    del kwargs[name]
#  else:
#    value = default
#  
#  return value



class Figure(matplotlib.figure.Figure):
  _TEX_PREAMBLE = r"""
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
  
  _TEX_POSTAMBLE = r"""
\end{document}
"""
  
  _OUTPUT_FILTER = r"""
Horizontal alignment will be ignored as no 'x tick label text width' has been passed in the 'extra' parameter
Horizontal alignment will be ignored as no 'y tick label text width' has been passed in the 'extra' parameter
Horizontal alignment will be ignored as no 'z tick label text width' has been passed in the 'extra' parameter
"""
  
  def __init__(self, *args, **kwargs):
    super(Figure, self).__init__(*args, **kwargs)
  
  def _get_build_dir():
    return os.path.realpath(os.environ["BUILD_DIR"])
  
  def _get_graphics_basename():
    name = os.path.splitext(os.path.split(os.path.realpath(sys.argv[0]))[1])[0]
    
    if "_" in name:
      parts = name.split("_")
      number = parts[-1]
      if len(number.strip("0123456789")) == 0: name = "_".join(parts[:-1])
    
    return name
  
  #def _set_dict(d, name, default):
  #  d[name] = d.get(name, default)
  
  def save(self, graphics_number, width=None, height=None, extra_axis_options=None):
    if width is not None:  width  = "{}mm".format(width)
    if height is not None: height = "{}mm".format(height)
    if extra_axis_options is None: extra_axis_options = {}
    
    build_dir = Figure._get_build_dir()
    graphics_basename = Figure._get_graphics_basename()
    filename = os.path.join(build_dir, "{}_{}.tex".format(graphics_basename, graphics_number))
    print("Saving {}...".format(os.path.split(filename)[1]))
    
    #for direction in ["x", "y"]:
    #  Figure._set_dict(extra_axis_options, "{} tick label text width".format(direction), "20mm")
    #  Figure._set_dict(extra_axis_options, "{} tick label align".format(direction), "center")
    #print(extra_axis_options)
    
    stdout = sys.stdout
    
    try:
      sys.stdout = io.StringIO()
      tex = matplotlib2tikz.get_tikz_code(
        "UNUSED",
        figure=self,
        figurewidth=width,
        figureheight=height,
        extra_axis_parameters=extra_axis_options,
        show_info=False,
      )
      output = sys.stdout.getvalue()
    finally:
      sys.stdout = stdout
    
    output = "\n".join([x for x in output.splitlines()
                        if x not in Figure._OUTPUT_FILTER])
    if output != "": print(output)
    
    tex = Figure._TEX_PREAMBLE + tex + Figure._TEX_POSTAMBLE
    
    with open(filename, "w") as f: f.write(tex)
