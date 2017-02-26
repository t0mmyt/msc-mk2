"""
Library for reading SAC obersvations for import to a TSDB
"""
import obspy
from iso8601 import parse_date
from logging import debug, info


class ObservationError(Exception):
    """
    Exception to contain all errors relating to loading the observations
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Observation(object):
    def __init__(self, path):
        try:
            self.stream = obspy.core.stream.read(path)
        except (IOError, TypeError) as e:
            raise ObservationError('Failed to read {}: {}'.format(path, e))

    @property
    def trace_count(self):
        return len(self.stream)

    def stats(self, tracenum=0):
        trace = self.stream[tracenum]
        stats = trace.stats
        stats['channel'] = stats['channel'][-1]
        return stats

    def as_tsdatastore_payload(self, tracenum=0):
        t = self.stream[tracenum]
        s = t.stats
        return {
            'starttime': int(parse_date(str(s.starttime)).timestamp() * 1000),
            'interval': 1000.0/s.sampling_rate,
            'tags': {
                  'network': s.network,
                  'station': s.station,
            },
            'datapoints': t.data.tolist()
        }
