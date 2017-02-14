import requests
import numpy as np
from obspy.signal.filter import bandpass
# from obspy import normalize
from flask import jsonify
from .sax import SAX


class DatasetError(Exception):
    pass


class Dataset(object):
    def __init__(self, url, **params):
        self._values = np.empty(0)
        self._times = np.empty(0)
        self.paa_times = np.empty(0)
        self.paa_values = np.empty(0)
        self._sax = None
        try:
            r = requests.get(url, params=params)
            self.dataset = r.json()
        except requests.ConnectionError as e:
            raise DatasetError("Connection Error to datastore: {}".format(e))
        except ValueError:
            raise DatasetError("Not JSON")

    @property
    def payload(self):
        self.dataset['results'] = list(zip(self.times, self.values))
        if len(self.paa_values) > 0 and len(self.paa_times) > 0:
            self.dataset['paa'] = list(zip(self.paa_times, self.paa_values))
        if self._sax:
            self.dataset['sax'] = str(self._sax)
            self.dataset['breakpoints'] = self._sax.breakpoints
        return self.dataset

    @property
    def values(self):
        """
        Return a numpy array of only values
        """
        if len(self._values) == len(self.dataset['results']):
            return self._values
        d = self.dataset
        arr = np.empty(len(d['results']))
        i = 0
        for v in d['results']:
            arr[i] = d['results'][i][1]
            i += 1
        # self._values = np.absolute(arr)
        self._values = arr
        return self._values

    @property
    def times(self):
        """
        Return a numpy array of only times
        """
        if len(self._times) == len(self.dataset['results']):
            return self._times
        d = self.dataset
        arr = np.empty(len(d['results']))
        i = 0
        for v in d['results']:
            arr[i] = d['results'][i][0]
            i += 1
        self._times = arr
        return self._times

    @property
    def freq(self):
        """
        Calculate frequency of observations.

        Raise a ValueError if observations are not evenly spaced
        """
        last_interval = None
        new_interval = None
        last_t = None
        for t in self.times:
            if not last_t:
                last_t = t
                continue
            if not last_interval:
                last_interval = t - last_t
            new_interval = t - last_t
            if new_interval != last_interval:
                print("{} {} {} {}".format(t, last_t, last_interval, new_interval))
                raise ValueError
            last_t = t
        return 1000 / last_interval

    def bandpass(self, low, high):
        """
        Perform a bandpass using obspy on values
        """
        self._values = bandpass(self.values, low, high, self.freq)

    def paa(self, interval):
        v = self.values
        t = self.times
        n = int(((t[-1:] - t[0]) / interval) + .5)
        self.paa_values = np.empty(n)
        self.paa_times = np.empty(n)
        i = 0
        start_pos = 0
        end_pos = 0

        while i < n:
            t_start = t[start_pos]
            end_pos = np.searchsorted(t[start_pos:], t_start + interval) + start_pos
            t_end = t[end_pos]
            self.paa_values[i] = np.mean(v[start_pos:end_pos - 1])
            self.paa_times[i] = t[start_pos]# + (interval / 2)
            start_pos = end_pos
            i += 1

    def sax(self, alphabet, absolute=False, distribution="gaussian"):
        self._sax = SAX(self.paa_values, alphabet, absolute, distribution)


    @property
    def max(self):
        peak = max(self.values.max(), abs(self.values.min()))
        print(peak)
        return peak

    def normalise(self):
        self._values = np.divide(self.values, self.max)

    def absolute(self):
        self._values = np.absolute(self.values)


if __name__ == "__main__":
    d = Dataset(
        url="http://localhost:8003/v1/metrics/Z",
        network="YW",
        station="NAB1",
        start=1315406870000,
        end=1315406871000
    )
    d.bandpass(5, 20)
    d.paa(50)
