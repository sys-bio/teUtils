"""
    A TimeseriesPlotter visualizes timeseries data, especially for comparing
    time series.
    
    All plots are line plots with the x-axis as time. The following
    can be varied:
      single or multiple variables in a plot
      one or two timeseries plot
    
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

    def do(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.title)
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)


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

    def plotSingle(self, num_row=1, num_col=None, 
          variables=None, other=timeseries, options=options):
        """
            Constructs a

            Parameters
            ---------
            num_row: int
                number of rows in the plot
            num_col: int
                number of columns in the plot
                default is the number of variables
            variables: list-str
                list of variables in the timeseries
            other: NamedTimeseries
                second timeseries with the same variables and times
            options: PlotOptions
                   
            Usage
            ____
                
        """
        if variables is None:
            variables = self.timeseries.colnames
        if num_col is None:
            num_col = len(variables)
        
