#!/usr/bin/python3
# dependencies = SG++

import helper.function
import helper.hpc

import numpy as np

import pysgpp



@helper.hpc.cacheToFile
@helper.hpc.executeRemotely
def optimizeFuzzy(fStr, d, gridType, gridGenerationType,
                  N, p, gamma, n, m, inputIndex, seed):
  import json
  import os
  import subprocess
  
  program = os.path.join(
      os.environ["BUILD_DIR"], "..", "cpp", "optimizeFuzzy")
  args = [program, "f={}".format(fStr), "d={}".format(d),
          "grid={}".format(gridType), "gridGen={}".format(gridGenerationType),
          "N={}".format(N), "p={}".format(p), "gamma={}".format(gamma),
          "n={}".format(n), "m={}".format(m), "input={}".format(inputIndex),
          "seed={}".format(seed)]
  env = dict(os.environ)
  env["OMP_NUM_THREADS"] = "48"
  
  try:
    process = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        check=True)
  except subprocess.CalledProcessError as exception:
    print(exception.stderr.decode())
    raise exception
  
  result = json.loads(process.stdout.decode())
  return result



def calculateRelativeL2FuzzyError(
    xDataExact, alphaDataExact, xDataAppr, alphaDataAppr):
  fuzzyIntervalExact = pysgpp.OptInterpolatedFuzzyInterval(
      helper.function.np2sgpp(np.array(xDataExact)),
      helper.function.np2sgpp(np.array(alphaDataExact)))
  fuzzyIntervalAppr = pysgpp.OptInterpolatedFuzzyInterval(
      helper.function.np2sgpp(np.array(xDataAppr)),
      helper.function.np2sgpp(np.array(alphaDataAppr)))
  return fuzzyIntervalExact.approximateRelativeL2Error(fuzzyIntervalAppr)
