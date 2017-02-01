import requests
import numpy as np
from obspy.signal.filter import bandpass
from flask import jsonify


class Dataset(object):
    def __init__(self, url, **params):
        self._values = np.empty(0)
        self._times = np.empty(0)
        try:
            r = requests.get(url, params=params)
            self.dataset = r.json()
        except requests.ConnectionError:
            print("ConnectionError")
        except ValueError:
            print("Not JSON")

    @property
    def payload(self):
        self.dataset['results'] = list(zip(self.times, self.values))
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




if __name__ == "__main__":
    d = Dataset(
        url="http://localhost:8003/v1/metrics/Z",
        network="YW",
        station="NAB1",
        start=1315406870000,
        end=1315406880000
    )
    d.bandpass(5, 20)
    print(d.payload)
