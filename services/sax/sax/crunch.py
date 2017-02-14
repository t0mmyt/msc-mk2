import numpy as np


class Sax(object):
    def __init__(self, t, v):
        self.t = t
        self.v = v


class Paa(object):
    def __init__(self, t, v):
        """
        Create and calculate PAA

        Parameters
        ----------
        time : numpy.array
            Times in epoch ms
        value : numpy.array
            Y values
        """
        pass

    # def _normalise_to_zero(self):
    #     """
    #     Return numpy array normalised to zero by subtracting the mean from each
    #     value
    #
    #     Parameters
    #     ----------
    #     v : numpy.array (1D)
    #         Array to normalise
    #     """
    #     mu = np.mean(v)
    #     v = np.subtract(v, mu)
    #     return v
