from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse, inputs
from flask_cors import CORS, cross_origin
from sax.dataset import Dataset
from os import getenv

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


class Sax(Resource):
    '''
    Metrics endpoint for tsdatastore API.
    '''
    def __init__(self):
        host = getenv('DSHOST', "localhost")
        port = int(getenv('DSPORT', 8084))

    def get(self, name):
        '''
        HTTP GET handler

        Additional fields to be passed as query string:
            start (int): Start of query time in milliseconds from epoch
            end (int)  : End of query time in milliseconds from epoch

        Args:
            name (str): Name of metric.
        '''
        params = {}
        for p in ("start", "end", "station", "network"):
            if p not in request.args:
                raise InvalidUsage(
                    "{} is a required parameter and was missing.".format(p))
            else:
                params[p] = request.args[p]

        normalise = inputs.boolean(request.args.get("normalise", False))
        absolute = inputs.boolean(request.args.get("absolute", False))
        bp_l = float(request.args.get('bandpassLow', 0))
        bp_h = float(request.args.get('bandpassHigh', 0))
        alphabet = request.args.get("alphabet", None)
        interval = int(request.args.get("interval", 0))
        distribution = request.args.get("distribution", "guassian")

        d = Dataset(
            url="http://localhost:8003/v1/metrics/{}".format(name),
            **params
        )

        # If there are bandpass params, run a bandpass
        if bp_l and bp_h:
            d.bandpass(bp_l, bp_h)

        # Normalise if set
        if normalise:
            d.normalise()

        if absolute:
            d.absolute()

        # If there are SAX params, run SAX code
        if alphabet and interval > 0:
            d.paa(interval)
            d.sax(alphabet, absolute, distribution)

        return d.payload

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

api.add_resource(Sax, '/v1/sax/<name>')
