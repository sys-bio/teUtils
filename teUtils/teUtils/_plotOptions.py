# -*- coding: utf-8 -*-
"""
Created on Aug 14, 2020

@author: joseph-hellerstein

Manages options for plotting.
"""

from teUtils._statementManager import StatementManager

import copy
import matplotlib.pyplot as plt
import numpy as np


PLOT = "plot"  # identifies a plotting function
EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)"
# Options
BINS = "bins"
COLUMNS = "columns"
LEGEND = "legend"
MARKER1 = "marker1"
MARKER2 = "marker2"
NUM_COL = "numCol"
NUM_ROW = "numRow"
SUBPLOT_WIDTH_SPACE = "subplot_width_space"
TIMESERIES2 = "timeseries2"
TITLE_POSITION = "titlePosition"
XLABEL = "xlabel"
YLABEL = "ylabel"
   
 
#########################
class PlotOptions(object):
    """
    Container for plot options. Common method for activating options for an axis.
    """

    def __init__(self):
        ### PRIVATE
        self._axes = None
        ### PUBLIC
        self.bins = None
        self.color1 = "blue"  # Color for first plot
        self.color2 = "red"  # Color for second plot
        self.columns = []  # Columns to plot
        self.figsize = (8, 6)
        self.legend = None # Tuple of str for legend
        self.numCol = None  # Default value
        self.numRow = 1  # Default value
        self.marker1 = None  # Marker for timerseries1
        self.markersize1 = None  # Size of the marker if present
        self.marker2 = None  # Marker for timeseries2
        self.markersize2 = None  # Size of the marker if present
        self.numRow = None  # rows of plots
        self.numCol = None  # columns of plots
        self.timeseries2 = None  # second timeseries
        self.title = None
        self.titlePosition = None  # Relative position in plot (x, y)
        self.subplotWidthSpace = None
        self.suptitle = None  # Figure title
        self.xlabel = "time"  # x axis title
        self.xlim = None  # order pair of lower and upper
        self.xticklabels = None
        self.ylabel = None
        self.ylim = None  # order pair of lower and upper
        self.yticklabels = None
        self.figure = None

    def __str__(self):
        stg = """
            Supported plotting options are:
                bins: int for number of bins in a histogram plot
                color1: color of first plot
                color2: color of second plot
                columns: List of columns to plot
                figsize: (horizontal width, vertical height)
                legend: Tuple of str for legend
                marker1: Marker for timerseries1
                markersize1: size of marker (>= 0)
                marker2: Marker for timeseries2
                markersize2: size of marker (>= 0)
                numRow: rows of plots
                numCol: columns of plots
                subplotWidthSpace: horizontal space between plots
                timeseries2: second timeseries
                title: plot title
                titlePosition: relative position in plot (x, y); x,y in [0, 1]; (0,0) is lower left.
                suptitle: Figure title
                xlabel: x axis title
                xlim: order pair of lower and upper
                xticklabels: list of labels for x ticks
                ylabel: label for x axis
                ylim: order pair of lower and upper
                yticklabels: list of labels for y ticks
            """
        return stg

    def set(self, attribute, value, isOverride=False):
        if attribute in self.__dict__.keys():
            if isOverride or (self.__getattribute__(attribute) is None):
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
                self.set(attribute, value, isOverride=True)

    def initialize(self, timeseries, numRow=None, numCol=None, **kwargs):
        """
        Initializes information for plotting.

        Parameters
        ---------
        timeseries: NamedTimeseries
            a timeseries to be plotted
        numRow: int
        numCol: int
        kwargs: dict
        """
        if numRow is not None:
            self.numRow = numRow
        if numCol is not None:
            self.numCol = numCol
        self.setDict(kwargs, excludes=[NUM_ROW, NUM_COL])  # Record the options
        if len(self.columns) == 0:
            self.columns = timeseries.colnames
        if self.figsize is None:
             self.figsize = plt.gca().figure.get_size_inches()

    def do(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        # Title
        if self.title is not None:
            manager = StatementManager(ax.set_title)
            manager.addPosarg(self.title)
            if self.titlePosition is not None:
                manager.addKwargs(position=self.titlePosition)
                manager.addKwargs(transform=ax.transAxes)
            manager.execute()
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
        if self.subplotWidthSpace is not None:
            plt.subplots_adjust(wspace=self.subplotWidthSpace)
        if self.suptitle is not None:
            plt.suptitle(self.suptitle)
