from flask import Flask, jsonify, request, g
from flask_restful import Resource, Api
from flask_cors import CORS
import logging
from logging import info, debug, error
# from os import getenv
import msgpack
from io import BytesIO
from uuid import uuid4
from payload import Payload, PayloadError
from datastore import Datastore, DatastoreError
from metadata import Metadata, MetadataError


class InvalidUsage(Exception):
    """
    Error handler for API.

    Taken from http://flask.pocoo.org/docs/0.12/patterns/apierrors
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        error(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class Metric(Resource):
    def __init__(self):
        self.datastore = getattr(g, '_datastore', None)
        if not self.datastore:
            info("Creating connection to datastore")
            self.minio_host = "127.0.0.1:9000"
            self.minio_key = "test_key"
            self.minio_secret = "test_secret"
            self.minio_bucket = "seismic"
            self.datastore = g._datastore = Datastore(self.minio_host, self.minio_key, self.minio_secret, self.minio_bucket)

        self.metadata = getattr(g, '_metadata', None)
        if not self.metadata:
            info("Creating connection to Metadata DB")
            self.crate_endpoints = ["localhost:4200"]
            self.metadata = g._metadata = Metadata(self.crate_endpoints)
            self.metadata.create_tables()

    def put(self):
        if request.content_type != "application/msgpack":
            raise InvalidUsage("Data should be sent as application/msgpack", 400)
        packed = BytesIO(request.get_data())
        data = msgpack.unpack(packed, encoding='utf-8')
        try:
            payload = Payload(data)
            length, blob = payload.to_np_save()
            tags = payload.tags
            new_uuid = str(uuid4())
            self.metadata.put(
                uuid=new_uuid,
                network=tags['network'],
                station=tags['station'],
                channel=tags['channel'],
                start=payload.start,
                end=payload.end,
                sampling_rate=tags['sampling_rate']
            )
            self.datastore.put(new_uuid, blob, length)

        except (DatastoreError, MetadataError, PayloadError) as e:
            raise InvalidUsage("Could not accept payload: {}".format(e))

    def get(self):
        req_params = ('network', 'station', 'channel', 'start', 'end')
        params = {}
        for p in req_params:
            if p not in request.args:
                raise InvalidUsage(
                    "{} is a required parameter and was missing.".format(p))
            else:
                params[p] = request.args[p]
        return self.metadata.list(**params)


app = Flask(__name__)
api = Api(app)
api.add_resource(Metric, "/v1/metrics")
CORS(app)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(err):
    response = jsonify(err.to_dict())
    response.status_code = err.status_code
    return response


if __name__ == "__main__":
    app.run(debug=True)
