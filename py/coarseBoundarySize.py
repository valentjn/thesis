#!/usr/bin/python3

import helper.grid

def formatScientific(x, precision):
  return r"\num{{{{{{:.{}e}}}}}}".format(precision).format(x)

def formatFloat(x, precision):
  return r"\num{{{{{{:.{}f}}}}}}".format(precision).format(x)

def formatInteger(x):
  return r"\num{{{:.0f}}}".format(x)

for k in range(2):
  if k == 0:
    d = 3
    ns = list(range(3, 11))
    bs = list(range(0, 6))
    formats = [
      lambda x: formatFloat(x, 1),
      lambda x: formatFloat(x, 1),
      lambda x: formatFloat(x, 2),
      lambda x: formatFloat(x, 2),
      lambda x: formatFloat(x, 2),
      lambda x: formatFloat(x, 2),
    ]
  else:
    d = 10
    ns = list(range(10, 18))
    bs = list(range(0, 6))
    formats = [
      lambda x: formatScientific(x, 1),
      lambda x: formatFloat(x, 0),
      lambda x: formatFloat(x, 0),
      lambda x: formatFloat(x, 1),
      lambda x: formatFloat(x, 1),
      lambda x: formatFloat(x, 1),
    ]
  
  interiorSizes = [helper.grid.RegularSparse(n, d).getSize() for n in ns]
  ratios = [[helper.grid.RegularSparseBoundary(ns[i], d, bs[j]).getSize() /
            interiorSizes[i] for j in range(len(bs))] for i in range(len(ns))]
  
  table = "\\\\\n".join(["&\n".join([r"$n = {}$".format(ns[i]), formatInteger(interiorSizes[i])] +
                                    [formats[j](ratios[i][j]) for j in range(len(bs))])
                         for i in range(len(ns))]) + "\\\\"
  print(table)
  print("")
