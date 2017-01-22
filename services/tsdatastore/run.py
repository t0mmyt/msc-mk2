#!/usr/bin/env python3
from os import getenv
from gevent.wsgi import WSGIServer
from tsdatastore.api import app

LISTEN_PORT = int(getenv('LISTEN_PORT', 8000))

http_server = WSGIServer(('', LISTEN_PORT), app)
http_server.serve_forever()
