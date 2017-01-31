from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS, cross_origin
from os import getenv
from tsdatastore.kairosdb import KairosDB as db, KairosDBPayload as payload


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


class Metrics(Resource):
    '''
    Metrics endpoint for tsdatastore API.
    '''
    def __init__(self):
        host = getenv('DBHOST', "localhost")
        port = int(getenv('DBPORT', 8083))
        self.db = db(host, port)

    def put(self, name):
        '''
        HTTP PUT handler

        Expects a JSON object of the following structure:
        {
            "starttime": <milliseconds from epoch>,
            "interval": <period between metrics in milliseconds>,
            "tags": {
                "key": "value"
            },
            "datapoints": [
                <datapoint.1>,
                <datapoint.2>,
                <datapoint.n>
            ]
        }

        Args:
            name (str): Name of metric.
        '''
        data = request.json
        p = payload(name, data['tags'])
        t = data['starttime']
        for i in data['datapoints']:
            p.append(t, i)
            t += data['interval']
        # TODO: Proper error handling
        if self.db.post(p.as_dict()):
            return None, 204
        else:
            return None, 400

    def get(self, name):
        '''
        HTTP GET handler

        Additional fields to be passed as query string:
            start (int): Start of query time in milliseconds from epoch
            end (int)  : End of query time in milliseconds from epoch

        Args:
            name (str): Name of metric.
        '''
        for p in ("start", "end"):
            if p not in request.args:
                raise InvalidUsage(
                    "{} is a required parameter and was missing.".format(p))

        tags = {k: v for k, v in request.args.items() if k not in ["start", "end"]}
        return self.db.query(name, tags, request.args['start'], request.args['end'])

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

api.add_resource(Metrics, '/v1/metrics/<name>')
