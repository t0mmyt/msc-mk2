#!/usr/bin/env python3

import requests

endpoint = "http://127.0.0.1:8003/v1/metrics/foo"

datapoints = (1, 2, 3, 4, 5, 4, 3, 2, 1)

tags = {
    'station': "euston",
    'channel': "bbc1"
}

payload = {
    'tags': tags,
    'starttime': 1484412294000,
    'interval': 1000,
    'datapoints': datapoints,
}

r = requests.put(endpoint, json=payload)
