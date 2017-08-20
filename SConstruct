import os

# set up environment, export environment variables of the shell
# (for example needed for custom TeX installations which need PATH)
env = Environment(ENV=os.environ)

# use LuaLaTeX as compiler (successor of PDFLaTeX)
env.Replace(PDFLATEX="texfot lualatex")
# enable SyncTeX for GUI editors
env.Append(PDFLATEXFLAGS="--synctex=1")
# quiet output
env.Append(BIBERFLAGS="-q")

sconscripts = {}

for dir in ["bib", "gfx", "tex"]:
  # tell SConscript which its build directory is
  env.Replace(BUILD_DIR=env.Dir("build/{}".format(dir)))
  # create build directory
  env.Execute(Mkdir(env["BUILD_DIR"]))
  # execute SConscript
  sconscripts[dir] = env.SConscript("{}/SConscript".format(dir), exports="env")
  # clean up (scons -c)
  env.Clean(sconscripts[dir], env["BUILD_DIR"])

# dependencies
env.Depends(sconscripts["tex"], [sconscripts["bib"], sconscripts["gfx"]])
# install PDF
pdf_dir = env.Dir("pdf")
env.Execute(Mkdir(pdf_dir))
pdf = env.Install(pdf_dir, sconscripts["tex"])

# don't clean PDF
env.NoClean(sconscripts["tex"], pdf)
