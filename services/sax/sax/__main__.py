'''
Run the SAX module using the flask internal server
'''
import sys
from .api import app

app.run(
    host="127.0.0.1",
    port=8004,
    debug=True
)
