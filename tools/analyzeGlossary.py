#!/usr/bin/python3

import argparse
import os
import re

def main():
  parser = argparse.ArgumentParser(
    description="Analyze usage of glossary commands.")
  parser.add_argument("--count-type",
      choices=["uses", "keystrokes"], default="uses",
      help="Determine what to count: Uses (default) or keystrokes "
           "(occurences times length).")
  args = parser.parse_args()
  
  notationTexFile = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "tex", "preamble", "notation.tex")
  texPath = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "tex", "document")
  
  with open(notationTexFile, "r") as f: notationTex = f.read()
  commands = []
  commands += ([(x[1], len(x[0]) > 0) for x in
      re.findall(r"(\\hidenextnotation"
                 "\n)?"
                 r"\\makecommandnotation\{\\([A-Za-z]+)\}",
                 notationTex)])
  commands += ([(x[2], len(x[0]) > 0) for x in
      re.findall(r"(\\hidenextnotation"
                 "\n)?"
                 r"\\newnotationcommand(\[[0-9]*\])?\{\\([A-Za-z]+)\}",
                 notationTex)])
  commands += ([(x[2], len(x[0]) > 0) for x in
      re.findall(r"(\\hidenextnotation"
                 "\n)?"
                 r"\\newnotationcommandoptarg(\[[^\]]*\])?\{[0-9]+\}"
                 r"\{\\([A-Za-z]+)\}", notationTex)])
  commands = {x[0] : {"isHidden" : x[1]} for x in commands}
  
  isChapterFilename = lambda x: (
    (x[0].isdigit() or ((x[0] == "a") and x[1].isdigit())) and
    x.endswith(".tex"))
  texFiles = sorted([os.path.join(texPath, x) for x in os.listdir(texPath)
                     if isChapterFilename(x)])
  commandCounts = {}
  
  for texFile in texFiles:
    basename = os.path.basename(texFile)
    chapter = (basename[0] if basename[0].isdigit() else
               chr(64 + int(basename[1])))
    section = basename[:2]
    with open(texFile, "r") as f: tex = f.read()
    
    for command in re.findall(r"\\([A-Za-z]+)", tex):
      if command in commands:
        if command not in commandCounts:
          commandCounts[command] = {
            "total" : 0,
            "chapters" : {},
            "sections" : {},
            "isHidden" : commands[command]["isHidden"],
          }
        
        commandCounts[command]["total"] += 1
        
        if chapter not in commandCounts[command]["chapters"]:
          commandCounts[command]["chapters"][chapter] = 0
        commandCounts[command]["chapters"][chapter] += 1
        
        if section not in commandCounts[command]["sections"]:
          commandCounts[command]["sections"][section] = 0
        commandCounts[command]["sections"][section] += 1
  
  for command in dict(commandCounts):
    if command not in notationTex:
      del commandCounts[command]
  
  if args.count_type == "keystrokes":
    output = {}
    
    for command in commandCounts:
      commandCounts[command]["total"] *= len(command)
      for chapter in commandCounts[command]["chapters"]:
        commandCounts[command]["chapters"][chapter] *= len(command)
      for section in commandCounts[command]["sections"]:
        commandCounts[command]["sections"][section] *= len(command)
  
  # \name  23  3,4,5  hidden
  output = [(x, y) for x, y in commandCounts.items()]
  output.sort(key=lambda x: (x[1]["isHidden"], -len(x[1]["chapters"]), x[0]))
  output = [
    (
      "\\{}".format(x[0]),
      str(x[1]["total"]),
      ",".join(x[1]["chapters"].keys()),
      str(len(x[1]["chapters"])),
      str(len(x[1]["sections"])),
      ("hidden" if x[1]["isHidden"] else "visible"),
    )
    for x in output
  ]
  
  output.insert(
      0, ("Command", "#Occ.", "Chapters", "#Ch.", "#Sec.", "Visible"))
  lengths = [max([len(x[i]) for x in output]) for i in range(6)]
  alignments = ("<", ">", "<", ">", ">", "<")
  formatString = "  ".join(["{{:{}{}}}".format(x, y)
                            for x, y in zip(alignments, lengths)])
  output.insert(1, [x * "-" for x in lengths])
  print("\n".join([formatString.format(*x) for x in output]))



if __name__ == "__main__":
  main()
