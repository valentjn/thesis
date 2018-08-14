#!/usr/bin/python3

import numpy as np

import helper.basis



def getChunks(x, n):
  for i in range(0, len(x), n): yield x[i:i + n]



p = 5
cutoffTolerance = 1e-10

origBasis = helper.basis.HierarchicalNotAKnotBSpline(p)
basis = helper.basis.NodalFundamentalTransformed(origBasis)

code = ""
maximumLevel = None
lMin = {3 : 2, 5 : 3}[p]

for l in range(lMin, 100):
  code += "}} else if (l == {}) {{\n".format(l)
  
  for i in range(1, 2**(l-1), 2):
    c, L, I = basis.getCoefficients(l, i)
    assert np.all(L == l)
    assert I[0] == 0
    cutoff = np.where(np.abs(c) < cutoffTolerance)[0]
    cutoff = (cutoff[0] if len(cutoff) > 0 else len(c))
    
    #print(l, i)
    #print(c)
    #print(L)
    #print(I)
    
    if not np.all(np.abs(c[cutoff:]) < cutoffTolerance):
      maximumLevel = l
      code += "  } else {\n"
      code += "    // l = {}, i >= {}\n".format(l, i)
      code += "    return -1;\n"
      break
    
    if i == 1:
      code += "  if (i == {}) {{\n".format(i)
    elif i < 2**(l-1)-1:
      code += "  }} else if (i == {}) {{\n".format(i)
    else:
      code += "  } else {\n"
    
    chunks = getChunks(["{:.12e}".format(x) for x in c[:cutoff]], 4)
    code += "    // l = {}, i = {}\n".format(l, i)
    code += "    coefficients = {{\n      {}\n    }};\n".format(
        ",\n      ".join([", ".join(chunk) for chunk in chunks]))
  
  code += "  }\n"
  if maximumLevel is not None: break

code += "}\n"
code = code.replace("}} else if (l == {}) {{\n".format(l), "} else {\n")
code = code.replace("// l = {},".format(l), "// l >= {},".format(l))

print(code)
