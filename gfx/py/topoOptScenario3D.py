#!/usr/bin/python3
# number of output figures = 2



# HACK
# important: remove this as soon as
# https://github.com/matplotlib/matplotlib/pull/9990 has been published
# in the release (via pip3)
import inspect
import textwrap
import warnings
import mpl_toolkits.mplot3d.axes3d
import matplotlib.colors as mcolors
from matplotlib.tri.triangulation import Triangulation
from mpl_toolkits.mplot3d import art3d, proj3d
from matplotlib.colors import Normalize, LightSource

source = inspect.getsource(mpl_toolkits.mplot3d.axes3d.Axes3D._shade_colors)
source = textwrap.dedent(source)
snippetsFound = False
snippetSearch1  = "(self, color, normals)"
snippetReplace1 = "(self, color, normals, lightsource=None)"
if snippetSearch1 in source:
  source = source.replace(snippetSearch1, snippetReplace1)
  snippetsFound = True
else:
  warnings.warn("Lightning hack 1 not applied.")
snippetSearch2 = """
    shade = np.array([np.dot(n / proj3d.mod(n), [-1, -1, 0.5])"""
snippetReplace2 = """
    if lightsource is None:
        # chosen for backwards-compatibility
        lightsource = LightSource(azdeg=225, altdeg=19.4712)
    
    shade = np.array([np.dot(n / proj3d.mod(n), lightsource.direction)"""
if snippetSearch2 in source:
  source = source.replace(snippetSearch2, snippetReplace2)
  snippetsFound = True
else:
  warnings.warn("Lightning hack 2 not applied.")
if snippetsFound:
  exec(source)
  mpl_toolkits.mplot3d.axes3d.Axes3D._shade_colors = _shade_colors

source = inspect.getsource(mpl_toolkits.mplot3d.axes3d.Axes3D.plot_trisurf)
source = textwrap.dedent(source)
snippetSearch3  = "colset = self._shade_colors(color, normals)"
snippetReplace3 = "colset = self._shade_colors(color, normals, lightsource)"
if snippetSearch3 in source:
  source = source.replace(snippetSearch3, snippetReplace3)
  exec(source)
  mpl_toolkits.mplot3d.axes3d.Axes3D.plot_trisurf = plot_trisurf
else:
  warnings.warn("Lightning hack 3 not applied.")



import numpy as np
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d
import skimage

from helper.figure import Figure
import helper.plot
import helper.topo_opt



def computeVolume(s1, s2, s3):
  if not np.isscalar(s1):
    volume = np.array([computeVolume(x1, x2, x3)
                       for x1, x2, x3 in zip(s1, s2, s3)])
    return volume
  
  volume = s1**2 + s2**2 + s3**2
  
  if (s1 >= s2) and (s1 >= s3):
    volume -= (s1*s2**2 + s1*s3**2)
  elif (s2 >= s1) and (s2 >= s3):
    volume -= (s2*s3**2 + s2*s1**2)
  else:
    assert (s3 >= s1) and (s3 >= s2)
    volume -= (s3*s1**2 + s3*s2**2)
  
  return volume



def main():
  for q in range(2):
    if q == 0:
      size = np.array([1, 1, 1])
      forcePoint = [0.75, 0.215]
      forceLength = 0.15
      h5Path = "./data/topoOpt/503/mech-3d.h5"
      nn = np.array((20, 20, 20))
    else:
      size = np.array([2, 2, 1])
      forcePoint = [0.5, 0.4]
      forceLength = 0.2
      h5Path = "./data/topoOpt/636/thesis-3d-centerload.h5"
      nn = np.array((20, 20, 10))
    
    fig = Figure.create(figsize=(3, 3), scale=1.2)
    
    
    
    ax0 = fig.add_subplot(111, label="ax0")
    ax0.plot(forcePoint[0], forcePoint[1], "k.")
    helper.plot.plotArrow(
        ax0, forcePoint, [forcePoint[0], forcePoint[1] - forceLength],
        scaleHead=0.7)
    ax0.text(forcePoint[0] + 0.02, forcePoint[1] - 0.5 * forceLength,
            r"$\force$", ha="left", va="center")
    ax0.set_xlim(0, 1)
    ax0.set_ylim(0, 1)
    ax0.set_axis_off()
    
    
    
    ax = fig.add_subplot(111, projection="3d", label="ax1")
    
    data = helper.topo_opt.readH5(h5Path)
    microparams = data["microparams"]["smart"]
    VV = computeVolume(*microparams[:,:3].T)
    VV = np.transpose(np.reshape(VV, nn[::-1]), [2, 1, 0])
    if q == 0: VV = np.flip(VV, axis=2)
    
    if q == 0:
      eps = 0.007
      verticess = [[(0, 0, eps), (0, 1-eps, eps), (0, 1-eps, 1), (0, 0, 1)]]
      zOrders = [-20]
    else:
      bcSize = 0.2
      eps = 0.01
      verticess = [
          [(0, 0, eps), (0, bcSize, eps),
           (0, bcSize, bcSize), (0, 0, bcSize)],
          [(0, size[1], eps), (0, size[1]-bcSize, eps),
           (0, size[1]-bcSize, bcSize), (0, size[1], bcSize)],
          [(size[0], 0, eps), (size[0], bcSize, eps),
           (size[0], bcSize, bcSize), (size[0], 0, bcSize)],
          [(size[0], size[1], eps), (size[0], size[1]-bcSize, eps),
           (size[0], size[1]-bcSize, bcSize), (size[0], size[1], bcSize)],
          
          [(0, 0, eps), (bcSize, 0, eps),
           (bcSize, 0, bcSize), (0, 0, bcSize)],
          [(size[0], 0, eps), (size[0]-bcSize, 0, eps),
           (size[0]-bcSize, 0, bcSize), (size[0], 0, bcSize)],
          [(0, size[1], eps), (bcSize, size[1], eps),
           (bcSize, size[1], bcSize), (0, size[1], bcSize)],
          [(size[0], size[1], eps), (size[0]-bcSize, size[1], eps),
           (size[0]-bcSize, size[1], bcSize), (size[0], size[1], bcSize)],
          
          [(eps, 0, 0), (bcSize, 0, 0),
           (bcSize, bcSize, 0), (eps, bcSize, 0)],
          [(size[0]-eps, 0, 0), (size[0]-bcSize, 0, 0),
           (size[0]-bcSize, bcSize, 0), (size[0]-eps, bcSize, 0)],
          [(eps, size[1]-eps, 0), (bcSize, size[1]-eps, 0),
           (bcSize, size[1]-bcSize-eps, 0), (eps, size[1]-bcSize-eps, 0)],
          [(size[0]-eps, size[1]-eps, 0), (size[0]-bcSize, size[1]-eps, 0),
           (size[0]-bcSize, size[1]-bcSize-eps, 0),
           (size[0]-eps, size[1]-bcSize-eps, 0)],
      ]
      zOrders = [-20, -20, 10, 10, 10, 10, -20, -20, -20, -20, -20, -20]
    
    for vertices, zOrder in zip(verticess, zOrders):
      poly3DCollection = mpl_toolkits.mplot3d.art3d.Poly3DCollection(
          [vertices], facecolors=["C1"])
      poly3DCollection.set_sort_zpos(zOrder)
      ax.add_collection3d(poly3DCollection)
    
    xs = np.array([(0, 1), (0, 0), (0, 0)])
    ys = np.array([(1, 1), (1, 0), (1, 1)])
    zs = np.array([(0, 0), (0, 0), (0, 1)])
    for x, y, z in zip(xs, ys, zs):
      ax.plot(size[0]*x, size[1]*y, "k-", zs=size[2]*z, clip_on=False,
              zorder=-10)
    
    v = 0.1
    verts, faces, _, _ = skimage.measure.marching_cubes_lewiner(
        VV, v, spacing=size/(nn-1))
    lightSource = mpl.colors.LightSource(0, 45)
    surf = ax.plot_trisurf(verts[:,0], verts[:,1], faces, verts[:,2],
                          lightsource=lightSource)
    helper.plot.removeWhiteLinesInSurfPlot(surf)
    
    eps = 0.05
    xs = np.array([
        (1, 1), (0, 1), (0, 0), (0, 0), (0, 1),
        (1, 1), (0, 1), (1, 1), (1, 1),
        (0, 0), (1, 1), (1, 1+eps), (1, 1+eps), (-eps, 0), (-eps, 0)])
    ys = np.array([
        (0, 1), (0, 0), (0, 0), (0, 1), (1, 1),
        (0, 1), (0, 0), (0, 0), (1, 1),
        (-eps, 0), (-eps, 0), (0, 0), (1, 1), (0, 0), (0, 0)])
    zs = np.array([
        (0, 0), (0, 0), (0, 1), (1, 1), (1, 1),
        (1, 1), (1, 1), (0, 1), (0, 1),
        (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 1)])
    for x, y, z in zip(xs, ys, zs):
      ax.plot(size[0]*x, size[1]*y, "k-", zs=size[2]*z, clip_on=False,
              zorder=20)
    
    eps = (0.08 if q == 0 else 0.16)
    ax.text(0, -eps, 0, "$0$",
            ha="right", va="top")
    ax.text(size[0], -eps, 0, "${:.0f}$".format(size[0]),
            ha="right", va="top")
    ax.text(size[0]+eps, 0, 0, "$0$",
            ha="left", va="center")
    ax.text(size[0]+eps, size[1], 0, "${:.0f}$".format(size[1]),
            ha="left", va="center")
    ax.text(-eps, 0, 0, "$0$",
            ha="right", va="center")
    ax.text(-eps, 0, size[2], "${:.0f}$".format(size[2]),
            ha="right", va="center")
    
    if q == 0:
      eps = 0.1
      ax.text(0.55*size[0], -eps, 0, r"$\tilde{x}_1$",
              ha="right", va="top")
      ax.text(size[0]+eps, 0.6*size[1], 0, r"$\tilde{x}_2$",
              ha="left",  va="center")
      ax.text(-eps, 0, 0.45*size[2], r"$\tilde{x}_3$",
              ha="right", va="center")
    else:
      eps = 0.1
      ax.text(0.55*size[0], -eps, 0, r"$\tilde{x}_1$",
              ha="right", va="top")
      ax.text(size[0]+2*eps, 0.5*size[1], 0, r"$\tilde{x}_2$",
              ha="left",  va="center")
      ax.text(-eps, 0, 0.45*size[2], r"$\tilde{x}_3$",
              ha="right", va="center")
    
    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])
    ax.set_zlim(0, size[2])
    
    ax.set_axis_off()
    helper.plot.setEqual3DAxes(ax)
    
    fig.save()



if __name__ == "__main__":
  main()
