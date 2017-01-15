#!/usr/bin/env python3
from gevent.wsgi import WSGIServer
from obsloader.api import app

http_server = WSGIServer(('', 8000), app)
http_server.serve_forever()
