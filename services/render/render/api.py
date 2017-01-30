from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from os import getenv
import requests


class Graph(object):
    def __init__(self):
        ds_host = getenv('DBHOST', "localhost")
        ds_port = getenv('DBPORT', 8003)
        self.ds_url = "http://{}:{}/v1/metrics".format(ds_host, ds_port)

    def get(self):
        '''
        HTTP GET handler

        Returns PNG graph of Raw data
        '''
        #TODO Replace this with a std lib
        params = {}
        for p in ("start", "end", "station", "network"):
            if p not in request.args:
                raise InvalidUsage(
                    "{} is a required parameter and was missing.".format(p))
            else:
                params[p] = request.args[p]
        #TODO - try/except
        r = requests.get(
            url = self.ds_url,
            params = params
        )
