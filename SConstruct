import os

env = Environment(ENV={"PATH" : os.environ["PATH"]})
env.Replace(PDFLATEX="lualatex")
env.Append(PDFLATEXFLAGS='-enable-write18')

Figs   = env.SConscript("figures/SConscript", exports='env')
Thesis = env.SConscript("SConscript", exports='env')

Depends (Thesis, Figs)
