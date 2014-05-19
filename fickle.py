#!/usr/bin/python3

__author__ = 'reggie'


import socket
import sys

import hashlib
import base64
from hashlib import sha1
from base64 import b64encode
import http.server

import threading

import atexit

from fickleserver import *
from ficklepageindex import *
from ficklehttpserver import *

if __name__ == '__main__':
   servers = PageIndex()
   wsserver = FickleServer()
   wsserver.start()
   httpserver = HttpServer()
   httpserver.start()



