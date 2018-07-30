#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import socketserver
import marshal
import types
import base64
import pickle
import socket 
import threading
import multiprocessing as mp
import sys
import argparse


# threaded xmlrpc
#import SimpleXMLRPCServer
if sys.version_info >= (3, 0):
  from xmlrpc.server import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
else:
  from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
class AsyncXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer): pass
class RemotelyException(Exception): pass


DEBUG_MODE = False

def create_remotely_server(api_key, port=8075):
    """
    create a server to be used with the given api key.
    call serve_forever() on the server obj to start.
    """ 
    server = RemotelyServer(('', port))
    server.register_multicall_functions()
    server.register_function(server.run, "run")
    server.register_function(server.join, "join")
    server.register_function(server.kill, "kill")
    server.register_key(api_key)
    return server


class RemotelyServer(AsyncXMLRPCServer):
    def __init__(self, *args, **kwds):
        """
        """
        SimpleXMLRPCServer.__init__(
            self, *args, use_builtin_types=True, **kwds)
        self.api_key = None
        self.pid = 1
        self.jobs = {}

    def server_bind(self):
        """
        """
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SimpleXMLRPCServer.server_bind(self)

    def register_key(self, api_key):
        """
        add an api_key for security
        """
        self.api_key = api_key

    def run(self, api_key, asynchronous, func_str, *args, **kwds):
        """
        called remotely to run a function in the local thread/process
        @api_key: security key 
        asynchronous: if true the function will be split into a separate
                      process; use join/kill to manage the process        
        """
        if api_key != self.api_key and self.api_key is not None:
            raise RemotelyException(" Bad API KEY: " + str(api_key))

        code = marshal.loads(base64.b64decode(func_str))
        func = types.FunctionType(code, globals(), "remote_func")
        
        if DEBUG_MODE:
            print("exec function", func)
            print("func params", args, kwds)

        if asynchronous:
            # create a process wrapper and use queue to get func output
            q = mp.Queue()
            def wrapper(func,q):
                def wrapper2(*args, **kwds):
                    ret = func(*args, **kwds)
                    q.put(ret)
                return wrapper2

            p = mp.Process(target=wrapper(func,q), args=args, kwargs=kwds)
            p.start()
            self.jobs[(api_key, p.pid)] = (p,q)
            output = base64.b64encode(pickle.dumps(p.pid))
        else:
            # block and run
            output = func(*args, **kwds)
            output = base64.b64encode(pickle.dumps(output))
        return output

    def join(self, api_key, pid, timeout=None):
        """
        Block on the thread until the process is terminated
        @return output from the function call
        """
        output = None
        if (api_key,pid) in self.jobs:        
            p,q = self.jobs[(api_key,pid)]
            p.join(timeout)
            if not p.is_alive():
                del self.jobs[(api_key,pid)]
            if not q.empty():
                output = q.get(block=False)

        output = base64.b64encode(pickle.dumps(output))
        return output

    def kill(self, api_key, pid, timeout=None):
        """
        Send kill signal to the job
        @return True if the job was succesfully terminated
        """
        output = False
        if (api_key,pid) in self.jobs:        
            p,q = self.jobs[(api_key,pid)]
            p.terminate()
            p.join(timeout)
            output = not p.is_alive()

        output = base64.b64encode(pickle.dumps(output))
        return output


def main():
    #cmd options 
    parser = OptionParser()
    parser.add_argument("--port", dest="port", default=8075, type="int",
                    help="server port (default to 8075).")
    parser.add_argument("--api_key", dest="api_key", default=None, type="string",
                    help="api key for authenticating against this server.")
    parser.add_argument('--daemon', dest="daemon", action='store_true', default=False,
                    help='run server as daemon (default false).')

    args = parser.parse_args()

    if args.api_key is None:
        print("warning: starting server without API_KEY, anyone can access the server")
    
    # argparse code
    #args = parser.parse_args()
    #print("HOST", args.host, args.port)
    #print("API_KEY", args.api_key)
    
    def start_server():
        server = create_remotely_server(args.api_key, args.port)
        print("starting remote exec server on port %s" % args.port)
        server.serve_forever()

    if args.daemon:
        print("running daemon mode")
        import daemon
        with daemon.DaemonContext():
            start_server()
    else:
        start_server()
    return 0


if __name__=="__main__":
    main()        

