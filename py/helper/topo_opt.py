#!/usr/bin/python3

import xml.etree.ElementTree as ET

import h5py
import numpy as np



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
  result = {}
  
  with h5py.File(path, "r") as f:
    result["nodes"] = np.array(f.get("Mesh/Nodes/Coordinates"))
    result["cells"] = np.array(f.get("Mesh/Elements/Connectivity")) - 1
    multiStep = f.get("Results/Mesh/MultiStep_1")
    steps = [int(x[5:]) for x in multiStep.keys() if x.startswith("Step_")]
    lastStep = multiStep.get("Step_{}".format(max(steps)))
    result["displacement"] = np.array(lastStep.get(
        "mechDisplacement/mech/Nodes/Real"))
    result["stress"] = np.array(lastStep.get(
        "mechStress/mech/Elements/Real"))
  
  return result
