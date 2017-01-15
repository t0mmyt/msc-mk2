'''
Run the API using the flask internal server
'''
from obsloader.api import app

app.run(
    host="127.0.0.1",
    port=8002,
    debug=True
)
