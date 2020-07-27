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
COLORS = ['r', 'g', 'b', 'c', 'pink', 'grey']
# Ensure lots of colors
COLORS.extend(COLORS)
COLORS.extend(COLORS)

# Options
NUM_ROW = "num_row"
NUM_COL = "num_col"
COLUMNS = "columns"
TIMESERIES2 = "timeseries2"
MARKER1 = "marker1"
MARKER2 = "marker2"
LEGEND = "legend"


########################################
class _Positioner(object):
    # Determines the position of a plot

    def __init__(self, num_plot, num_row=1, num_col=None):
        assigned = lambda v: not v in [None, 0]
        #
        self.num_row = num_row
        self.num_col = num_col
        self.num_plot = num_plot
        if (not assigned(self.num_row)) and assigned(self.num_col):
            self.num_row = int(num_plot/num_col)
        elif (not assigned(self.num_col)) and assigned(self.num_row):
            self.num_col = int(num_plot/num_row)
        elif (not assigned(self.num_col)) and (not assigned(self.num_row)):
            if self.num_plot != self.num_row*self.num_col:
                raise ValueError("Number of plots != num_row*num_col")
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
    """
    Class that manages plot options.
    """

    def __init__(self):
        self.columns = []  # Columns to plot
        self.figsize = (8, 6)
        self.legend = None # Tuple of str for legend
        self.num_col = None  # Default value
        self.num_row = 1  # Default value
        self.marker1 = None  # Marker for timerseries1
        self.marker2 = None  # Marker for timeseries2
        self.num_row = None  # rows of plots
        self.num_col = None  # columns of plots
        self.timeseries2 = None  # second timeseries
        self.title = None
        self.suptitle = None  # Figure title
        self.xlabel = "time"  # x axis title
        self.xlim = None  # order pair of lower and upper
        self.xticklabels = None
        self.ylabel = None
        self.ylim = None  # order pair of lower and upper
        self.yticklabels = None

    def __str__(self):
        stg = """
            Supported plotting options are:
                columns: List of columns to plot
                figsize: (horizontal width, vertical height)
                legend: Tuple of str for legend
                marker1: Marker for timerseries1
                marker2: Marker for timeseries2
                num_row: rows of plots
                num_col: columns of plots
                timeseries2: second timeseries
                title: plot title
                suptitle: Figure title
                xlabel: x axis title
                xlim: order pair of lower and upper
                xticklabels: list of labels for x ticks
                ylabel: label for x axis
                ylim: order pair of lower and upper
                yticklabels: list of labels for y ticks
            """
        return stg

    def set(self, attribute, value, is_override=True):
        if attribute in self.__dict__.keys():
            if is_override or (self.__getattribute__(attribute) is None):
                self.__setattr__(attribute, value)
        else:
            raise ValueError("Unknown plot option: %s" % attribute)

    def setDict(self, dct, excludes=[]):
        """
        Changes setting based on attributes, values in a dictionary.
        Only those attributes that are initialized are consumed.

        Parameters
        ----------
        dct: dict
            dictionary of attribute value pairs
        excludes: list-sstr
            attributes not to be set
        """
        for attribute, value in dct.items():
            if not attribute in excludes:
                self.set(attribute, value, is_override=True)

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
          
    def __init__(self, is_plot=True):
        """
        Parameters
        ---------
        is_plot: boolean
            display the plot
               
        Usage
        ____
            
        plotter = TimeseriesPlotter(timeseries)
        plotter.plotTimeSingle()  # Single variable plots for one timeseries
        """
        self.is_plot = is_plot

    def _setup(self, timeseries1, options=PlotOptions(), **kwargs):
        """
        Sets up plot information.

        Parameters
        ---------
        is_plot: boolean
            display the plot

        Returns
        -------
        PlotOptions, figure, axes

        Notes
        -----
        1. Values must be set for options.num_row, options.num_col
               
        """
        options.setDict(kwargs, excludes=[NUM_ROW, NUM_COL])  # Record the options
        if len(options.columns) == 0:
            options.columns = timeseries1.colnames
        #
        if options.figsize is not None:
            fig, axes = plt.subplots(options.num_row, options.num_col,
                  figsize=options.figsize)
            plt.subplots_adjust(wspace=0.5)
        else:
            fig, axes = plt.subplots(options.num_row, options.num_col)
        if "matplotlib" in str(type(axes)):
            axes = np.array([axes])
        if axes.ndim == 1:
            axes = np.reshape(axes, (options.num_row, options.num_col))
        elif axes.ndim == 2:
            pass
        else:
            raise RuntimeError("Should not get here")
        return options, fig, axes

    def _initializeRowColumn(self, timeseries1, max_col=None, **kwargs):
        """
        Determines values for number of rows and columns.

        Returns
        -------
        PlotOptions
            assigns values to options.num_row, options.num_col
        """
        options = PlotOptions()
        if max_col is None:
            if COLUMNS in kwargs:
                max_col = len(kwargs[COLUMNS])
            else:
                max_col = len(timeseries1.colnames)
        # States
        has_col = False
        has_row = False
        if NUM_ROW in kwargs:
            options.num_row = kwargs[NUM_ROW]
            has_row = True
        if NUM_COL in kwargs:
            options.num_col = kwargs[NUM_COL]
            has_col = True
        # Assignments based on state
        if has_row and has_col:
            # Have been assigned
            pass
        elif has_row and (not has_col):
            options.num_col = int(max_col/options.num_row)
        elif (not has_row) and has_col:
            options.num_row = int(max_col/options.num_col)
        else:
           options.num_row = 1
           options.num_col = max_col
        if max_col > options.num_row*options.num_col:
           options.num_row += 1
        #
        return options

    def plotTimeSingle(self, timeseries1, **kwargs):
        """
        Constructs plots of single columns, possibly with a second
        timeseries.

        Parameters
        ---------
        timeseries1: NamedTimeseries
        kwargs: dict
            See PlotOptions (help(PlotOptions))
               
        Usage
        ____
            
        """
        options = self._initializeRowColumn(timeseries1, **kwargs)
        options, fig, axes = self._setup(timeseries1, options=options, **kwargs)
        positioner = _Positioner(len(options.columns), options.num_row, options.num_col)
        base_options = copy.deepcopy(options)
        for idx, variable in enumerate(options.columns):
            options = copy.deepcopy(base_options)
            row, col = positioner.pos(idx)
            ax = axes[row, col]
            if options.ylabel is None:
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
            if options.timeseries2 is not None:
                if options.marker2 is None:
                    ax.plot(options.timeseries2[TIME], options.timeseries2[variable], color="red", label=LABEL2)
                else:
                    ax.scatter(options.timeseries2[TIME], options.timeseries2[variable], color="red", label=LABEL2,
                          marker=options.marker2)
                if options.legend is None:
                    options.set("legend", [LABEL1, LABEL2])
            options.do(ax)
        if self.is_plot:
            plt.show()

    def plotTimeMultiple(self, timeseries1, **kwargs):
        """
        Constructs a plot with all columns in a timeseries.
        If there is a second timeseries, then there are 2 plots.

        Parameters
        ---------
        timeseries1: NamedTimeseries
        kwargs: dict
            See PlotOptions (help(PlotOptions))
        """
        max_col = 2 if TIMESERIES2 in kwargs else 1
        options = self._initializeRowColumn(timeseries1, max_col=max_col, **kwargs)
        if (NUM_ROW in kwargs) and (NUM_COL in kwargs):
            if (kwargs[NUM_ROW] == 1) and (kwargs[NUM_COL] == 1):
                options.num_row = 1
                options.num_col = 1
        options, fig, axes = self._setup(timeseries1, options=options, **kwargs)
        #
        def multiPlot(timeseries, ax, marker=None):
            if marker is None:
                for idx, col in enumerate(timeseries.colnames):
                    ax.plot(timeseries[TIME], timeseries[col], color=COLORS[idx])
            else:
                for idx, col in enumerate(timeseries.colnames):
                    ax.scatter(timeseries[TIME], timeseries[col], color=COLORS[idx],
                          marker=marker)
            options.legend = timeseries.colnames
            options.do(ax)
        #
        if options.timeseries2 is not None:
            if len(axes.flatten()) == 1:
                options.num_row = 2
                options.num_col = 1
                axes = np.array([ axes[0,0], axes[0,0] ])
                axes = np.reshape(axes, (options.num_row, options.num_col))
            positioner = _Positioner(2, options.num_row, options.num_col)
            markers = [options.marker1, options.marker2]
            for idx, ts in enumerate([timeseries1, options.timeseries2]):
                row, col = positioner.pos(idx)
                ax = axes[row, col]
                multiPlot(ts, ax, markers[idx])
                options.do(ax)
        else:
            multiPlot(timeseries1, axes[0, 0], options.marker1)
        if self.is_plot:
            plt.show()

    def plotValuePairs(self, timeseries, pairs, **kwargs):
        """
        Constructs plots of values of column pairs for a single
        timeseries.

        Parameters
        ---------
        timeseries: NamedTimeseries
        kwargs: dict
            See PlotOptions (help(PlotOptions))
        """
        options = self._initializeRowColumn(timeseries,
              max_col=len(pairs), **kwargs)
        options, fig, axes = self._setup(timeseries, options=options, **kwargs)
        positioner = _Positioner(len(options.columns), options.num_row, options.num_col)
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
