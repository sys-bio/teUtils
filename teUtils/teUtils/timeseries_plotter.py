"""
A TimeseriesPlotter visualizes timeseries data, especially for comparing
time series.

Usage:
"""

from named_timeseries import NamedTimeseries, TIME

import matplotlib.pyplot as plt
import numpy as np


########################################
class PlotOptions(object):

    def __init__(self):
        self.xlabel = "time"
        self.ylabel = ""
        self.title = ""
        self.ylim = None
        self.xlim = None


########################################
class TimeseriesPlotter(object):
          
    def __init__(self, timeseries, options=options):
        """
            Parameters
            ---------
            timeseries: NamedTimeseries
            options: PlotOptions
                   
            Usage
            ____
                
        """
        self.timeseries = timeseries
        self.options = options
        pass

    def plotWithCommonTime(self, variables, options=options):
        """
            Plots the selected variables on a common time axis.

            Parameters
            ---------
            timeseries: NamedTimeseries
                   
            Usage
            ____
                
        """
