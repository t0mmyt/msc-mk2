#!/usr/bin/env python3
import obspy
from sys import argv
from iso8601 import parse_date
import requests

assert len(argv) == 2, "Need file as arg"

api = "http://localhost:8003/v1/metrics"

o = obspy.core.stream.read(argv[1])

for i in o:
  s = i.stats
  ch = i.stats['channel'][-1:]
  payload = {
      'starttime': int(parse_date(str(i.stats.starttime)).timestamp() * 1000),
      'tags': {
          'network': s.network,
          'station': s.station,
      },
      'datapoints': i.data.tolist(),
      'interval': 1000.0/s.sampling_rate
  }
  r = requests.put(url="{}/{}".format(api, s.channel[-1:]), json=payload)
  print(r.status_code)
