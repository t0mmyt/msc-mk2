from os import getenv
from celery import Celery
from .metadata import Metadata

broker = getenv("BROKER", "redis://localhost")
cassandra = getenv("CASSANDRA", "localhost").split(",")

app = Celery("tasks", broker=broker)
metadata = Metadata(hosts=cassandra)


@app.task
def update_meta(network, station, channel, start, end):
    pass
