#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info >= (3, 0):
  import xmlrpc.client as xmlrpclib
else:
  import xmlrpclib
import marshal
import base64
import pickle
import multiprocessing
import functools



def remotely(api_key, host, port):
    """
    synchronous decorator for executing code remotely. 
    @param api_key: key for authentication
    @param host: remotely server ip
    @param port: remotely server port
    """
    def decorate(func):
        url = "http://%s:%s" % (host, port)
        proxy = xmlrpclib.ServerProxy(
            url, allow_none=True, use_builtin_types=True)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            func_code = getattr(func, "func_code", func.__code__)
            code_str = base64.b64encode(marshal.dumps(func_code))
            output = proxy.run(api_key, False, code_str, *args, **kwds)
            return pickle.loads(base64.b64decode(output))

        return wrapper
    return decorate


class RemoteClient(object):

    def __init__(self, api_key, host, port, asynchronous=True):
        """
        class for asynchronous remote execution
        """
        url = "http://%s:%s" % (host, port)
        self.proxy = xmlrpclib.ServerProxy(
            url, allow_none=True, use_builtin_types=True)
        self.api_key = api_key
        self.host = host
        self.port = port
        self.asynchronous = True

    def set_async(self, asynchronous=True):
        self.asynchronous = asynchronous

    def run(self, func, *args, **kwds):
        """
        run function on remote server
        @return pid for asynchronous    
        """
        func_code = getattr(func, "func_code", func.__code__)
        code_str = base64.b64encode(marshal.dumps(func_code))
        output = self.proxy.run(self.api_key, self.asynchronous, code_str, *args, **kwds)
        return pickle.loads(base64.b64decode(output))

    def join(self, pid, timeout=None):
        """
        Block the calling thread until the function terminate or timeout occurs.
        @param pid: process id from run()
        @param timeout: if timeout is none then there's no timeout
        """
        output = self.proxy.join(self.api_key, pid, timeout)
        return pickle.loads(base64.b64decode(output))

    def kill(self, pid):
        """
        Terminate the process using Process.terminate() call
        @param pid: process id from run()
        """
        output = self.proxy.kill(self.api_key, pid, None)
        return pickle.loads(base64.b64decode(output))


