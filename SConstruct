import os
import shlex
import subprocess
import sys
import warnings

# check SCons version
EnsureSConsVersion(3, 0)

# we need at least Python 3.5, for example for subprocess.run
if sys.version_info < (3, 5):
  raise RuntimeError("These SCons scripts require Python 3.5 or newer. "
                     "Try running `python3 /usr/bin/scons` or similar.")

# class with helper methods
class Helper(object):
  isPDFSizeOptInstalled = None
  
  @staticmethod
  def checkPDFSizeOptInstalled(env):
    if Helper.checkProgramInstalled(env, "pdfsizeopt"):
      Helper.isPDFSizeOptInstalled = True
    else:
      warnings.warn("pdfsizeopt required for compressing output PDFs. "
                    "Output PDFs won't be compressed.")
      Helper.isPDFSizeOptInstalled = False
  
  # check if a dependency is installed, fail if not (if desired)
  @staticmethod
  def checkProgramInstalled(env, program, fail=False):
    if (not env.GetOption("help")) and (not env.GetOption("clean")):
      conf = Configure(env, log_file=None)
      result = (conf.CheckProg(program) is not None)
      if fail and (not result): raise RuntimeError(
          "Program \"{}\" required, but not found in PATH.".format(program))
      conf.Finish()
      return result
    else:
      return True
  
  # compress PDF via pdfsizeopt
  def compressPDFs(target, source, env):
    pdf = target[0].abspath
    
    if Helper.isPDFSizeOptInstalled:
      pdfOptimized = "{}.opt".format(pdf)
      Helper.runCommand(["pdfsizeopt", "--do-unify-fonts=no",
                         "--use-pngout=no", "--v=30", pdf, pdfOptimized])
      os.remove(pdf)
      os.rename(pdfOptimized, pdf)
    else:
      print("Skipping compression of \"{}\".".format(pdf))
  
  # print and run command line, check=True by default
  @staticmethod
  def runCommand(args, check=True, **kwargs):
    print(" ".join([shlex.quote(arg) for arg in args]))
    kwargs["check"] = check
    return subprocess.run(args, **kwargs)

# set up environment, export environment variables of the shell
# (for example needed for custom TeX installations which need PATH)
env = Environment(ENV=os.environ)

# check if pdfsizeopt is installed
Helper.checkPDFSizeOptInstalled(env)

# use timestamp to decide if a file should be rebuilt
# (otherwise SCons won't rebuild even if it is necessary)
env.Decider("timestamp-newer")

# iterate over all dependent directories
# note: "tex" has to be before "out"; "cpp" has to be before "gfx"
dirTargets = {}
dirs = ["bib", "cpp", "gfx", "lua", "misc", "tex", "out"]
buildPDF = []
createDirs = (not env.GetOption("help")) and (not env.GetOption("clean"))

for dir_ in dirs:
  # tell SConscript which its build directory is
  env["BUILD_DIR"] = env.Dir(os.path.join("build", dir_))
  
  # create build directory
  if (dir_ not in ["lua", "misc"]) and createDirs:
    env.Execute(Mkdir(env["BUILD_DIR"]))
  
  # execute SConscript
  dirTargets[dir_] = env.SConscript(os.path.join(dir_, "SConscript"),
                                    exports=["env", "Helper"])
  # clean up dir_
  env.Clean(dirTargets[dir_], env["BUILD_DIR"])
  
  # set SGPP_FILES variable (list of files in build/cpp/sgpp)
  if dir_ == "cpp": env["SGPP_FILES"] = dirTargets[dir_][0]
  # set BUILD_PDF variable (build/tex/thesis.pdf)
  if dir_ == "tex": env["BUILD_PDF"]  = dirTargets[dir_][0]

# the PDF depends on everything that is not in tex (these dependencies are
# handled by tex/SConscript) and out
env.Depends(env["BUILD_PDF"], [dirTargets[dir_] for dir_ in dirs
                               if dir_ not in ["tex", "out"]])

# dirty fix for Debian bug #893740
# (https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=893740),
# they seem to have reintroduced the Python-2-only syntax "dict.has_key"
# (instead of "in") in SCons/Script/Main.py, line 1111,
# occurs when cleaning, i.e., `scons -c`
os.environ.has_key = (lambda x: x in os.environ)
