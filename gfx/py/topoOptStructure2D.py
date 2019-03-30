#!/usr/bin/python3
# number of output figures = 8

import multiprocessing

import matplotlib as mpl
import numpy as np

from helper.figure import Figure
import helper.topo_opt



def plotPolygon(ax, trafo, faceColor, vertices):
  vertices = trafo(*np.array(vertices).T)
  ax.add_patch(mpl.patches.Polygon(vertices, fc=faceColor, ec="none"))

def plotMacroCell(ax, corner, size, parameters, model, color="k"):
  corner = np.array(corner) - 0.0008
  size   = np.array(size)   + 0.0016
  elementTrafo = (lambda x, y: np.array(
      corner + size * np.column_stack((x, y))))
  parameters = np.array(parameters).tolist()
  thresholds = [0.1, 0.98]
  
  if model in ["cross", "shearedCross"]:
    if model == "cross": parameters.append(0.5)
    a, b, theta = parameters
    if a > thresholds[1]: a = 1
    if b > thresholds[1]: b = 1
    theta = np.pi * (0.5 - theta)
    shearingTrafo = (lambda x, y: np.column_stack(
        (x + (y-0.5) * np.tan(theta), y)))
    totalTrafo = (lambda x, y: elementTrafo(*shearingTrafo(x, y).T))
    if a > thresholds[0]: plotPolygon(ax, elementTrafo, color, [
        (0, (1-a)/2),
        (1, (1-a)/2),
        (1, (1+a)/2),
        (0, (1+a)/2)])
    if b > thresholds[0]: plotPolygon(ax, totalTrafo, color, [
        ((1-b)/2, 0),
        ((1+b)/2, 0),
        ((1+b)/2, 1),
        ((1-b)/2, 1)])
  elif model in ["framedCross", "shearedFramedCross"]:
    if model == "framedCross": parameters.append(0.5)
    a, b, c, d, theta = parameters
    theta = np.pi * (0.5 - theta)
    shearingTrafo = (lambda x, y: np.column_stack(
        (x + (y-0.5) * np.tan(theta), y)))
    totalTrafo = (lambda x, y: elementTrafo(*shearingTrafo(x, y).T))
    if a > thresholds[1]: a = 1
    if b > thresholds[1]: b = 1
    if c > thresholds[1]: c = 1
    if d > thresholds[1]: d = 1
    if a > thresholds[0]:
      a = max(a, 2*thresholds[0])
      plotPolygon(ax, elementTrafo, color, [
          (0, 0),
          (1, 0),
          (1, a/2),
          (0, a/2)])
      plotPolygon(ax, elementTrafo, color, [
          (0, 1-a/2),
          (1, 1-a/2),
          (1, 1),
          (0, 1)])
    if b > thresholds[0]:
      b = max(b, 2*thresholds[0])
      plotPolygon(ax, totalTrafo, color, [
          (0,   0),
          (b/2, 0),
          (b/2, 1),
          (0,   1)])
      plotPolygon(ax, totalTrafo, color, [
          (1-b/2, 0),
          (1,     0),
          (1,     1),
          (1-b/2, 1)])
    if c > thresholds[0]:
      plotPolygon(ax, totalTrafo, color, [
          (0,     1-c/2),
          (1-c/2, 0),
          (1,     0),
          (1,     c/2),
          (c/2,   1),
          (0,     1),
          (0,     1-c/2)])
    if d > thresholds[0]:
      plotPolygon(ax, totalTrafo, color, [
          (0,     0),
          (d/2,   0),
          (1,     1-d/2),
          (1,     1),
          (1-d/2, 1),
          (0,     d/2),
          (0,     0)])
  else:
    raise ValueError("Unknown micro-cell model.")

def plotStructure(ax, h5Data, model):
  nodes, elements = h5Data["nodes"], h5Data["elements"]
  displacement = np.linalg.norm(h5Data["displacement"], ord=2, axis=1)
  colormap = mpl.cm.viridis
  #vmin, vmax = np.amin(displacement), np.amax(displacement)
  vmin, vmax = 0, 190
  normalize = mpl.colors.Normalize(vmin, vmax)
  scalarMappable = mpl.cm.ScalarMappable(norm=normalize, cmap=colormap)
  
  for i, element in enumerate(elements):
    corners = nodes[element,:]
    corner = np.amin(corners[:,:2], axis=0)
    size   = np.amax(corners[:,:2], axis=0) - corner
    parameters = h5Data["microparams"]["smart"][i,:]
    k = np.where(np.all(np.equal(corners[:,:2], corner), axis=1))[0][0]
    j = element[k]
    color = scalarMappable.to_rgba(displacement[j])
    plotMacroCell(ax, corner, size, parameters, model, color=color)
  
  ax.set_xlim(np.amin(nodes[:,0]), np.amax(nodes[:,0]))
  ax.set_ylim(np.amin(nodes[:,1]), np.amax(nodes[:,1]))
  ax.set_aspect("equal")
  ax.set_axis_off()

def plotFigure(q):
  scale = [1.2, 1.14][q % 2]
  fig = Figure.create(figsize=(3, 3), scale=scale)
  ax = fig.gca()
  
  id_ = 650 + q
  scenario = ["thesis-2d-cantilever", "thesis-2d-L"][q % 2]
  model = ["cross", "framedCross",
            "shearedCross", "shearedFramedCross"][q // 2]
  
  h5Data = helper.topo_opt.readH5(
      "./data/topoOpt/results/{}/{}.h5".format(id_, scenario))
  plotStructure(ax, h5Data, model)
  
  fig.save(graphicsNumber=q+1)



def main():
  with multiprocessing.Pool() as pool:
    pool.map(plotFigure, list(range(8)))



if __name__ == "__main__":
  main()
