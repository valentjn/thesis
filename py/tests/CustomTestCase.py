#!/usr/bin/python3

import contextlib
import inspect
import random
import unittest

import numpy as np

class CustomTestCase(unittest.TestCase):
  def assertAlmostEqual(self, a, b, *args, **kwargs):
    a, b = np.array(a), np.array(b)
    self.assertEqual(a.shape, b.shape)
    np.testing.assert_allclose(a, b, *args, **kwargs)
  
  def assertNotAlmostEqual(self, a, b, *args, **kwargs):
    try:
      self.assertAlmostEqual(a, b, *args, **kwargs)
    except AssertionError:
      return
    
    raise AssertionError
  
  @staticmethod
  def getUnitTestVerbosity():
      frame = inspect.currentframe()
      
      while frame:
          self = frame.f_locals.get("self")
          if isinstance(self, unittest.TestProgram): return self.verbosity
          frame = frame.f_back
  
  def setUp(self):
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
  
  def subTest(self, msg=None, **params):
    class WrappedContextManager(contextlib.AbstractContextManager):
      def __init__(self, subTestCM,):
        self.subTestCM = subTestCM
      
      def __enter__(self):
        self.subTestCM.__enter__()
      
      def __exit__(self, excType, excValue, traceback):
        if isinstance(excValue, AssertionError):
          print("FAILURE")
        elif excValue is not None:
          print("ERROR")
        else:
          print("ok")
        
        return self.subTestCM.__exit__(excType, excValue, traceback)
    
    logMessage = ".".join(self.id().split(".")[1:])
    
    if msg is not None: logMessage += ", ({})".format(msg)
    if len(params) > 0:
      logMessage += ", ".join(
        [""] + ["{}={}".format(x, y) for x, y in params.items()])
    
    logMessage += " ... "
    print(logMessage, end="")
    
    subTestCM = (super().subTest(**params) if msg is None else
                 super().subTest(msg, **params))
    return WrappedContextManager(subTestCM)
