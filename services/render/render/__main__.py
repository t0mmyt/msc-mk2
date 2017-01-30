'''
Run the Graph Render using the flask internal server
'''
from render.api import app

app.run(
    host="127.0.0.1",
    port=8004,
    debug=True
)
