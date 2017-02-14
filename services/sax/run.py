#!/usr/bin/env python3
'''
Run the SAX module using the flask internal server
'''
from os import getenv
from sax.api import app

LISTEN_PORT = int(getenv('LISTEN_PORT', 8000))

app.run(
    host="127.0.0.1",
    port=8004,
    debug=True
)