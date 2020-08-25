# -*- coding: utf-8 -*-
"""
Created on Aug 14, 2020

@author: joseph-hellerstein

Manages options for plotting.
"""

from teUtils._statementManager import StatementManager

from docstring_expander.kwarg import Kwarg
import matplotlib.pyplot as plt
import numpy as np


PLOT = "plot"  # identifies a plotting function
EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)"
# Options
BINS = "bins"
COLUMNS = "columns"
COLOR1 = "color1"
COLOR2 = "color2"
FIGSIZE = "figsize"
LEGEND = "legend"
MARKER1 = "marker1"
MARKERSIZE1 = "markersize1"
MARKER2 = "marker2"
MARKERSIZE2 = "markersize2"
NUM_COL = "numCol"
NUM_ROW = "numRow"
SUBPLOT_WIDTH_SPACE = "subplotWidthSpace"
SUPTITLE = "suptitle"
TIMESERIES2 = "timeseries2"
TITLE = "title"
TITLE_FONTSIZE = "titleFontsize"
TITLE_POSITION = "titlePosition"
XLABEL = "xlabel"
XLIM = "xlim"
XTICKLABELS = "xticklabels"
YLABEL = "ylabel"
YTICKLABELS = "yticklabels"
YLIM = "ylim"
# Options common to most plots
BASE_OPTIONS = [COLUMNS, COLOR1, COLOR2, LEGEND, MARKER1, MARKER2,
      NUM_COL, MARKERSIZE1, MARKERSIZE2,
      NUM_ROW, SUBPLOT_WIDTH_SPACE, SUPTITLE, TIMESERIES2, TITLE,
      TITLE_FONTSIZE, TITLE_POSITION, XLABEL, XLIM, YLABEL, YLIM]
KWARGS = [
      Kwarg(BINS, doc="number of bins in a histogram plot", dtype=int),
      Kwarg(COLOR1, doc="color of first plot", dtype=str, default="blue"),
      Kwarg(COLOR2, doc= "color of second plot", dtype=str, default="red"),
      Kwarg(COLUMNS, doc= "List of columns to plot", dtype=list, default=[]),
      Kwarg(FIGSIZE, doc= "(horizontal width, vertical height)",
      dtype=list, default=[8, 6]),
      Kwarg(LEGEND, doc= "Tuple of str for legend", dtype=list),
      Kwarg(MARKER1, doc= "Marker for timerseries1", dtype=str),
      Kwarg(MARKERSIZE1, doc="Size of marker for timeseries1; >0", dtype=float),
      Kwarg(MARKER2, doc= "Marker for timerseries2", dtype=str),
      Kwarg(MARKERSIZE2, doc="Size of marker for timeseries2; >0", dtype=float),
      Kwarg(NUM_ROW, doc= "rows of plots", dtype=int),
      Kwarg(NUM_COL, doc= "columns of plots", dtype=int),
      Kwarg(SUBPLOT_WIDTH_SPACE, doc= "horizontal space between plots", dtype=float),
      Kwarg(TIMESERIES2, doc= "second timeseries"),
      Kwarg(TITLE, doc= "plot title", dtype=str),
      Kwarg(TITLE_FONTSIZE, doc= "point size for title", dtype=float),
      Kwarg(TITLE_POSITION,
      doc= "relative position in plot (x, y); x,y in [0, 1]; (0,0) is lower left.",
      dtype=list),
      Kwarg(SUPTITLE, doc= "Figure title", dtype=str),
      Kwarg(XLABEL, doc= "x axis title", dtype=str),
      Kwarg(XLIM, doc= "order pair of lower and upper", dtype=list),
      Kwarg(XTICKLABELS, doc= "list of labels for x ticks", dtype=list),
      Kwarg(YLABEL, doc= "label for x axis", dtype=str),
      Kwarg(YLIM, doc= "order pair of lower and upper", dtype=str),
      Kwarg(YTICKLABELS, doc= "list of labels for y ticks", dtype=list),
      ]
   
 
#########################
class PlotOptions(object):
    """
    Container for plot options. Common method for activating options for an axis.
    """

    def __init__(self):
        ### PRIVATE
        self._axes = None
        ### PUBLIC
        self.figure = None
        for kwarg in KWARGS:
          self.set(kwarg.name, kwarg.default, isForce=True)

    def __str__(self):
        stg = "Supported plotting options are:\n"
        for kwarg in KWARGS:
          stg += "  %s: %s" % (kwarg.name, kwarg.doc)
        return stg

    def set(self, attribute, value, isOverride=False, isForce=False):
        isOK = False
        if isForce:
            isOK = True
        if attribute in self.__dict__.keys():
            isOK = True
        if isOK:
            if isForce or isOverride  \
                  or (self.__getattribute__(attribute) is None):
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
            if self.titleFontsize is not None:
                manager.addKwargs(fontsize=self.titleFontsize)
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
