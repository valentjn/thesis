#!/usr/bin/python3

import enum
import xml.etree.ElementTree as ET

import numpy as np

import helper.function



def readDensityFile(path):
  tree = ET.parse(path)
  cfsErsatzMaterial = tree.getroot()
  
  header = cfsErsatzMaterial.findall("./header")[0]
  mesh = header.findall("./mesh")[0]
  M1 = int(mesh.attrib["x"])
  M2 = int(mesh.attrib["y"])
  M3 = int(mesh.attrib["z"])
  d = len(header.findall("./design"))
  result = np.full((M1, M2, M3, d, 2), np.nan)
  
  elements = cfsErsatzMaterial.findall("./set/element")
  typePrefix = "microparam"
  
  for element in elements:
    j = int(element.attrib["nr"]) - 1
    j1 = j % M1
    j2 = (j // M1) % M2
    j3 = (j // (M1 * M2)) % M3
    type_ = element.attrib["type"]
    assert type_.startswith(typePrefix)
    t = int(type_[len(typePrefix):]) - 1
    result[j1,j2,j3,t,0] = float(element.attrib["design"])
    result[j1,j2,j3,t,1] = float(element.attrib["physical"])
  
  assert not np.any(np.isnan(result))
  return result



def readH5(path):
  # local import as h5py triggers a warning when importing on Python 3.6
  import h5py
  
  result = {}
  
  with h5py.File(path, "r") as f:
    result["nodes"] = np.array(f.get("Mesh/Nodes/Coordinates"))
    result["elements"] = np.array(f.get("Mesh/Elements/Connectivity")) - 1
    multiStep = f.get("Results/Mesh/MultiStep_1")
    steps = [int(x[5:]) for x in multiStep.keys() if x.startswith("Step_")]
    lastStep = multiStep.get("Step_{}".format(max(steps)))
    result["displacement"] = np.array(lastStep.get(
        "mechDisplacement/mech/Nodes/Real"))
    result["stress"] = np.array(lastStep.get(
        "mechStress/mech/Elements/Real"))
    microparams = [
        int(x[17:-6]) for x in lastStep.keys()
        if x.startswith("design_microparam") and x.endswith("_plain")]
    d = max(microparams)
    result["microparams"] = {
      "plain" : np.column_stack(
          lastStep.get("design_microparam{}_plain/"
                       "mech/Elements/Real".format(t))
          for t in range(1, d+1)),
      "smart" : np.column_stack(
          lastStep.get("design_microparam{}_smart/"
                       "mech/Elements/Real".format(t))
          for t in range(1, d+1)),
    }
  
  return result



class Stats(object):
  class Distribution(enum.Enum):
    uniform        = enum.auto()
    clenshawCurtis = enum.auto()
    
    @staticmethod
    def fromString(s):
      return {
        "uniform" : Stats.Distribution.uniform,
        "cc"      : Stats.Distribution.clenshawCurtis,
      }[s]
  
  class Transformation(enum.Enum):
    normal   = enum.auto()
    cholesky = enum.auto()
    
    @staticmethod
    def fromString(s):
      return {
        "normal"   : Stats.Transformation.normal,
        "cholesky" : Stats.Transformation.cholesky,
      }[s]
  
  def __init__(self):
    self.X, self.L, self.I = None, None, None
    self.fX = None
    self.distribution = None
    self.transformation = None
    self.bounds = None
    self.isHierarchized = None
    self.interpolant = None
  
  @property
  def N(self): return self.X.shape[0]
  @property
  def d(self): return self.X.shape[1]
  @property
  def m(self): return self.fX.shape[1]
  
  @staticmethod
  def _popField(fields):
    field = fields[0]
    del fields[0]
    return field
  
  def load(self, path):
    with open(path, "r") as f:
      firstLine = f.readline()
      secondLine = f.readline()
    
    fields = firstLine[:-1].split("\t")
    
    field = Stats._popField(fields)
    versionPrefix = "sparsegrid_ver"
    assert field.startswith(versionPrefix)
    version = int(field[len(versionPrefix):])
    assert version >= 1
    
    N = int(Stats._popField(fields))
    assert N >= 0
    
    d = int(Stats._popField(fields))
    assert d >= 0
    
    m = int(Stats._popField(fields))
    assert m >= 0
    
    distribution = (Stats._popField(fields) if version >= 3 else "uniform")
    distribution = Stats.Distribution.fromString(distribution)
    
    transformation = (Stats._popField(fields) if version >= 4 else "normal")
    transformation = Stats.Transformation.fromString(transformation)
    
    isHierarchized = Stats._popField(fields)
    assert isHierarchized in ["hierarchized", "not_hierarchized"]
    isHierarchized = (isHierarchized == "hierarchized")
    
    notation = Stats._popField(fields)
    assert notation == "voigt"
    
    assert len(fields) == 0
    
    if version >= 2:
      bounds = np.fromstring(secondLine, sep="\t")
      bounds = np.reshape(bounds, (d, 2)).T
      skipRows = 2
    else:
      bounds = np.vstack((np.zeros((d,)), np.ones((d,))))
      skipRows = 1
    
    data = np.loadtxt(path, skiprows=skipRows)
    assert data.shape[0] == N
    assert data.shape[1] == 2*d + m
    L, I, fX = data[:,:d], data[:,d:2*d], data[:,2*d:]
    L, I = L.astype(np.uint64), I.astype(np.uint64)
    
    self.distribution = distribution
    self.transformation = transformation
    self.bounds = bounds
    self.isHierarchized = isHierarchized
    self.L, self.I = L, I
    self.fX = np.full((N, m), np.nan)
    self.updateX()
    self.fX = fX
  
  def loadScattered(self, path):
    with open(path, "r") as f:
      firstLine = f.readline()
      secondLine = f.readline()
    
    fields = firstLine[:-1].split("\t")
    
    field = Stats._popField(fields)
    versionPrefix = "scattereddata_ver"
    assert field.startswith(versionPrefix)
    version = int(field[len(versionPrefix):])
    assert version >= 1
    
    N = int(Stats._popField(fields))
    assert N >= 0
    
    d = int(Stats._popField(fields))
    assert d >= 0
    
    m = int(Stats._popField(fields))
    assert m >= 0
    
    notation = Stats._popField(fields)
    assert notation == "voigt"
    
    assert len(fields) == 0
    
    data = np.loadtxt(path, skiprows=1)
    assert data.shape[0] == N
    assert data.shape[1] == d + m
    X, fX = data[:,:d], data[:,d:]
    
    self.distribution = None
    self.transformation = Stats.Transformation.fromString("normal")
    self.bounds = None
    self.isHierarchized = False
    self.L, self.I = None, None
    self.X = X
    self.fX = fX
  
  def updateX(self):
    h = 1 / 2**self.L
    
    if self.distribution == Stats.Distribution.clenshawCurtis:
      self.X = (np.cos(np.pi * (1 - self.I * h)) + 1) / 2
    else:
      self.X = self.I * h
    
    newBounds = self.bounds
    self.bounds = np.vstack((np.zeros((self.d,)), np.ones((self.d,))))
    self.changeBounds(newBounds)
  
  def convertDomainToGridCoords(self, XX):
    return (XX - self.bounds[0,:]) / (self.bounds[1,:] - self.bounds[0,:])
  
  def convertGridToDomainCoords(self, XX):
    return self.bounds[0,:] + XX * (self.bounds[1,:] - self.bounds[0,:])
  
  def changeBounds(self, newBounds):
    self.X = self.convertDomainToGridCoords(self.X)
    self.bounds = newBounds
    self.X = self.convertGridToDomainCoords(self.X)
    self.fX = np.full(self.fX.shape, np.nan)
    self.interpolant = None
  
  def transform(self, newTransformation):
    self.fX = Stats.transformValues(self.fX, self.transformation,
                                    newTransformation)
    self.transformation = newTransformation
  
  @staticmethod
  def transformValues(fX, oldTransformation, newTransformation):
    m = fX.shape[1]
    
    if oldTransformation == newTransformation:
      fXNew = fX[:,:-1]
    elif ((oldTransformation == Stats.Transformation.normal) and
          (newTransformation == Stats.Transformation.cholesky)):
      E = Stats.pumpElasticityTensor(fX)
      R = np.transpose(np.linalg.cholesky(E), (0, 2, 1))
      fXNew = Stats.flattenElasticityTensor(R, m)
    elif ((oldTransformation == Stats.Transformation.cholesky) and
          (newTransformation == Stats.Transformation.normal)):
      R = np.triu(Stats.pumpElasticityTensor(fX))
      RT = np.transpose(R, (0, 2, 1))
      E = np.einsum("qij,qjk->qik", RT, R)
      fXNew = Stats.flattenElasticityTensor(E, m)
    else:
      raise ValueError("Unknown old/new transformation combination.")
    
    fXNew = np.hstack((fXNew, fX[:,[-1]]))
    return fXNew
  
  @staticmethod
  def pumpElasticityTensor(fX):
    N, m = fX.shape
    assert m in [7, 10, 22]
    
    if m == 7:
      E = np.reshape(fX[:,[0, 1, 2,
                           1, 3, 4,
                           2, 4, 5]], (N, 3, 3))
    elif m == 10:
      E = np.zeros((N, 36))
      E[:,[0, 1, 2, 6, 7, 8, 12, 13, 14, 21, 28, 35]] = \
          fX[:,[0, 1, 2, 1, 3, 4, 2, 4, 5, 6, 7, 8]]
      E = np.reshape(E, (N, 6, 6))
    else:
      E = np.reshape(fX[:,[ 0,  1,  2,  3,  4,  5,
                            1,  6,  7,  8,  9, 10,
                            2,  7, 11, 12, 13, 14,
                            3,  8, 12, 15, 16, 17,
                            4,  9, 13, 16, 18, 19,
                            5, 10, 14, 17, 19, 20]], (N, 6, 6))
    
    return E
  
  @staticmethod
  def flattenElasticityTensor(E, m):
    N = E.shape[0]
    assert m in [7, 10, 22]
    
    if m == 7:
      E = np.reshape(E, (N, 9))
      fX = E[:,[0, 1, 2, 4, 5, 8]]
    elif m == 10:
      E = np.reshape(E, (N, 36))
      fX = E[:,[0, 1, 2, 7, 8, 14, 21, 28, 35]]
    else:
      E = np.reshape(E, (N, 36))
      fX = E[:,[0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11,
                14, 15, 16, 17, 21, 22, 23, 28, 29, 35]]
    
    return fX
  
  @staticmethod
  def getSmallestEigenvalues(fX):
    E = Stats.pumpElasticityTensor(fX)
    eigenvalues, _ = np.linalg.eig(E)
    eigenvalues = np.amin(eigenvalues, axis=1)
    return eigenvalues
  
  def updateInterpolant(self, basis):
    self.interpolant = helper.function.Interpolant(
        basis, self.convertDomainToGridCoords(self.X),
        self.L, self.I, None, aX=self.fX)
  
  def hierarchize(self, basis):
    assert not self.isHierarchized
    assert not np.any(np.isnan(self.fX))
    self.interpolant = helper.function.Interpolant(
        basis, self.convertDomainToGridCoords(self.X),
        self.L, self.I, self.fX)
    aX = self.interpolant.aX
    assert aX.shape[0] == self.N
    assert aX.shape[1] == self.m
    self.fX = aX
    self.isHierarchized = True
  
  def evaluate(self, XX):
    assert self.isHierarchized
    XXsg = self.convertDomainToGridCoords(XX)
    fXX = self.interpolant.evaluate(XXsg)
    return fXX
