'''
Run the API using the flask internal server
'''
from tsdatastore.api import app

app.run(
    host="127.0.0.1",
    port=8003,
    debug=True
)
