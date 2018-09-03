#!/usr/bin/python3

import datetime
import os
import subprocess

import matplotlib.pyplot as plt

progressPaths = ["tex/document/progress.tex", "tex/progress.tex"]

gitDir = os.path.join(os.path.dirname(__file__), "..")
gitLogArgs = ["git", "log", "--pretty=format:%h %ci", "--follow",
              progressPaths[0]]
process = subprocess.run(gitLogArgs, cwd=gitDir, check=True,
                         stdout=subprocess.PIPE)
gitLogOutput = process.stdout.decode()
lines = [line.split(" ") for line in gitLogOutput.splitlines()[::-1]]
commits = [line[0] for line in lines]
dates = [line[1] for line in lines]
pageNumbers = []

for commit in commits:
  progressTex = None
  
  for progressPath in progressPaths:
    gitShowArgs = ["git", "show", "{}:{}".format(commit, progressPath)]
    
    try:
      process = subprocess.run(
          gitShowArgs, cwd=gitDir, check=True,
          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
      continue
    
    progressTex = process.stdout.decode()
    break
  
  assert progressTex is not None
  tableTex = progressTex[progressTex.index(r"\toprule"):
                         progressTex.index(r"\bottomrule")]
  pageNumber = sum([int(line.split("&")[1].strip())
                    for line in tableTex.splitlines()[1:]])
  pageNumbers.append(pageNumber)

dates = ["2018-01-31", "2018-02-21", "2018-03-12", "2018-03-16"] + dates
pageNumbers = [0, 52, 56, 70] + pageNumbers

fig = plt.figure()
ax = fig.gca()
dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]
ax.plot_date(dates, pageNumbers, "k.-")
ax.plot_date([datetime.datetime(2018,  1, 31),
              datetime.datetime(2018, 11, 30)], [0, 224], "r-")
ax.grid()
ax.set_xlabel("Time")
ax.set_ylabel("Number of total pages")
ax.set_title("Writing Progress")
ax.legend(["Actual pages written", "Ideal"])
plt.show()
