#!/usr/bin/python3

import os
import shutil
import subprocess
import tempfile



texPath = os.path.join(os.path.dirname(__file__),
                       "..", "tex", "document", "abstract.tex")
outPath = os.path.join(os.path.dirname(__file__),
                       "..", "build", "gfx", "abstractForCover.pdf")

replaceWords = {
  r"In simulation technology," : r"\textbf{In simulation technology,}",
  r"curse of dimensionality," : r"\emph{curse of dimen\-sionality,}",
  r"Sparse grids" : r"\emph{Sparse grids}",
  r"This thesis demonstrates" : r"\textbf{This thesis demonstrates}",
  r"hierarchical B-splines on sparse grids are" :
      r"\emph{hierarchical B-splines on sparse grids} are",
}

with open(texPath, "r") as f: tex = f.read()
lines = tex.splitlines()
i = [i for i in range(len(lines))
     if lines[i].startswith(r"\section")][0] + 1
j = ([j for j in range(i, len(lines))
      if lines[j].startswith("\\")] + [len(lines)])[0]
abstract = "\n".join(lines[i:j])

for search, replace in replaceWords.items():
  abstract = abstract.replace(search, replace)

tex = (r"""
\documentclass{article}
\usepackage[american]{babel}
\usepackage[T1]{fontenc}
\usepackage[bitstream-charter]{mathdesign}
\usepackage[final,tracking=smallcaps,stretch=10,shrink=10]{microtype}
\usepackage[left=20mm,right=102mm]{geometry}
\setlength{\parindent}{0em}
\setlength{\parskip}{0.5em}
\pagestyle{empty}
\begin{document}
""" + abstract + r"""
\end{document}
""")

print(tex)

with tempfile.TemporaryDirectory() as tempPath:
  tempTexPath = os.path.join(tempPath, "abstract.tex")
  with open(tempTexPath, "w") as f: f.write(tex)
  subprocess.run(["lualatex", "abstract"], cwd=tempPath, check=True)
  
  tempPDFPath = os.path.join(tempPath, "abstract.pdf")
  subprocess.run(["pdfcrop", tempPDFPath, tempPDFPath], check=True)
  
  shutil.copy(tempPDFPath, outPath)
