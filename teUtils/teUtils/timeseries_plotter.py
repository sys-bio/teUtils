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

import copy
import matplotlib.pyplot as plt
import numpy as np


########################################
class PlotOptions(object):

    def __init__(self):
        self.xlabel = "time"
        self.ylabel = None
        self.title = None
        self.ylim = None
        self.xlim = None
        self.xticklabels = None
        self.yticklabels = None
        self.legend = None
        self.suptitle = None

    def set(self, attribute, value):
        if not attribute in self.__dict__.keys():
            raise ValueError("Unknown PlotOptions: %s" % attribute)
        # Don't override a user specification
        if self.__getattribute__(attribute) is None:
            self.__setattr__(attribute, value)

    def do(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.title)
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        if self.xticklabels is not None:
            ax.set_xticklabels(self.xticklabels)
        if self.yticklabels is not None:
            ax.set_yticklabels(self.yticklabels)
        if self.legend is not None:
            ax.legend(self.legend)
        if self.suptitle is not None:
            plt.suptitle(self.suptitle)


########################################
class TimeseriesPlotter(object):
          
    def __init__(self, timeseries, options=PlotOptions(), is_plot=True):
        """
        Parameters
        ---------
        timeseries: NamedTimeseries
        options: PlotOptions
        is_plot: boolean
            display the plot
               
        Usage
        ____
            
        plotter = TimeseriesPlotter(timeseries)
        plotter.plotSingle()  # Single variable plots for one timeseries
        """
        self.timeseries = timeseries
        self.options = options
        self.is_plot = is_plot

    def plotSingle(self, num_row=1, num_col=None, 
          variables=None, timeseries2=None, options=PlotOptions()):
        """
        Constructs plots of single variables, possibly with a second
        timeseries.

        Parameters
        ---------
        num_row: int
            number of rows in the plot
        num_col: int
            number of columns in the plot
            default is the number of variables
        variables: list-str
            list of variables in the timeseries
        timeseries2: NamedTimeseries
            second timeseries with the same variables and times
        options: PlotOptions
               
        Usage
        ____
            
        """
        if variables is None:
            variables = self.timeseries.colnames
        if num_col is None:
            num_col = len(variables)
        #
        fig, axes = plt.subplots(num_row, num_col)
        if len(np.shape(axes)) == 1:
            axes = np.reshape(axes, (num_row, num_col))
        for idx, variable in enumerate(variables):
            row = idx // num_col
            col = idx % num_col
            ax = axes[row, col]
            options = copy.deepcopy(options)
            options.set("ylabel", "concentration")
            options.set("title", variable)
            if col > 0:
                options.ylabel =  ""
                options.set("yticklabels", [])
                options.xlabel = ""
                options.set("ylabel", "")
            if row < len(variables) // num_col - 1:
                options.set("xticklabels", [])
                options.xlabel = ""
                options.ylabel =  ""
            ax.plot(self.timeseries[TIME], self.timeseries[variable], color="blue")
            if timeseries2 is not None:
                ax.plot(timeseries2[TIME], timeseries2[variable], color="red")
                options.set("legend", ("1", "2"))
            options.do(ax)
        if self.is_plot:
            plt.show()

    def plotMultiple(self,
          variables=None, timeseries2=None, options=PlotOptions()):
        """
        Constructs a plot with all variables in a timeseries.
        If there is a second timeseries, then there are 2 plots.

        Parameters
        ---------
        variables: list-str
            list of variables in the timeseries
        timeseries2: NamedTimeseries
            second timeseries with the same variables and times
        options: PlotOptions
               
        Usage
        ____
            
        """
        if variables is None:
            variables = self.timeseries.colnames
        #
        def multiPlot(timeseries, ax):
            df = timeseries.to_dataframe()
            df.plot(ax=ax)
            options.do(ax)
        #
        if timeseries2 is not None:
            fig, axes = plt.subplots(2)
            for idx, ts in enumerate([self.timeseries, timeseries2]):
                multiPlot(ts, axes[idx])
                options.do(axes[idx])
        else:
            fig, ax = plt.subplots()
            multiPlot(self.timeseries, ax)
        if self.is_plot:
            plt.show()
