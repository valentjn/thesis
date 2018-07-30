#!/usr/bin/python3

import atexit
import functools
import inspect
import lzma
import os
import pickle
import secrets
import socket
import subprocess
import time
import warnings

import helper.remotely



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



DEFAULT_REMOTELY_URL  = "neon.informatik.uni-stuttgart.de"
DEFAULT_REMOTELY_PORT = 8075

remotelyServerCache = {}

def readRemotelyKey():
  keyPath = os.path.expanduser("~/.remotely_key.txt")
  
  if os.path.isfile(keyPath):
    with open(keyPath, "r") as f: key = f.read().strip()
  else:
    key = secrets.token_hex(32)
    with open(keyPath, "w") as f: f.write(key)
  
  return key

def checkRemotelyConnection(url, port, key):
  previousTimeout = socket.getdefaulttimeout()
  socket.setdefaulttimeout(0.1)
  
  @helper.remotely.remotely(key, url, port)
  def dummyFunction(a, b):
    return a + b
  
  try:
    result = dummyFunction(3, 4)
    return (result == 7)
  except Exception as exception:
    return False
  finally:
    socket.setdefaulttimeout(previousTimeout)

def startRemotelyServer(url, port, key):
  cmd =  ("PYTHONPATH=\""
            "$REAL_HOME/git/thesis/py:"
            "$REAL_HOME/git/thesis/gfx/py:"
            "$REAL_HOME/git/thesis/cpp/sgpp/lib:"
            "$REAL_HOME/git/thesis/cpp/sgpp/lib/pysgpp:"
            "$PYTHONPATH"
          "\" "
          "LD_LIBRARY_PATH=\""
            "$REAL_HOME/git/thesis/cpp/sgpp/lib/sgpp:"
            "$LD_LIBRARY_PATH"
          "\" "
          "REMOTELY_KEY=\"{}\" "
          "nice -n 19 python3 -c '"
            "import pysgpp; import multiprocessing; "
            "import helper.remotely; import os; "
            "pysgpp.omp_set_num_threads(multiprocessing.cpu_count()); "
            "server = helper.remotely.create_remotely_server("
                "os.environ[\"REMOTELY_KEY\"], {}); "
            "server.serve_forever()"
          "' </dev/null >/dev/null 2>&1 &").format(key, port)
  args = ["ssh", url, cmd]
  subprocess.run(args, check=True)
  print("Starting remotely server on {} with port {} and key {}.".format(
      url, port, key))
  time.sleep(1.0)

def executeRemotely(func, url=DEFAULT_REMOTELY_URL,
                    autoStart=2, fallback=True):
  if "REMOTELY_KEY" in os.environ:
    warnings.warn("Environment variable REMOTELY_KEY is set, "
                  "which means that we are already running remotely. "
                  "Using local fallback.")
    return func
  
  if url in remotelyServerCache:
    cache = remotelyServerCache[url]
    isConnected = cache["isConnected"]
    if isConnected: port, key = cache["port"], cache["key"]
  else:
    isConnected = False
  
  if (not isConnected) and (autoStart >= 1):
    startPort = DEFAULT_REMOTELY_PORT
    key = readRemotelyKey()
    
    for port in range(startPort, startPort+5):
      if checkRemotelyConnection(url, port, key):
        isConnected = True
        break
      
      try:
        startRemotelyServer(url, port, key)
      except Exception as exception:
        pass
      else:
        if checkRemotelyConnection(url, port, key):
          isConnected = True
          break
      
      if autoStart < 2: break
    
    if isConnected:
      remotelyServerCache[url] = {"isConnected" : True,
                                  "port" : port, "key" : key}
    else:
      remotelyServerCache[url] = {"isConnected" : False}
  
  if isConnected:
    print("Connected to remotely server on {} "
          "with port {} and key {}.".format(url, port, key))
    return helper.remotely.remotely(key, url, port)(func)
  else:
    if fallback:
      warnings.warn("Could not connect to remotely server, "
                    "using local fallback.")
      return func
    else:
      raise RuntimeError("Could not connect to remotely server.")
