#!/usr/bin/python3
# number of output figures = 6

import mpl_toolkits
import numpy as np

from helper.figure import Figure
import helper.plot



def plotText(ax, trafo, x, y, text, width=None, height=None,
             contourColor=None, raiseText=0, **kwargs):
  if height is None:
    assert width is not None
    ax.plot(*trafo([x - width/2, x + width/2], [y, y]), "w-", clip_on=False)
  else:
    ax.plot(*trafo([x, x], [y - height/2, y + height/2]), "w-", clip_on=False)
  
  kwargs = {"color" : "w", "ha" : "center", "va" : "center", **kwargs}
  if contourColor is not None:
    text = r"\contour[32]{{{}}}{{{}}}".format(contourColor, text)
  ax.text(*trafo(x, y-0.03+raiseText), text, **kwargs)



def plot3D(ax, trafo, x, y, z, *args, **kwargs):
  x, y, z = trafo(x, y, z)
  kwargs = {"zs" : z, "clip_on" : False, **kwargs}
  ax.plot(x, y, *args, **kwargs)

def plotRectangle(ax, trafo, vertices, faceColor, edgeColor, zorder=None):
  vertices = np.column_stack(trafo(*(np.array(vertices).T)))
  poly3DCollection = mpl_toolkits.mplot3d.art3d.Poly3DCollection(
      [vertices], facecolors=[faceColor], edgecolors=[edgeColor], lw=1)
  if zorder is not None: poly3DCollection.set_sort_zpos(2)
  ax.add_collection3d(poly3DCollection)

def plotCuboid(ax, trafo, corner, size, faceColor, zorder=None):
  corner, size = np.array(corner), np.array(size)
  x, y = [0, 1, 1, 0, 0], [0, 0, 1, 1, 0]
  getFaceColor = (lambda brightness:
      helper.plot.mixColors(faceColor, 1-brightness,
                            helper.plot.mixColors("hellblau", 0.1)))
  edgeColor = helper.plot.mixColors("mittelblau", 0.8, "k")
  plotRectangle(ax, trafo, corner + size * np.array([5*[0], x, y]).T,
                getFaceColor(0.3), edgeColor, zorder=zorder)
  plotRectangle(ax, trafo, corner + size * np.array([x, 5*[0], y]).T,
                getFaceColor(0.0), edgeColor, zorder=zorder)
  plotRectangle(ax, trafo, corner + size * np.array([x, y, 5*[1]]).T,
                getFaceColor(0.2), edgeColor, zorder=zorder)

def plotText3D(ax, trafo, x, y, z, text, extent,
               contourColor=None, **kwargs):
  for t in range(3):
    if not np.isnan(extent[t]):
      xyz = [[x, x], [y, y], [z, z]]
      xyz[t][0] -= extent[t]/2
      xyz[t][1] += extent[t]/2
      plot3D(ax, trafo, *xyz, "w-", clip_on=False,
             zorder=40, solid_capstyle="butt")
  
  kwargs = {"color" : "w", "ha" : "center", "va" : "center",
            "zorder" : 50, **kwargs}
  if contourColor is not None:
    text = r"\contour[32]{{{}}}{{{}}}".format(contourColor, text)
  ax.text(*trafo(x, y, z-0.01), text, **kwargs)



def main():
  a, b, c, d = 0.4, 0.3, 0.3, 0.4
  theta = 20/180*np.pi
  
  kwargs = (lambda r: {
    "color" : helper.plot.mixColors("mittelblau", 1-0.1*r),
  })
  contourColors = (lambda r: "mittelblau!{}".format(100-10*r))
  
  for q in range(4):
    fig = Figure.create(figsize=(5, 3), scale=0.59, preamble=r"""
\contourlength{2.5pt}
""")
    ax = fig.gca()
    
    if q in [0, 2]:
      trafo = (lambda x, y: (x, y))
    else:
      trafo = (lambda x, y: (np.array(x) + np.array(y) * np.tan(-theta),
                             np.array(y)))
    
    if q < 2:
      ax.fill(*trafo([0, 1, 1, 0, 0],
                     [(1-a)/2, (1-a)/2, (1+a)/2, (1+a)/2, (1-a)/2]),
              **kwargs(1))
      ax.fill(*trafo([(1-b)/2, (1+b)/2, (1+b)/2, (1-b)/2, (1-b)/2],
                     [0, 0, 1, 1, 0]), **kwargs(0))
      plotText(ax, trafo, 0.8, 0.5,   r"$x_1$", height=a,
               contourColor=contourColors(1))
      plotText(ax, trafo, 0.5, 0.2,   r"$x_2$", width=b,
               contourColor=contourColors(0))
    else:
      ax.fill(*trafo([0, 1, 1, 0, 0], [0, 0, a/2, a/2, 0]), **kwargs(1))
      ax.fill(*trafo([0, 1, 1, 0, 0], [1-a/2, 1-a/2, 1, 1, 1-b/2]),
              **kwargs(1))
      ax.fill(*trafo([0, b/2, b/2, 0, 0], [0, 0, 1, 1, 0]), **kwargs(0))
      ax.fill(*trafo([1-b/2, 1, 1, 1-b/2, 1-b/2], [0, 0, 1, 1, 0]),
              **kwargs(0))
      ax.fill(*trafo([0, 1-c/2, 1, 1, c/2, 0, 0],
                     [1-c/2, 0, 0, c/2, 1, 1, 1-c/2]), **kwargs(2))
      ax.fill(*trafo([0, d/2, 1, 1, 1-d/2, 0, 0],
                     [0, 0, 1-d/2, 1, 1, d/2, 0]), **kwargs(3))
      plotText(ax, trafo, 0.5,   a/4,   r"$x_1/2$",         height=a/2,
               contourColor=contourColors(1), raiseText=0.025)
      plotText(ax, trafo, 0.5,   1-a/4, r"$x_1/2$",         height=a/2,
               contourColor=contourColors(1), raiseText=0.015)
      plotText(ax, trafo, b/4,   0.5,   r"$\frac{x_2}{2}$", width=b/2,
               contourColor=contourColors(0))
      plotText(ax, trafo, 1-b/4, 0.5,   r"$\frac{x_2}{2}$", width=b/2,
               contourColor=contourColors(0))
      plotText(ax, trafo, 0.7,   0.3,   r"$x_3$",           width=c,
               contourColor=contourColors(2))
      plotText(ax, trafo, 0.7,   0.7,   r"$x_4$",           width=d,
               contourColor=contourColors(3))
    
    x, y = trafo([0, 1, 1, 0, 0], [0, 0, 1, 1, 0])
    ax.plot(x, y, "k-", clip_on=False)
    
    if q in [1, 3]:
      radius = 0.5
      center = trafo(1, 0.5)
      tt = np.linspace(np.pi/2, np.pi/2+theta, 100)
      xx, yy = center[0]+radius*np.cos(tt), center[1]+radius*np.sin(tt)
      ax.plot(xx, yy, "k--", clip_on=False)
      ax.plot(2*[center[0]], [center[1], center[1]+radius], "k--",
              clip_on=False)
      t = np.pi/2 + theta/2
      ax.text(
          center[0]+0.8*radius*np.cos(t), center[1]+0.8*radius*np.sin(t),
          r"$\theta", ha="center", va="center")
    
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    
    fig.save()
  
  
  
  a, b, c = 0.2, 0.3, 0.4
  theta1, theta2 = 20/180*np.pi, 15/180*np.pi
  
  getFaceColor = (lambda brightness:
      helper.plot.mixColors("mittelblau", 1-brightness,
                            helper.plot.mixColors("hellblau", 0.1)))
  trafos = []
  
  for q in range(2):
    fig = Figure.create(figsize=(4, 4), scale=[0.62, 0.8][q])
    ax = fig.add_subplot(111, projection="3d")
    
    if q == 0:
      trafo = (lambda x, y, z: (x, y, z))
    else:
      trafo = (lambda x, y, z: (np.array(x) + np.array(z) * np.tan(theta1),
                                np.array(y) + np.array(z) * np.tan(theta2),
                                np.array(z)))
    trafos.append(trafo)
    
    plotCuboid(ax, trafo, [(1+c)/2, (1-a)/2, (1-a)/2], [(1-c)/2, a, a],
               "mittelblau", zorder=0)
    plotCuboid(ax, trafo, [(1-b)/2, (1+c)/2, (1-b)/2], [b, (1-c)/2, b],
               "mittelblau", zorder=1)
    plotCuboid(ax, trafo, [(1-c)/2, (1-c)/2, 0],       [c, c,       1],
               "mittelblau", zorder=2)
    plotCuboid(ax, trafo, [0,       (1-a)/2, (1-a)/2], [(1-c)/2, a, a],
               "mittelblau", zorder=3)
    plotCuboid(ax, trafo, [(1-b)/2, 0,       (1-b)/2], [b, (1-c)/2, b],
               "mittelblau", zorder=4)
    
    plotText3D(ax, trafo, 0, 0.5, 0.5, r"$x_1$", [np.nan, a, a],
               contourColor="mittelblau!67")
    plotText3D(ax, trafo, 0.5, 0, 0.5, r"$x_2$", [b, np.nan, b],
               contourColor="mittelblau!100")
    plotText3D(ax, trafo, 0.5, 0.5, 1, r"$x_3$", [c, c, np.nan],
               contourColor="mittelblau!78")
    
    if q == 1:
      trafos.insert(1, (lambda x, y, z: (
          np.array(x) + np.array(z) * np.tan(theta1),
          np.array(y), np.array(z))))
    
    for j, curTrafo in enumerate(trafos):
      lineStyle = ("k-" if q == 0 else ["k--", "k:", "k-"][j])
      
      for corner in [[1, 1, 0], [1, 0, 1], [0, 1, 1], [0, 0, 0]]:
        zOrder = (-10 if corner == [1, 1, 0] else 100)
        plot3D(ax, curTrafo,
              [corner[0], 1-corner[0]], 2*[corner[1]], 2*[corner[2]],
              lineStyle, zOrder=zOrder)
        plot3D(ax, curTrafo,
              2*[corner[0]], [corner[1], 1-corner[1]], 2*[corner[2]],
              lineStyle, zOrder=zOrder)
        plot3D(ax, curTrafo,
              2*[corner[0]], 2*[corner[1]], [corner[2], 1-corner[2]],
              lineStyle, zOrder=zOrder)
    
    if q == 1:
      center = np.array([0, 1, 0])
      
      radius = 0.7
      tt = np.linspace(np.pi/2-theta1, np.pi/2, 100)
      xx = center[0] + radius * np.cos(tt)
      yy = np.ones_like(tt)
      zz = center[2] + radius * np.sin(tt)
      ax.plot(xx, yy, "k--", zs=zz, clip_on=False)
      t = np.pi/2 - theta1/2
      ax.text(
          center[0]+0.8*radius*np.cos(t), 1, center[2]+0.8*radius*np.sin(t),
          r"\contour{mittelblau!10}{$\theta_1$}",
          ha="center", va="center", zorder=200)
      
      radius = 0.9
      tt = np.linspace(np.pi/2, np.pi/2+theta2, 100)
      xx = np.zeros_like(tt)
      yy = center[1] + radius * np.cos(tt)
      zz = center[2] + radius * np.sin(tt)
      plot3D(ax, trafo, xx, yy, zz, "k:")
      t = np.pi/2 + theta2/2
      ax.text(*trafo(0, center[1]+0.85*radius*np.cos(t),
                     center[2]+0.85*radius*np.sin(t)),
          r"\contour{mittelblau!10}{$\theta_2$}",
          ha="center", va="center", zorder=200)
    
    ax.set_axis_off()
    ax.view_init(30, 235)
    x, y, z = trafo([0, 1], [0, 1], [0, 1])
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min(y), max(y))
    ax.set_zlim(min(z), max(z))
    helper.plot.setEqual3DAxes(ax)
    
    fig.save()



if __name__ == "__main__":
  main()
