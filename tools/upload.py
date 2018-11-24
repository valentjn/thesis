#!/usr/bin/python3

import argparse
import os
import shlex
import shutil
import subprocess
import tempfile
import time

def run(args, pipe=False, **kwargs):
  print("Running \"{}\"...".format(" ".join([shlex.quote(arg) for arg in args])))
  if pipe: kwargs["stdout"] = subprocess.PIPE
  process = subprocess.run(args, check=True, **kwargs)
  if pipe: return process.stdout.decode()



repoURL = "valentjn@neon%proxy:/data/scratch-ssd1/valentjn/git_repos/thesis"
switches = {
  "draftMode" : True,
  "checkMode" : True,
  "debugMode" : False,
  "showGlossaryDefinitionsMode" : False,
  "flipBookMode" : True,
  "partialCompileMode" : False,
}
defaultThesisPDFCopyPathDraft = "/tmp/thesisDraft/"
defaultThesisPDFCopyPathFinal = "/tmp/thesisFinal/"



if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Compiles thesis and uploads to bsplines.org")
  parser.add_argument("--revision", default="master", metavar="REV",
                      help="revision to compile (default: master)")
  parser.add_argument("--upload", action="store_true", default=True,
                      help="upload to bsplines.org (default)")
  parser.add_argument("--no-upload", action="store_false", dest="upload",
                      help="don't upload to bsplines.org")
  parser.add_argument("--draft-mode", action="store_true", default=True,
                      help="use draft mode (default)")
  parser.add_argument("--no-draft-mode", action="store_false", dest="draft_mode",
                      help="don't use draft mode")
  parser.add_argument("--destination", default=None, metavar="PATH",
                      help="local destination for compiled thesis")
  parser.add_argument("--copy-stuff", metavar="DIR",
                      help="copy .sconsign.dblite, build/gfx, and "
                           "git-fat files from this thesis folder "
                           "to save time")
  args = parser.parse_args()
  
  switches["draftMode"] = args.draft_mode
  destination = (args.destination if args.destination is not None else
                 (defaultThesisPDFCopyPathDraft if args.draft_mode else
                  defaultThesisPDFCopyPathFinal))
  
  with tempfile.TemporaryDirectory() as repoPath:
    print("Creating directory...")
    repoPath = os.path.join(repoPath, "thesis")
    os.mkdir(repoPath)
    
    print("")
    print("Cloning repo...")
    run(["git", "clone", repoURL, repoPath])
    
    print("")
    print("Checking out revision \"{}\"...".format(args.revision))
    run(["git", "checkout", args.revision], cwd=repoPath)
    
    print("")
    print("Setting git-fat remote...")
    gitFatConfigPath = os.path.join(repoPath, ".gitfat")
    with open(gitFatConfigPath, "r") as f: gitFatConfig = f.read()
    gitFatConfig = gitFatConfig.replace("neon:", "neon%proxy:")
    with open(gitFatConfigPath, "w") as f: f.write(gitFatConfig)
    
    print("")
    print("Initializing git-fat...")
    run(["git", "fat", "init"], cwd=repoPath)
    
    if args.copy_stuff is not None:
      gitDirSrc = run(["git", "rev-parse", "--git-dir"], pipe=True,
                      cwd=args.copy_stuff).strip()
      gitDirDst = os.path.join(repoPath, ".git")
      print("")
      print("Copying git-fat files...")
      os.rmdir(os.path.join(gitDirDst, "fat", "objects"))
      shutil.copytree(os.path.join(gitDirSrc, "fat", "objects"),
                      os.path.join(gitDirDst, "fat", "objects"))
    
    print("")
    print("Excluding bibliography from git-fat...")
    for root, dirs, files in os.walk(os.path.join(repoPath, "bib")):
      for file_ in files:
        if os.path.splitext(file_)[1] == ".pdf":
          with open(os.path.join(root, file_), "w") as f: f.truncate()
    
    print("")
    print("Pulling git-fat files...")
    run(["git", "fat", "pull"], cwd=repoPath)
    
    print("")
    print("Setting switches...")
    switchesPath = os.path.join(repoPath, "tex", "preamble", "switches.tex")
    with open(switchesPath, "r") as f: switchesTex = f.read()
    
    for switchName, switchValue in switches.items():
      trueString  = r"\toggletrue{{{}}}".format(switchName)
      falseString = r"\togglefalse{{{}}}".format(switchName)
      newString   = r"\newtoggle{{{}}}".format(switchName)
      switchesTex = switchesTex.replace(trueString, "")
      switchesTex = switchesTex.replace(falseString, "")
      switchesTex = switchesTex.replace(
        newString, newString + (trueString if switchValue else falseString))
    
    with open(switchesPath, "w") as f: f.write(switchesTex)
    
    if args.copy_stuff is not None:
      print("")
      print("Copying cpp/sgpp/...")
      os.rmdir(os.path.join(repoPath, "cpp", "sgpp"))
      shutil.copytree(os.path.join(args.copy_stuff, "cpp", "sgpp"),
                      os.path.join(repoPath, "cpp", "sgpp"),
                      copy_function=shutil.copy2)
      
      print("")
      print("Copying .sconsign.dblite, build/cpp/, and build/gfx/...")
      shutil.copy(os.path.join(args.copy_stuff, ".sconsign.dblite"), repoPath)
      for x in ["cpp", "gfx"]:
        shutil.copytree(os.path.join(args.copy_stuff, "build", x),
                        os.path.join(repoPath, "build", x),
                        copy_function=shutil.copy)
    
    try:
      print("")
      print("Compiling thesis...")
      run(["scons", "-j", str(os.cpu_count()), "out"], cwd=repoPath)
      outDir = os.path.join(repoPath, "out")
      thesisPDFPath = os.path.join(outDir, "thesisManuscriptScreen.pdf")
      
      if args.upload:
        print("")
        print("Uploading thesis...")
        run(["scp", thesisPDFPath,
             "jvalentin@xgm.de:bsplines.org/pub/~valentjn/files/thesis.pdf"])
    except subprocess.CalledProcessError:
      print("")
      print("Error while compiling or uploading the thesis.")
      print("Entering endless loop. You've got the chance to debug or")
      print("copy necessary files. Repository: {}".format(repoPath))
      while True: time.sleep(1)
      raise
    
    print("")
    print("Copying thesis to {}...".format(destination))
    os.makedirs(destination, exist_ok=True)
    
    for filename in os.listdir(outDir):
      if filename.endswith(".pdf"):
        shutil.copy(os.path.join(outDir, filename), destination)
