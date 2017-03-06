from flask import Flask, jsonify, request, g
from flask_restful import Resource, Api
from flask_cors import CORS
import logging
from logging import info, debug, error
# from os import getenv
import msgpack
import numpy as np
from io import BytesIO
from uuid import uuid4
from payload import PayloadFromImport, PayloadFromObject, PayloadError
from datastore import Datastore, DatastoreError
from metadata import Metadata, MetadataError
from iso8601 import parse_date


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
            payload = PayloadFromImport(data)
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
        object_list = self.metadata.list(**params)
        new_datapoints = np.empty(0)

        start = parse_date(params['start']).replace(tzinfo=None).timestamp() * 1000
        end = parse_date(params['end']).replace(tzinfo=None).timestamp() * 1000

        debug("Got object list: {}".format(object_list))
        for o in object_list:
            interval = 1000 / o[3]
            debug("Interval: {}".format(interval))
            p = PayloadFromObject(data=self.datastore.get(o[0]), meta={})
            if o[1] < start:
                start_i = int((start - o[1]) / interval) # start index
                if o[2] < end:
                    debug("Reading {} from {} to end".format(o[0], start_i))
                    new_datapoints = np.append(new_datapoints, p.datapoints[start_i:])
                else:
                    # TODO - Out by 1?
                    end_i = int((end - o[1]) / interval)
                    debug("Reading {} from {} to {}".format(o[0], start_i, end_i))
                    new_datapoints = np.append(new_datapoints, p.datapoints[start_i:end_i])
            else: # o[1] >= start
                if o[2] > end:
                    debug("Reading {} from beginning to end".format(o[0], start_i))
                    new_datapoints = np.append(new_datapoints, p.datapoints)
                else:
                    # TODO - Out by 1?
                    end_i = int((end - o[1]) / interval)
                    debug("Reading {} from beginning to {}".format(o[0], end_i))
                    new_datapoints = np.append(new_datapoints, p.datapoints[:end_i])
        return list(new_datapoints)


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
