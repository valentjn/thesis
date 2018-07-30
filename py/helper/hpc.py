#!/usr/bin/python3

import atexit
import functools
import inspect
import lzma
import os
import pickle




cacheCache = {}

def getCachePath(path=None):
  if (path is None) and ("BUILD_DIR" in os.environ):
    path = os.environ["BUILD_DIR"]
  
  if (path is None) or os.path.isdir(path):
    stack = inspect.stack()
    
    for frame in stack:
      if frame.filename != stack[0].filename:
        basename = "{}.cache.xz".format(
            os.path.splitext(os.path.basename(frame.filename))[0])
        dirname = (os.path.dirname(frame.filename) if path is None else path)
        path = os.path.join(dirname, basename)
        break
  
  return path

def cacheToFile(func, path=None):
  path = getCachePath(path)
  
  if path in cacheCache:
    cache = cacheCache[path]
  else:
    if os.path.isfile(path):
      print("Reading cache file \"{}\"...".format(path))
      with lzma.open(path, "rb") as f: cache = pickle.load(f)
    else:
      print("Using new cache file \"{}\".".format(path))
      cache = {}
    
    cacheCache[path] = cache
  
  funcName = func.__name__
  if funcName not in cache: cache[funcName] = {}
  funcCache = cache[funcName]
  
  @functools.wraps(func)
  def cacheLookup(*args, **kwargs):
    spec = inspect.getfullargspec(func)
    allArgs = frozenset(list(zip(spec.args, args)) + list(kwargs.items()))
    if allArgs not in funcCache:
      funcCache[allArgs] = func(*args, **kwargs)
      cache["__modified__"] = True
    return funcCache[allArgs]
  
  @atexit.register
  def saveCache():
    if cache.get("__modified__", False):
      del cache["__modified__"]
      while True:
        try:
          with lzma.open(path, "wb") as f: pickle.dump(cache, f)
          break
        except KeyboardInterrupt:
          pass
  
  return cacheLookup

def clearCacheFile(path=None):
  path = getCachePath(path)
  if os.path.isfile(path): os.remove(path)
