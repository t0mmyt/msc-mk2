from os import getenv
import random
from celery import Celery
from .metadata import Metadata

broker = getenv("BROKER", "redis://localhost")
cassandra = getenv("CASSANDRA", "localhost").split(",")

app = Celery("batch", broker=broker)


@app.task(bind=True)
def add_meta(self, network, station, channel, start, end, sample_rate):
    try:
        metadata = Metadata(hosts=cassandra)
        return metadata.add_meta(network, station, channel, start, end, sample_rate)
    except:
        raise self.retry(countdown=30 + int(random.uniform(-5, 5)))


@app.task(bind=True)
def init_schema(self):
    try:
        metadata = Metadata(hosts=cassandra)
        metadata.create_tables()
    except:
        raise self.retry(countdown=30 + int(random.uniform(-5, 5)))
