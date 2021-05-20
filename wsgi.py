#! /usr/bin/python
import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/ubuntu/circuitnimble/async-socket-server")

from app import app as application
application.secret_key = os.urandom(64)


