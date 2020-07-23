# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein

    A TimeseriesPlotter visualizes timeseries data, especially for comparing
    time series.
    
    All plots are line plots with the x-axis as time. The following
    can be varied:
      single or multiple columns in a plot
      one or two timeseries plot
    
    Usage:
"""

from teUtils.named_timeseries import NamedTimeseries, TIME

import copy
import matplotlib.pyplot as plt
import numpy as np


LABEL1 = "1"
LABEL2 = "2"


########################################
class _Positioner(object):
    # Determines the position of a plot

    def __init__(self, num_plot, num_row=1, num_col=None):
        self.num_row = num_row
        self.num_col = num_col
        self.num_plot = num_plot
        if self.num_row is None:
            self.num_row = int(num_plot/num_col)
        if self.num_col is None:
            self.num_col = int(num_plot/num_row)
        self.row = 0  # Current row
        self.col = 0  # Current column

    def pos(self, index):
        self.row = index // self.num_col
        self.col = index % self.num_col
        return self.row, self.col

    def isFirstColumn(self):
        return self.col == 0

    def isLastRow(self):
        return self.row == self.num_row - 1
   
 
#########################
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
        self.marker1 = None
        self.marker2 = None
        self.figsize = (8, 6)

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
          
    def __init__(self, options=PlotOptions(), is_plot=True):
        """
        Parameters
        ---------
        options: PlotOptions
        is_plot: boolean
            display the plot
               
        Usage
        ____
            
        plotter = TimeseriesPlotter(timeseries)
        plotter.plotTimeSingle()  # Single variable plots for one timeseries
        """
        self.options = options
        self.is_plot = is_plot

    def plotTimeSingle(self, timeseries1, num_row=1, num_col=None, 
          columns=None, timeseries2=None, options=PlotOptions()):
        """
        Constructs plots of single columns, possibly with a second
        timeseries.

        Parameters
        ---------
        timeseries1: NamedTimeseries
        num_row: int
            number of rows in the plot
        num_col: int
            number of columns in the plot
            default is the number of columns
        columns: list-str
            list of columns in the timeseries
        timeseries2: NamedTimeseries
            second timeseries with the same columns and times
        options: PlotOptions
               
        Usage
        ____
            
        """
        if columns is None:
            columns = timeseries1.colnames
        positioner = _Positioner(len(columns), num_row=num_row,
            num_col=num_col)
        #
        if options.figsize is not None:
            fig, axes = plt.subplots(positioner.num_row, positioner.num_col,
                  figsize=options.figsize)
            plt.subplots_adjust(wspace=0.5)
        else:
            fig, axes = plt.subplots(positioner.num_row, positioner.num_col)
        if len(np.shape(axes)) == 1:
            axes = np.reshape(axes, (positioner.num_row, positioner.num_col))
        base_options = copy.deepcopy(options)
        for idx, variable in enumerate(columns):
            options = copy.deepcopy(base_options)
            row, col = positioner.pos(idx)
            ax = axes[row, col]
            options.set("ylabel", "concentration")
            options.title = variable
            if not positioner.isFirstColumn():
                options.ylabel =  ""
                options.set("ylabel", "")
            if not positioner.isLastRow():
                options.xlabel =  ""
            if options.marker1 is None:
                ax.plot(timeseries1[TIME], timeseries1[variable], color="blue", label=LABEL1)
            else:
                ax.scatter(timeseries1[TIME], timeseries1[variable], color="blue", label=LABEL1,
                      marker=options.marker1)
            if timeseries2 is not None:
                if options.marker2 is None:
                    ax.plot(timeseries2[TIME], timeseries2[variable], color="red", label=LABEL2)
                else:
                    ax.scatter(timeseries2[TIME], timeseries2[variable], color="red", label=LABEL2,
                          marker=options.marker2)
                options.set("legend", [LABEL1, LABEL2])
            options.do(ax)
        if self.is_plot:
            plt.show()

    def plotTimeMultiple(self, timeseries1,
          columns=None, timeseries2=None, options=PlotOptions()):
        """
        Constructs a plot with all columns in a timeseries.
        If there is a second timeseries, then there are 2 plots.

        Parameters
        ---------
        timeseries1: NamedTimeseries
        columns: list-str
            list of columns in the timeseries
        timeseries2: NamedTimeseries
            second timeseries with the same columns and times
        options: PlotOptions
               
        Usage
        ____
            
        """
        if columns is None:
            columns = timeseries1.colnames
        #
        def multiPlot(timeseries, ax):
            df = timeseries.to_dataframe()[columns]
            df.plot(ax=ax)
            options.do(ax)
        #
        if timeseries2 is not None:
            if options.figsize is not None:
                fig, axes = plt.subplots(2, figsize=options.figsize)
            else:
                fig, axes = plt.subplots(2)
            for idx, ts in enumerate([timeseries1, timeseries2]):
                multiPlot(ts, axes[idx])
                options.do(axes[idx])
        else:
            if options.figsize is not None:
                fig, ax = plt.subplots(figsize=options.figsize)
            else:
                fig, ax = plt.subplots()
            multiPlot(timeseries1, ax)
        if self.is_plot:
            plt.show()

    def plotValuePairs(self, timeseries, pairs, num_row=1, num_col=None,
          options=PlotOptions()):
        """
        Constructs plots of values of column pairs for a single
        timeseries.

        Parameters
        ---------
        timeseries: NamedTimeseries
        num_row: int
            number of rows in the plot
        num_col: int
            number of columns in the plot
            default is the number of pairs 
        pairs: list-tuple-str
            list of pairs of columns
        options: PlotOptions
               
        Usage
        ____
            
        """
        positioner = _Positioner(len(pairs), num_row=num_row, num_col=num_col)
        #
        if options.figsize is not None:
            fig, axes = plt.subplots(positioner.num_row, positioner.num_col,
                  figsize=options.figsize)
            plt.subplots_adjust(wspace=0.5)
        else:
            fig, axes = plt.subplots(num_row, num_col)
        if (len(np.shape(axes)) == 1) or (len(np.shape(axes)) == 0):
            axes = np.reshape(axes, (positioner.num_row, positioner.num_col))
        #
        base_options = copy.deepcopy(options)
        for idx, pair in enumerate(pairs):
            options = copy.deepcopy(base_options)
            var1 = pair[0]
            var2 = pair[1]
            row, col = positioner.pos(idx)
            ax = axes[row, col]
            options.xlabel = var1
            options.ylabel = var2
            options.title = "%s v. %s" % (var1, var2)
            if not positioner.isFirstColumn():
                options.ylabel =  ""
                options.set("ylabel", "")
            if not positioner.isLastRow():
                options.xlabel =  ""
            ax.scatter(timeseries[var1], timeseries[var2], marker='o')
            options.xlabel = var1
            options.ylabel = var2
            options.do(ax)
        if self.is_plot:
            plt.show()
        
