import requests
import json


class KairosDB(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def post(self, payload):
        r = requests.post(
            url="http://{}:{}/api/v1/datapoints".format(self.host, self.port),
            json=payload
        )
        if r.status_code == 204:
            return True
        return False

    def query(self, name, tags, start, end):
        q = {
            'start_absolute': start,
            'end_absolute': end,
            'metrics': [
                {
                    'name': name,
                    'tags': tags,
                }
            ]
        }
        print(json.dumps(q, indent=2))
        r = requests.post(
            url="http://{}:{}/api/v1/datapoints/query".format(self.host, self.port),
            json=q
        )
        return r.json()


class KairosDBPayload(object):
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
        self.datapoints = []

    def append(self, timestamp, value):
        self.datapoints.append((timestamp, value))

    def as_dict(self):
        return dict(
            name=self.name,
            tags=self.tags,
            datapoints=self.datapoints
        )
