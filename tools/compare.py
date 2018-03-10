#!/usr/bin/python3

import argparse
import os
import shlex
import subprocess

def run(args, pipe=True, **kwargs):
  print("Running \"{}\"...".format(" ".join([shlex.quote(arg) for arg in args])))
  if pipe: kwargs["stdout"] = subprocess.PIPE
  process = subprocess.run(args, check=True, **kwargs)
  if pipe: return process.stdout.decode()



directory = "/tmp/compare"



if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Compares two versions of the thesis")
  parser.add_argument("revision1", metavar="REVISION1",
                      help="first revision to compare")
  parser.add_argument("revision2", metavar="REVISION2",
                      help="first revision to compare")
  parser.add_argument("--copy-gfx", metavar="DIR",
                      help="copy .sconsign.dblite and build/gfx from this thesis folder "
                           "to save time")
  args = parser.parse_args()
  
  os.makedirs(directory, exist_ok=True)
  
  revs = [run(["git", "rev-parse", "--short=8", x]).strip()
          for x in [args.revision1, args.revision2]]
  print("Comparing {} ({}) with {} ({}).".format(
    args.revision1, revs[0], args.revision2, revs[1]))
  
  for i in range(2):
    pdfPath = os.path.join(directory, "thesis_{}.pdf".format(revs[i]))
    
    if os.path.isfile(pdfPath):
      print("{} already exists.".format(pdfPath))
    else:
      print("Compiling PDF for revision {}...".format(revs[i]))
      uploadPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "upload.py")
      uploadArgs = [uploadPath, "--revision", revs[i], "--no-upload", "--destination", pdfPath]
      if args.copy_gfx: uploadArgs += ["--copy-gfx", args.copy_gfx]
      run(uploadArgs, pipe=False)
    
    firstImagePath = os.path.join(directory, "thesis_{}-0.png".format(revs[i]))
    
    if os.path.isfile(firstImagePath):
      print("{} already exists.".format(firstImagePath))
    else:
      print("Converting to PNGs for revision {}...".format(revs[i]))
      pngPath = os.path.join(directory, "thesis_{}.png".format(revs[i]))
      run(["convert", "-density", "100", pdfPath, "-alpha", "flatten", pngPath])
  
  j = 0
  
  while True:
    imagePaths = [os.path.join(directory, "thesis_{}-{}.png".format(rev, j))
                  for rev in revs]
    if any([not os.path.isfile(x) for x in imagePaths]): break
    
    diffPath = os.path.join(directory, "diff_{}_{}-{}.png".format(revs[0], revs[1], j))
    
    if os.path.isfile(diffPath):
      print("{} already exists.".format(diffPath))
    else:
      print("Diffing page {}...".format(j + 1))
      subprocess.run(["composite", imagePaths[0], imagePaths[1],
                      "-compose", "difference", diffPath])
    
    j += 1
