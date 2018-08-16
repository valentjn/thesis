#!/usr/bin/python3

import atexit
import functools
import inspect
import lzma
import multiprocessing
import multiprocessing.managers
import os
import pickle
import secrets
import signal
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

multiprocessingManager = multiprocessing.managers.SyncManager()
multiprocessingManager.start(signal.signal, (signal.SIGINT, signal.SIG_IGN))

def cacheToFile(func, path=None):
  path = getCachePath(path)
  
  if path in cacheCache:
    cache = cacheCache[path]
  else:
    if os.path.isfile(path):
      print("Reading cache file {}...".format(path))
      with lzma.open(path, "rb") as f: cache = pickle.load(f)
    else:
      print("Using new cache file {}.".format(path))
      cache = {}
    
    cache = multiprocessingManager.dict(cache)
    cacheCache[path] = cache
    cache["__info__"] = multiprocessingManager.dict(
        {"modified" : False, "depth" : 0, "ignoreDepth" : 0})
  
  funcName = func.__name__
  if funcName not in cache: cache[funcName] = {}
  funcCache = cache[funcName]
  if isinstance(funcCache, dict):
    funcCache = multiprocessingManager.dict(funcCache)
    cache[funcName] = funcCache
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
    
    if ((boundArgsTuple in funcCache) and
        (cache["__info__"]["depth"] >= cache["__info__"]["ignoreDepth"])):
      print("Cache hit: {}".format(callString))
    else:
      print("Cache miss: {}".format(callString))
      
      try:
        cache["__info__"]["depth"] += 1
        funcCache[boundArgsTuple] = func(*args, **kwargs)
      finally:
        cache["__info__"]["depth"] -= 1
      
      cache["__info__"]["modified"] = True
    
    return funcCache[boundArgsTuple]
  
  @atexit.register
  def saveCache():
    if "__info__" in cache:
      if cache["__info__"]["modified"]:
        print("Saving cache file \"{}\"...".format(path))
        cacheToSave = {x : dict(y) for x, y in cache.items()
                       if x is not "__info__"}
        while True:
          try:
            with lzma.open(path, "wb") as f: pickle.dump(cacheToSave, f)
            cache["__info__"]["modified"] = False
            break
          except KeyboardInterrupt:
            pass
      else:
        print("Not saving cache file {}, as it doesn't seem to be "
              "modified.".format(path))
    else:
      print("Not saving cache file {}, as it already seems to be "
            "saved.".format(path))
  
  return cacheLookup

def clearCacheFile(path=None):
  path = getCachePath(path)
  if os.path.isfile(path): os.remove(path)

class CacheFileIgnorer(object):
  def __init__(path=None, delta=None):
    path = getCachePath(path)
    self.cache = cacheCache[path]
    self.delta = delta
  
  def __enter__(self):
    self.cache["__info__"]["ignore_depth"] += self.delta
    print("Increasing ignore depth of cache file {} to {}.".format(
        self.path, self.cache["__info__"]["ignore_depth"]))
  
  def __exit__(self, exceptionType, exceptionValue, traceback):
    self.cache["__info__"]["ignore_depth"] -= self.delta
    print("Decrasing ignore depth of cache file {} to {}.".format(
        self.path, self.cache["__info__"]["ignore_depth"]))



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

def isRemotelyConnected(url=DEFAULT_REMOTELY_URL):
  return remotelyServerCache[url]["isConnected"]

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
  subprocess.run(args, check=True, timeout=2)
  print("Starting remotely server on {} with port {} and key {}.".format(
      url, port, key))
  time.sleep(1)

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
