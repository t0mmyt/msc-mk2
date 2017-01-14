from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from os import getenv
from tsdatastore.kairosdb import KairosDB as db, KairosDBPayload as payload


class InvalidUsage(Exception):
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
    def __init__(self):
        host = getenv('DBHOST', "localhost")
        port = getenv('DBPORT', 8083)
        self.db = db(host, port)

    def put(self, name):
        data = request.json
        p = payload(name, data['tags'])
        t = data['starttime']
        for i in data['datapoints']:
            p.append(t, i)
            t += data['interval']
        if self.db.post(p.as_dict()):
            print("Ok.")
        else:
            print("Error")

    def get(self, name):
        for p in ("start", "end"):
            if p not in request.args:
                raise InvalidUsage(
                    "{} is a required parameter and was missing.".format(p))

        # s = 1315350000000
        # e = 1315436400000
        tags = {k: v for k, v in request.args.items() if k not in ["start", "end"]}
        return self.db.query(name, tags, request.args['start'], request.args['end'])

app = Flask(__name__)
api = Api(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

api.add_resource(Metrics, '/v1/metrics/<name>')
