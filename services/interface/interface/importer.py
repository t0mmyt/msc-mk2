from os import getenv
import requests


class Importer(object):
    def __init__(self, url=None):
        self.url = getenv('OBSLOADER', "http://localhost:8164/v1/observations") if not url else url
        self.data = []

    def add(self, data):
        self.data.append(data)

    def send(self):
        status = []
        for data in self.data:
            status.append(self._upload(data) == 204)
        return status

    def _upload(self, data):
        # TODO try/except ConnectionError
        r = requests.put(
            url=self.url,
            headers={'Content-Type': "application/octet"},
            data=data
        )
        return r.status_code
