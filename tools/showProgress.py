#!/usr/bin/python3

import datetime
import os
import subprocess

import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np



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

progressPaths = ["tex/document/progress.tex", "tex/progress.tex"]
totalPages = 228
totalTests = 44



gitDir = os.path.join(os.path.dirname(__file__), "..")
gitLogArgs = ["git", "log", "--pretty=format:%h %ci", "--follow",
              progressPaths[0]]
process = subprocess.run(gitLogArgs, cwd=gitDir, check=True,
                         stdout=subprocess.PIPE)
gitLogOutput = process.stdout.decode()
lines = [line.split(" ") for line in gitLogOutput.splitlines()[::-1]]

commits = [line[0] for line in lines]
dates = [line[1] for line in lines]
indices = sorted(list({date : i for i, date in enumerate(dates)}.values()))
commits = [commits[i] for i in indices]
dates   = [dates[i] for i in indices]

writingProgress, testingProgress, editingProgress = [], [], []

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
  lines = [line.split("&") for line in tableTex.splitlines()[1:]]

  writtenPages = sum([int(fields[1].strip()) for fields in lines])
  writingProgress.append(writtenPages / totalPages)
  
  tests = sum([int(fields[4].strip()) for fields in lines])
  testingProgress.append(tests / totalTests)
  
  editedPages = sum([int(fields[1].strip()) * int(fields[-2].strip()[4:-1]) / 100
                     for fields in lines])
  editingProgress.append(editedPages / totalPages)

dates = (["2018-01-31", "2018-02-21", "2018-03-12", "2018-03-16"] + dates +
         [datetime.datetime.now().strftime("%Y-%m-%d")])
dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]

writingProgress = ([0/totalPages, 52/totalPages, 56/totalPages, 70/totalPages] +
                   writingProgress + [writingProgress[-1]])
testingProgress = [0, 0, 0, 0] + testingProgress + [testingProgress[-1]]
editingProgress = [0, 0, 0, 0] + editingProgress + [editingProgress[-1]]

writingProgress = np.array(writingProgress)
testingProgress = np.array(testingProgress)
editingProgress = np.array(editingProgress)

t0 = datetime.datetime(2018,  1, 31)
T  = datetime.datetime(2018, 11, 30)
linearProgress  = np.array([min((date - t0).days / (T - t0).days, 1)
                            for date in dates])
daysPerPercent = 100 / (T - t0).days



mpl.rcParams["axes.prop_cycle"] = cycler.cycler(color=lineColors)

fig = plt.figure()

ax1 = fig.gca()
lines = []
lines.extend(ax1.plot_date(dates, 100*writingProgress, ".-"))
lines.extend(ax1.plot_date(dates, 100*testingProgress, ".-"))
lines.extend(ax1.plot_date(dates, 100*editingProgress, ".-"))
lines.extend(ax1.plot_date(
    dates + [T], (100*linearProgress).tolist() + [100], "k-"))
ax1.grid()
ax1.set_xlabel("Time")
ax1.set_ylabel("Percentage")
ax1.set_title("Writing, Testing, and Editing Progress")
ax1.set_xlim(t0-0.05*(T-t0), T+0.05*(T-t0))
ax1.set_ylim(-5, 105)

ax2 = ax1.twinx()
lines.extend(ax2.plot_date(
    dates, (T - t0).days * (writingProgress-linearProgress),
    ".--", color="C3"))
ax1.legend(lines, ["Pages written", "Tests written", "Pages edited",
                   "Ideal", "Written minus ideal"])
ax2.set_ylabel("Days before schedule")
ax1.spines["right"].set_visible(False)
ax2.spines["right"].set_linewidth(1.5)
ax2.spines["right"].set_linestyle((0, (3, 2.5)))
ax2.spines["right"].set_color("C3")
ax2.yaxis.label.set_color("C3")
ax2.tick_params(axis="y", colors="C3")
ax2.set_xlim(t0-0.05*(T-t0), T+0.05*(T-t0))
ax2.set_ylim(-5, 105)

plt.show()
