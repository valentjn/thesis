#!/usr/bin/python3

import argparse
import collections
import os
import pprint
import re

def main():
  parser = argparse.ArgumentParser(
    description="Count notation LaTeX commands.")
  parser.add_argument("--count-type",
      choices=["uses", "keystrokes", "files"], default="uses",
      help="Determine what to count: Uses (default), keystrokes "
           "(occurences times length), or files.")
  parser.add_argument("--all-commands", action="store_true",
      help="Count all commands, not only the ones defined in notation.tex")
  args = parser.parse_args()
  
  texPath = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "tex")
  
  if not args.all_commands:
    notationFile = os.path.join(texPath, "notation.tex")
    with open(notationFile, "r") as f: tex = f.read()
    possibleCommands = []
    #possibleCommands += ([x[1] for x in
    #    re.findall(r"\\(re)?newcommand\*?\{\\([A-Za-z]+)\}", tex)])
    possibleCommands += ([x[1] for x in
        re.findall(r"\\newnotationcommand(\[[0-9]*\])?\{\\([A-Za-z]+)\}", tex)])
    possibleCommands += ([x[1] for x in
        re.findall(r"\\newnotationcommandoptarg(\[[^\]]*\])?\{[0-9]+\}"
               r"\{\\([A-Za-z]+)\}", tex)])
    possibleCommands.sort()
  
  isChapterFilename = lambda x: (
    (x[0].isdigit() or ((x[0] == "a") and x[1].isdigit())) and
    x.endswith(".tex"))
  texFiles = sorted([os.path.join(texPath, x) for x in os.listdir(texPath)
                     if isChapterFilename(x)])
  commandCounts = {}
  
  for texFile in texFiles:
    with open(texFile, "r") as f: tex = f.read()
    fileCommands = []
    
    for command in re.findall(r"\\([A-Za-z]+)", tex):
      if not args.all_commands:
        if command not in possibleCommands: continue
      if args.count_type == "files":
        if command in fileCommands: continue
        fileCommands.append(command)
      commandCounts[command] = commandCounts.get(command, 0) + 1
  
  notationTexFile = os.path.join(texPath, "notation.tex")
  with open(notationTexFile, "r") as f: notationTex = f.read()
  
  for command in dict(commandCounts):
    if command not in notationTex:
      del commandCounts[command]
  
  if args.count_type == "keystrokes":
    output = {x : commandCounts[x] * len(x) for x in commandCounts}
  else:
    output = commandCounts
  
  output = collections.OrderedDict(sorted(
    output.items(), key=lambda x: -x[1]))
  pprint.pprint(output)



if __name__ == "__main__":
  main()
