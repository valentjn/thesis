#!/usr/bin/python3

import collections
import os
import pprint
import re

if __name__ == "__main__":
  texPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "tex")
  isDigit = lambda x: (48 <= ord(x) <= 57)
  isChapter = lambda x: ((isDigit(x[0]) or
                         ((x[0] == "a") and isDigit(x[1]))) and x.endswith(".tex"))
  
  texFiles = sorted([os.path.join(texPath, x) for x in os.listdir(texPath)
                     if isChapter(x)])
  commandCounts = {}
  
  for texFile in texFiles:
    with open(texFile, "r") as f: tex = f.read()
    for command in re.findall(r"\\([A-Za-z]+)", tex):    
      commandCounts[command] = commandCounts.get(command, 0) + 1
  
  notationTexFile = os.path.join(texPath, "notation.tex")
  with open(notationTexFile, "r") as f: notationTex = f.read()
  
  for command in dict(commandCounts):
    if command not in notationTex:
      del commandCounts[command]
  
  commandKeystrokes = {x : commandCounts[x] * len(x) for x in commandCounts}
  commandKeystrokes = collections.OrderedDict(sorted(commandKeystrokes.items(),
                                                     key=lambda x: -x[1]))
  pprint.pprint(commandKeystrokes)
