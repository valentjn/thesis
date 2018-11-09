#!/usr/bin/python3
# number of output figures = 129

import multiprocessing

import numpy as np
import scipy.linalg

from helper.figure import Figure
import helper.grid
import helper.plot



def createRotationMatrix(axis, angle):
  return scipy.linalg.expm(np.cross(
    np.eye(3), axis / scipy.linalg.norm(axis) * angle * np.pi / 180))

def rotate(matrix, x, y, z):
  rotatedVectors = np.dot(matrix, np.row_stack((x, y, z)) - 0.5) + 0.5
  return rotatedVectors[0,:], rotatedVectors[1,:], rotatedVectors[2,:]

def drawImage(imageNumber):
  angle = startAngle + numberOfRevolutions * 360 * imageNumber / numberOfImages
  
  fig = Figure.create(figsize=(1, 1.2), scale=1.5)
  ax = fig.add_subplot(111, projection="3d")
  
  grid = helper.grid.RegularSparseBoundary(n, d, b)
  X, _, _ = grid.generate()
  
  prerotationMatrix = createRotationMatrix(prerotationAxis, prorotationAngle)
  viewRotationMatrix1 = createRotationMatrix([1, 0, 0], elevation)
  viewRotationMatrix2 = createRotationMatrix([0, 0, 1], angle)
  viewRotationMatrix = np.dot(viewRotationMatrix2, viewRotationMatrix1)
  rotationMatrix = np.dot(viewRotationMatrix, prerotationMatrix)
  
  xs = [[0, 1, 1, 0, 0], [0, 1, 1, 0, 0], [0, 0], [1, 1], [0, 0], [1, 1]]
  ys = [[0, 0, 1, 1, 0], [0, 0, 1, 1, 0], [0, 0], [0, 0], [1, 1], [1, 1]]
  zs = [[0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 1], [0, 1], [0, 1], [0, 1]]
  pointsAndLines = []
  
  for x, y, z in zip(xs, ys, zs):
    for i in range(len(x) - 1):
      xx = np.linspace(x[i], x[i + 1], 10)
      yy = np.linspace(y[i], y[i + 1], 10)
      zz = np.linspace(z[i], z[i + 1], 10)
      for j in range(xx.shape[0] - 1):
        xCur, yCur, zCur = xx[j:j+2], yy[j:j+2], zz[j:j+2]
        xCur, yCur, zCur = rotate(rotationMatrix, xCur, yCur, zCur)
        pointsAndLines.append({
          "type" : "line",
          "key" : xCur[0],
          "data" : (xCur, yCur, zCur),
        })
  
  x, y, z = X[:,0], X[:,1], X[:,2]
  x, y, z = rotate(rotationMatrix, x, y, z)
  pointsAndLines += [
    {"type" : "point", "key" : xCur, "data" : (xCur, yCur, zCur)}
    for xCur, yCur, zCur in zip(x, y, z)
  ]
  
  pointsAndLines.sort(key=lambda x: x["key"])
  
  for pointOrLine in pointsAndLines:
    xCur, yCur, zCur = pointOrLine["data"]
    
    if pointOrLine["type"] == "point":
      markerSize = 2 + 1.0 * xCur**2
      brightness = getBrightness(xCur)
      color = helper.plot.mixColors(colorBase, 1-brightness)
      ax.plot([xCur], [yCur], zs=[zCur], marker="o", ls="", ms=markerSize,
              color=color)
    else:
      brightness = getBrightness(xCur[0])
      color = helper.plot.mixColors(colorBase, 1-brightness)
      ax.plot(xCur, yCur, zs=zCur, ls="-", marker="", color=color)
  
  ax.set_xlim(*xLim)
  ax.set_ylim(*yLim)
  ax.set_zlim(*zLim)
  helper.plot.setEqual3DAxes(ax)
  ax.set_axis_off()
  
  ax.view_init(0, 0)
  #ax.view_init(elevation, angle)
  fig.save(graphicsNumber=imageNumber+1, crop=False,
           tightLayout={"pad" : 0, "h_pad" : 0, "w_pad" : 0})



numberOfImages = 129
numberOfRevolutions = 1.0
startAngle = 30
elevation = 20
prerotationAxis = [0, 1, 0]
prorotationAngle = 20
xLim = [-0.3, 1.3]
#yLim = [0, 1]
yLim = [-0.3, 1.3]
zLim = [-0.3, 1.3]
n = 4
d = 3
b = 1
colorBase = "anthrazit"
colorDarkBrightness = 0.3
colorLightBrightness = 0.7

colorDark = helper.plot.mixColors(colorBase, 1-colorDarkBrightness)
getBrightness = (lambda x: ((x - xLim[0]) / (xLim[1] - xLim[0])) *
                          (colorDarkBrightness - colorLightBrightness) + colorLightBrightness)

with multiprocessing.Pool() as pool:
  pool.map(drawImage, range(numberOfImages))
