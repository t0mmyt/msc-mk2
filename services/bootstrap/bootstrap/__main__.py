from os import getenv
from sys import exit
from celery import Celery


broker = getenv("BROKER", "redis://localhost")
queue = Celery("batch", broker=broker)

# Initialise DB schema for metadata
queue.send_task("batch.tasks.init_schema")

# All good if we got this far
exit(0)
