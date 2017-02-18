import numpy as np


class FrequencyError(Exception):
    """ Custom exception for errors during frequency calculation """
    pass


class Frequency(object):
    def __init__(self, times, values):
        """
        Prepare a Frequency object to calculate the frequency of oscillations

        Args:
            times (Array):  epoch times in millisecods
            values (Array): values
        """
        if not len(times) == len(values):
            raise FrequencyError("Lengths of times and values did not match")
        self.t = np.array(times)
        self.v = np.array(values)

    def inversions_basic(self):
        """
        Times when the direction flipped, no regression

        Yields:
            int: epoch times in millisecods
        """
        t = self.t
        v = self.v
        i = 0
        while i < len(t):
            # Initial state
            if i == 0:
                last_state = True if v[i] > 0 else False
                i = 1
                continue

            # Have we flipped?
            positive = True if v[i] > v[i - 1] else False
            if positive != last_state:
                last_state = positive
                yield(t[i])
            i += 1

    def frequency_basic(self):
        """
        Calculate approximate frequency as a function of time based
        on inversions.  Performs no regression.

        Yields:
            (time, frequency(Hz))
        """
        last_time = None
        for t in self.inversions_basic():
            # Initial state
            if not last_time:
                last_time = t
                continue

            # Calculate frequency based on the last inversion
            half_wave = t - last_time
            freq = 500 / half_wave
            yield (t, freq)
            last_time = t
