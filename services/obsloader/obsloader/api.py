"""
Exposed API for ObsLoader (Observation Loader)
"""
from io import BytesIO
from os import getenv
import requests
import logging
from logging import info
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from celery import Celery
from .obs import Observation, ObservationError


class InvalidUsage(Exception):
    """
    Error handler for API.

    Taken from http://flask.pocoo.org/docs/0.12/patterns/apierrors
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class Observations(Resource):
    """
    Observations endpoint for obsloader API.

    Will add a job to ensure schema is created
    """
    def __init__(self):
        url = getenv('TSDATASTORE', "http://localhost:8163")
        broker = getenv("BROKER", "redis://localhost")
        self.ds_url = "{}/v1/metrics".format(url)
        self.queue = Celery("batch", broker=broker)

    def put(self):
        """
        HTTP PUT handler

        Expects raw SAC files
        """
        try:
            data = BytesIO(request.get_data())
            o = Observation(path=data)
            payload = o.as_tsdatastore_payload()
            info("Payload: {}.{}.{} starting at {} at {}Hz and {} points.".format(
                o.stats().network, o.stats().station, o.stats().channel,
                payload['starttime'], o.stats().sampling_rate, len(payload['datapoints'])))

            r = requests.put(
                url="{}/{}".format(self.ds_url, o.stats().channel),
                json=payload
            )
            self.queue.send_task("batch.tasks.add_meta", args=(
                o.stats().network,
                o.stats().station,
                o.stats().channel,
                payload['starttime'],
                payload['starttime'] + len(payload['datapoints']) * payload['interval'],
                o.stats().sampling_rate
            ))
            return None, r.status_code
        except ObservationError as e:
            print(e)
            return None, 400


app = Flask(__name__)
api = Api(app)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

api.add_resource(Observations, '/v1/observations')
