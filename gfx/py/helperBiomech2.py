#!/usr/bin/python3

import numpy as np



def matrix2str(XX):
  XX = np.array(XX)
  return "{} {} {}".format(
      *XX.shape, " ".join([str(x) for x in XX.flatten().tolist()]))

def applyBiomech2(action, gridType, basisType, p, forceLoad, XX):
  import json
  import os
  import subprocess
  
  program = os.path.join(
      os.environ["BUILD_DIR"], "..", "cpp", "applyBiomech2")
  args = [program, "action={}".format(action), "gridType={}".format(gridType),
          "basisType={}".format(basisType), "p={}".format(p),
          "forceLoad={}".format(forceLoad)]
  stdin = (matrix2str(XX).encode() if XX is not None else None)
  process = subprocess.Popen(
      args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
      stderr=subprocess.DEVNULL)
  stdout, _ = process.communicate(input=stdin)
  assert process.returncode == 0, "applyBiomech2 terminated unsuccessfully."
  result = np.array(json.loads(stdout.decode()))
  return result

def computeRelativeL2Error(YYExact, YYAppr):
  NN = YYExact.shape[0]
  error = np.sqrt(np.sum((YYExact - YYAppr)**2, axis=0) / NN)
  error = error / np.sqrt(np.sum(YYExact**2, axis=0) / NN)
  return error
