from timeit import default_timer
import logging
from logging import debug
import numpy as np
import obspy
from obspy.signal.filter import bandpass
from datetime import timedelta
from nptime import nptime


def time(f):
    """
    Decorator to log method call time to debug
    """
    def timed(*args, **kwargs):
        st = default_timer()
        result = f(*args, **kwargs)
        dt = default_timer() - st
        debug("Calling {0} took {1:.3f}s".format(f.__name__, dt))
        return result
    return timed


class Stream(object):
    def __init__(self, stream, sampling_rate):
        self.stream = stream
        self.freq = sampling_rate
        self.interval = 1000/sampling_rate
        debug("Got stream of length {} at intervals of {}ms".format(len(self.stream), self.interval))
        self._abs = None

    @property
    def abs(self):
        """
        Absolute values of stream

        Returns:
            numpy.ndarray
        """
        if not isinstance(self._abs, np.ndarray):
            self._abs = np.abs(self.stream)
        return self._abs

    @staticmethod
    def normalised_to_peak(a):
        """
        Divide all values in a by the maximum value

        Args:
            a:

        Returns:
            np.ndarray
        """
        assert isinstance(a, np.ndarray), "normalisation only works on numpy arrays"
        d = np.divide(a, np.max(a))
        return d

    def bandpass(self, low, high):
        """
        Perform a frequency bandpass in-place on a stream to reduce noise
        Args:
            low:  Remove frequencies below this value
            high: Remove frequencies above this value
        """
        self.stream = bandpass(self.stream, low, high, self.freq)

    @time
    def detect(self, short, long):
        long_window_length = int(long * self.interval)
        short_window_length = int(short * self.interval)
        debug("Window lengths: {}, {} ({}s, {}s)".format(
            long_window_length, short_window_length, long/1000, short/1000))
        i = long_window_length
        while i + short_window_length < len(self.stream):
            long_window = Stream.normalised_to_peak(self.abs[i - long_window_length:i])
            # short_window = self.abs[i - short_window_length:i]
            long_window_mean = np.mean(long_window)
            long_window_std = np.std(long_window)
            short_window_mean = np.mean(long_window[-short_window_length:])
            if short_window_mean > (long_window_mean + (long_window_std / 2)):
                yield(i, long_window_mean, short_window_mean)
            i += short_window_length
            # raise StopIteration


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    o = obspy.read('/srv/seismic_raw/2011.239/2011.239.00.00.00.0000.YW.NAB1..HHZ.D.SAC')
    t = o[0]
    s = Stream(t.data, t.meta.sampling_rate)
    s.bandpass(5, 7)
    foo = s.abs
    for this in s.detect(1000, 10000):
        print(nptime.from_timedelta(timedelta(milliseconds=this[0] * 10)), this[1], this[2])
