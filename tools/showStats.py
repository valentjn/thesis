#!/usr/bin/python3

import datetime
import multiprocessing
import os
import re
import subprocess

import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt

def runCommand(args, decode=True, **kwargs):
  kwargs = {"check" : True, "stdout" : subprocess.PIPE,
            "stderr" : subprocess.DEVNULL, **kwargs}
  process = subprocess.run(args, **kwargs)
  output = process.stdout
  if decode: output = output.decode()
  return output

def fmt(number):
  return ("{:,}" if number >= 1e4 else "{}").format(number)

def getStats(head):
  pdfPath = "/tmp/thesis/thesisManuscriptScreen.pdf"
  stats = {}
  
  try:
    output = runCommand(["git", "log", "--pretty=format:%ci",
                         "{}~..{}".format(head, head)])
  except subprocess.CalledProcessError:
    output = runCommand(["git", "log", "--pretty=format:%ci", head])
  
  commitDate = output.strip().split(" ")[0]
  print("Processing commit {} from {}...".format(head, commitDate))
  
  output = runCommand(["git", "log", "--pretty=format:%h %ci", head])
  commits = [x.split(" ") for x in output.strip().splitlines()]
  commits = [[x[0], x[1]] for x in commits]
  numberOfCommits = len(commits)
  stats["commits"] = numberOfCommits
  
  numberOfDays = len(set([x[1] for x in commits]))
  numberOfWorkHours = 6 * numberOfDays
  stats["work hours (est.)"] = numberOfWorkHours
  
  numberOfAppleJuiceLiters = 1.7 * numberOfDays
  stats["liters of apple juice (est.)"] = round(numberOfAppleJuiceLiters)
  
  output = runCommand(["git", "log", "-C", "--pretty=format:%h",
                        "--shortstat", head])
  shortStats = [x.strip() for x in output.strip().splitlines()
                if x.startswith(" ")]
  numberOfChangedFiles = 0
  numberOfInsertions = 0
  numberOfDeletions = 0
  
  for shortStat in shortStats:
    matches = re.findall(r"([0-9]+) file", shortStat)
    if len(matches) > 0: numberOfChangedFiles += len(matches[0])
    matches = re.findall(r"([0-9]+) insertion", shortStat)
    if len(matches) > 0: numberOfInsertions += len(matches[0])
    matches = re.findall(r"([0-9]+) deletion", shortStat)
    if len(matches) > 0: numberOfDeletions += len(matches[0])
  
  stats["changed files"] = numberOfChangedFiles
  stats["insertions"] = numberOfInsertions
  stats["deletions"] = numberOfDeletions
  
  output = runCommand(["git", "log", "-C", "--pretty=format:%h",
                       "-p", "--color-words=.", head,
                       "gfx/py", "lua", "py", "tex", "tools"], decode=False)
  insertionMatches = re.findall(b"\x1b\\[32m(.*?)\x1b\\[m", output)
  deletionMatches  = re.findall(b"\x1b\\[31m(.*?)\x1b\\[m", output)
  numberOfKeystrokes = len(deletionMatches)
  lowerCaseCharacters = b"^1234567890qwertzuiop+asdfghjkl#<yxcvbnm,.-"
  
  for match in insertionMatches:
    for character in match:
      numberOfKeystrokes += (1 if character in lowerCaseCharacters else 2)
  
  stats["keystrokes"] = numberOfKeystrokes
  
  try:
    bib = runCommand(["git", "show", "{}:bib/bibliography.bib".format(head)])
  except subprocess.CalledProcessError:
    bib = ""
  
  matches = re.findall(r"@([A-Za-z]+)\{", bib)
  numberOfReferences = len([x for x in matches if x.lower() != "comment"])
  stats["cited works"] = numberOfReferences
  
  output = runCommand(["git", "ls-tree", "-r", head, "tex/document"])
  if len(output.strip()) == 0:
    output = runCommand(["git", "ls-tree", "-r", head, "tex"])
  
  texPaths = [x.split("\t")[1] for x in output.strip().splitlines()]
  numberOfCitations = 0
  numberOfCrossReferences = 0
  numberOfEquations = 0
  numberOfFormulas = 0
  numberOfFigures = 0
  numberOfTables = 0
  numberOfAlgorithms = 0
  numberOfTheorems = 0
  
  for texPath in texPaths:
    tex = runCommand(["git", "show", "{}:{}".format(head, texPath)])
    
    matches = re.findall(r"\\(multi)?cite\{(.*?)\}", tex)
    numberOfCitations += sum([x[1].count(",") + 1 for x in matches])
    
    matches = re.findall(r"\\(eq|c|C)?ref\{(.*?)\}", tex)
    numberOfCrossReferences += len(matches)
    
    matches = re.findall(r"\\begin\{(equation|align|alignat|gather|"
                         r"split|multline)\}", tex)
    numberOfEquations += len(matches)
    
    matches = re.findall(r"\$(.*?)\$", tex, flags=re.DOTALL)
    numberOfFormulas += len(matches)
    
    matches = re.findall(r"\\begin\{(SC)?figure\}", tex)
    numberOfFigures += len(matches)
    
    matches = re.findall(r"\\begin\{(SC)?table\}", tex)
    numberOfTables += len(matches)
    
    matches = re.findall(r"\\begin\{algorithm\}", tex)
    numberOfAlgorithms += len(matches)
    
    matches = re.findall(r"\\begin\{(short)?(theorem|proposition|lemma|"
                         r"corollary|definition|restatable)\}", tex)
    numberOfTheorems += len(matches)
  
  stats["citations"] = numberOfCitations
  stats["cross-references"] = numberOfCrossReferences
  stats["equations"] = numberOfEquations
  stats["formulas"] = numberOfFormulas
  stats["figures"] = numberOfFigures
  stats["tables"] = numberOfTables
  stats["algorithms"] = numberOfAlgorithms
  stats["theorems"] = numberOfTheorems
  
  try:
    output = runCommand([
        "git", "show", "{}:compileCounter.txt".format(head)])
  except subprocess.CalledProcessError:
    try:
      output = runCommand([
          "git", "show", "{}:compile_counter.txt".format(head)])
    except subprocess.CalledProcessError:
      output = "0"
  
  numberOfLaTeXRuns = int(output.strip())
  stats["LaTeX runs"] = numberOfLaTeXRuns
  
  try:
    tex = runCommand(["git", "show",
                      "{}:tex/document/progress.tex".format(head)])
  except subprocess.CalledProcessError:
    try:
      tex = runCommand(["git", "show",
                        "{}:tex/progress.tex".format(head)])
    except subprocess.CalledProcessError:
      tex = ""
  
  progressTableLines = [x for x in tex.splitlines() if x.count("&") > 5]
  numberOfSections = len(progressTableLines)
  numberOfUnitTests = sum([int(x.split("&")[4].strip())
                           for x in progressTableLines])
  stats["sections"] = numberOfSections
  stats["unit tests"] = numberOfUnitTests
  stats["chapters"] = 9+3
  
  if head == "HEAD":
    numberOfBytes = os.stat(pdfPath).st_size
    stats["PDF bytes"] = numberOfBytes
    
    output = runCommand(["pdfinfo", pdfPath])
    matches = re.findall(r"Pages: *([0-9]+)", output)
    numberOfPages = int(matches[0]) - 4
    stats["pages"] = numberOfPages
    
    pdf = runCommand(["pdftotext", "-layout", "-nopgbrk",
        "-x", "70", "-y", "85", "-W", "455", "-H", "700", pdfPath, "-"])
    pdf = pdf.replace("\u2013", "-")
    pdf = pdf.replace("\n", " ")
    words = re.findall(r"(?:(?=[^0-9])[\w\-])+", pdf)
    words = [x for x in words if len(x) > 2]
    numberOfWords = len(words)
    stats["words"] = numberOfWords
    
    numberOfCharacters = sum([len(x) for x in words])
    stats["characters"] = numberOfCharacters
  
  stats["PhD thesis"] = 1
  
  stats = sorted(list(stats.items()), key=lambda x: -x[1])
  return stats

def main():
  stats = getStats("HEAD")
  print("")
  print("\n".join(["{} {}".format(fmt(x[1]), x[0]) for x in stats]))
  print("")
  
  output = runCommand(["git", "log", "--pretty=format:%h %ci", "HEAD"])
  lines = [line.split(" ") for line in output.strip().splitlines()]
  
  commits = [line[0] for line in lines]
  dates = [line[1] for line in lines]
  indices = sorted(list({date : i for i, date in enumerate(dates)}.values()),
                   reverse=True)
  commits = [commits[i] for i in indices]
  dates   = [dates[i] for i in indices]
  
  dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]
  t0 = datetime.datetime(2018, 1, 31)
  commits = [commits[i] for i in range(len(commits)) if dates[i] >= t0]
  dates   = [dates[i]   for i in range(len(dates))   if dates[i] >= t0]
  
  with multiprocessing.Pool() as pool:
    allStats = pool.map(getStats, commits)
  
  labels = [x[0] for x in allStats[-1]
            if x[0] not in ["PhD thesis", "chapters"]]
  allStats = [dict(x) for x in allStats]
  lines = [[((min(stats[label] / allStats[-1][label], 1) * 100)
             if allStats[-1][label] > 0 else 0) for stats in allStats]
           for label in labels]
  
  lineTypes = [
    {
      "color" : "C{}".format(i % 9),
      "ls" : ["-", "--", ":"][i // 9],
    } for i in range(len(lines))
  ]
  
  lineColors = [
    (0.000, 0.447, 0.741),
    (0.850, 0.325, 0.098),
    (0.929, 0.694, 0.125),
    (0.494, 0.184, 0.556),
    (0.466, 0.674, 0.188),
    (0.301, 0.745, 0.933),
    (0.635, 0.078, 0.184),
    (0.887, 0.465, 0.758),
    (0.496, 0.496, 0.496),
  ]
  
  mpl.rcParams["axes.prop_cycle"] = cycler.cycler(color=lineColors)
  fig = plt.figure()
  ax = fig.gca()
  
  for line, lineType in zip(lines, lineTypes):
    ax.plot_date(dates, line, **lineType)
  
  ax.grid()
  ax.set_xlabel("Time")
  ax.set_ylabel("Percentage (current value = 100%)")
  ax.set_title("Thesis Statistics")
  plt.legend(["{} {}".format(fmt(allStats[-1][x]), x) for x in labels])
  plt.show()



if __name__ == "__main__":
  main()
