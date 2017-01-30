'''
Class to generate graphs via matplotlib
'''
from io import BytesIO
import datetime as dt
import cherrypy as cp
import numpy as np
import requests
import matplotlib as mpl
mpl.use('agg')
from matplotlib import pyplot as plt


class Graph(object):
    pass
