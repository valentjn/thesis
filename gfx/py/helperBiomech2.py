#!/usr/bin/python3

import numpy as np

import helper.grid
import helper.hpc



def applyBiomech2Scattered(action, gridType, basisType, p, forceLoad, XX):
  XX = tuple(tuple(xx) for xx in np.array(XX))
  return _applyBiomech2Scattered(
      action, gridType, basisType, p, forceLoad, XX)

@helper.hpc.cacheToFile
def _applyBiomech2Scattered(action, gridType, basisType, p, forceLoad, XX):
  return _applyBiomech2(action, gridType, basisType, p, forceLoad, XX)

@helper.hpc.cacheToFile
def applyBiomech2MeshGrid(action, gridType, basisType, p, forceLoad, nn):
  _, _, XX = helper.grid.generateMeshGrid(nn)
  return _applyBiomech2(action, gridType, basisType, p, forceLoad, XX)

@helper.hpc.cacheToFile
def applyBiomech2MonteCarlo(action, gridType, basisType, p, forceLoad, NN):
  XX = getMonteCarloPoints(NN)
  return _applyBiomech2(action, gridType, basisType, p, forceLoad, XX)

def _applyBiomech2(action, gridType, basisType, p, forceLoad, XX):
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

def matrix2str(XX):
  XX = np.array(XX)
  return "{} {} {}".format(
      *XX.shape, " ".join([str(x) for x in XX.flatten().tolist()]))

def getMonteCarloPoints(NN):
  np.random.seed(342)
  d = 2
  XX = np.random.rand(NN, d)
  return XX

def computeRelativeL2Error(YYExact, YYAppr):
  NN = YYExact.shape[0]
  error = np.sqrt(np.sum((YYExact - YYAppr)**2, axis=0) / NN)
  error = error / np.sqrt(np.sum(YYExact**2, axis=0) / NN)
  return error
