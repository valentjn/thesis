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
  funcSignature = inspect.signature(func)
    
  @functools.wraps(func)
  def cacheLookup(*args, **kwargs):
    boundArgs = funcSignature.bind(*args, **kwargs)
    boundArgs.apply_defaults()
    boundArgsOrderedDict = boundArgs.arguments
    boundArgsTuple = tuple(boundArgsOrderedDict.items())
    
    callString = "{}({})".format(funcName,
        ", ".join(["{}={}".format(x, repr(y))
                   for x, y in boundArgsOrderedDict.items()]))
    
    if boundArgsTuple in funcCache:
      print("Cache hit: {}".format(callString))
    else:
      print("Cache miss: {}".format(callString))
      funcCache[boundArgsTuple] = func(*args, **kwargs)
      cache["__modified__"] = True
    
    return funcCache[boundArgsTuple]
  
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
