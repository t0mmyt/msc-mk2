'''
Library for interacting with KairosDB REST API
'''
import requests


class KairosDB(object):
    '''
    Object for interacting with the KairosDB REST API

    Args:
        host (str): hostname of the KairosDB instance
        port (int): port number to connect to
    '''
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def post(self, payload):
        '''
        Send data to the KairosDB as a KairosDBPayload

        Args:
            payload (KairosDBPayload): Payload to send

        Returns:
            True on success else False
        '''
        r = requests.post(
            url="http://{}:{}/api/v1/datapoints".format(self.host, self.port),
            json=payload
        )
        if r.status_code == 204:
            return True
        return False

    def query(self, name, tags, start, end):
        '''
        Query data from KairosDB.

        Args:
            name (str) : name of metric to query
            start (int): start_absolute in milliseconds since the epoch
            end (int)  : end_absolute in milliseconds since the epoch
            tags (dict): list of tags to add to query
        '''
        q = {
            'start_absolute': start,
            'end_absolute': end,
            "time_zone": "UTC",
            'metrics': [
                {
                    'name': name,
                    'tags': tags,
                }
            ]
        }
        # TODO - try/except
        r = requests.post(
            url="http://{}:{}/api/v1/datapoints/query".format(self.host, self.port),
            json=q
        )
        results = r.json()
        return {
            'metric': results['queries'][0]['results'][0]['name'],
            'tags': {k: v[0] for k, v in results['queries'][0]['results'][0]['tags'].items()},
            'results': results['queries'][0]['results'][0]['values']
        }


class KairosDBPayload(object):
    '''
    Payload constructor for sending data to KairosDB

    Args:
        name (str):  name of metric
        tags (dict): tags for metric
    '''
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
        self.datapoints = []

    def append(self, timestamp, value):
        '''
        Add datapoints to the payload

        Args:
            timestamp (int): time of metric in milliseconds since the epoch
            value (float):   value for metric
        '''
        self.datapoints.append((timestamp, value))

    def as_dict(self):
        '''
        Return the payload as a dict ready for JSON conversion

        Returns:
            dict of payload
        '''
        return dict(
            name=self.name,
            tags=self.tags,
            datapoints=self.datapoints
        )
