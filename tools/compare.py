#!/usr/bin/python3

import argparse
import multiprocessing
import os
import shlex
import shutil
import subprocess

def run(args, pipe=True, **kwargs):
  print("Running \"{}\"...".format(" ".join([shlex.quote(arg) for arg in args])))
  if pipe: kwargs["stdout"] = subprocess.PIPE
  process = subprocess.run(args, check=True, **kwargs)
  if pipe: return process.stdout.decode()

def compileConvert(i):
  pdfPath = os.path.join(directory, "thesis_{}.pdf".format(revs[i]))
  
  if os.path.isfile(pdfPath):
    print("{} already exists.".format(pdfPath))
  else:
    print("Compiling PDF for revision {}...".format(revs[i]))
    uploadPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "upload.py")
    uploadArgs = [uploadPath, "--revision", revs[i], "--no-upload", "--no-draft-mode",
                  "--destination", pdfPath]
    if args.copy_stuff: uploadArgs += ["--copy-stuff", args.copy_stuff]
    run(uploadArgs, pipe=False)
  
  firstImagePath = os.path.join(directory, "thesis_{}-0.png".format(revs[i]))
  
  if os.path.isfile(firstImagePath):
    print("{} already exists.".format(firstImagePath))
  else:
    print("Converting to PNGs for revision {}...".format(revs[i]))
    pngPath = os.path.join(directory, "thesis_{}.png".format(revs[i]))
    run(["convert", "-density", "100", pdfPath, "-alpha", "flatten", pngPath])

def diffPage(j):
  if os.path.isfile(diffPaths[j]):
    print("{} already exists.".format(diffPaths[j]))
  else:
    print("Diffing page {}...".format(j + 1))
    run(["composite", imagePaths[j][0], imagePaths[j][1],
         "-compose", "difference", diffPaths[j]])
  
  brightness = float(run(["identify", "-format", "%[fx:maxima]", diffPaths[j]]).strip())
  return (brightness > brightnessThreshold)

def generateResult(j):
  run(["convert", imagePaths[j][0], diffPaths[j], imagePaths[j][1],
       "+append", resultPaths[j]])



directory = "/tmp/compare"
brightnessThreshold = 0



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
  
  with multiprocessing.Pool() as pool:
    pool.map(compileConvert, range(2))
  
  pageCount = 0
  imagePaths = []
  
  while True:
    curImagePaths = [os.path.join(directory, "thesis_{}-{}.png".format(rev, pageCount))
                     for rev in revs]
    if any([not os.path.isfile(x) for x in curImagePaths]): break
    pageCount += 1
    imagePaths.append(curImagePaths)
  
  diffPaths = [os.path.join(directory, "diff_{}_{}-{}.png".format(*revs, j))
               for j in range(pageCount)]
  
  with multiprocessing.Pool() as pool:
    pagesChanged = pool.map(diffPage, range(pageCount))
  
  pagesChanged = [i for i in range(pageCount) if pagesChanged[i]]
  resultsDirectory = os.path.join(directory, "results")
  if os.path.isdir(resultsDirectory): shutil.rmtree(resultsDirectory)
  os.makedirs(resultsDirectory)
  
  resultPaths = [os.path.join(resultsDirectory, "result_{}.png".format(j))
                 for j in range(pageCount)]
  
  with multiprocessing.Pool() as pool:
    pool.map(generateResult, pagesChanged)
  
  if len(pagesChanged) > 0:
    print("Pages with changes: {}".format(", ".join([str(x+1) for x in pagesChanged])))
    subprocess.Popen(["gwenview", resultPaths[pagesChanged[0]]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  else:
    print("No changes detected.")
