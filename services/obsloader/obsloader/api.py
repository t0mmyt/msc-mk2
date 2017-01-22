'''
Exposed API for ObsLoader (Observation Loader)
'''
from io import BytesIO
from os import getenv
import requests
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from obsloader.obs import Observation, ObservationError


class InvalidUsage(Exception):
    '''
    Error handler for API.

    Taken from http://flask.pocoo.org/docs/0.12/patterns/apierrors
    '''
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
    '''
    Oberservations endpoint for obsloader API.
    '''
    def __init__(self):
        ds_host = getenv('DSHOST', "localhost")
        ds_port = int(getenv('DSPORT', 8003))
        self.ds_url = "http://{}:{}/v1/metrics".format(ds_host, ds_port)

    def put(self):
        '''
        HTTP PUT handler

        Expects raw SAC files
        '''
        try:
            data = BytesIO(request.get_data())
            o = Observation(path=data)
            r = requests.put(
                url="{}/{}".format(self.ds_url, o.stats().channel),
                json=o.as_tsdatastore_payload()
            )
            return None, r.status_code
        except ObservationError as e:
            print(e)
            return None, 400


app = Flask(__name__)
api = Api(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

api.add_resource(Observations, '/v1/observations')
