# -*- coding: utf-8 -*-
"""
Created on Aug 14, 2020

@author: joseph-hellerstein

Manages options for a figure of plots.

A figure may contain 1 or more plot, and each plot may contain
1 or more line. An option is applied to a single scope: figure, plot, line.
If the option is singled valued, then it applies to all instances
of the scope. If it has multiple values, then the index of the value
corresponds to the instance within the scope. A figure scope is
always single valued.
"""

from teUtils._statementManager import StatementManager

from docstring_expander.kwarg import Kwarg
import matplotlib.pyplot as plt
import numpy as np


PLOT = "plot"  # identifies a plotting function
EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)"
# Options
ALPHA = "alpha"
BINS = "bins"
COLUMNS = "columns"
COLOR = "color"
FIGSIZE = "figsize"
LEGEND = "legend"
LINESTYLE = "linestyle"
MARKER = "marker"
MARKERSIZE = "markersize"
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
   
 
#########################
class ExKwarg(Kwarg):
    """Extends Kwarg with scope information."""
    FIGURE = "figure"
    PLOT = "plot"
    LINE = "line"

    def __init__(self, name:str, scope:str, doc:str=None, 
              dtype:type=None, default:object=None):
        self.scope = scope
        super().__init__(name, dtype=dtype, default=default)
        shortScope = "(%s)" % self.scope[0]
        self.doc = "%s %s" % (shortScope, doc)
        

# Options common to most plots
BASE_OPTIONS = [COLUMNS, COLOR, LEGEND, LINESTYLE, MARKER, NUM_COL, MARKERSIZE,
      NUM_ROW, SUBPLOT_WIDTH_SPACE, SUPTITLE, TIMESERIES2, TITLE,
      TITLE_FONTSIZE, TITLE_POSITION, XLABEL, XLIM, YLABEL, YLIM]
FF = ExKwarg.FIGURE
PP = ExKwarg.PLOT
LL = ExKwarg.LINE
KWARGS = [
      ExKwarg(ALPHA, LL, doc="transparency; in [0, 1]", dtype=float),
      ExKwarg(BINS, PP, doc="number of bins in a histogram plot", dtype=int),
      ExKwarg(COLOR, LL, doc="color of the line", dtype=str, default="blue"),
      ExKwarg(COLUMNS, FF, doc= "List of columns to plot", dtype=list, default=[]),
      ExKwarg(FIGSIZE, FF, doc= "(horizontal width, vertical height)",
      dtype=list, default=[8, 6]),
      ExKwarg(LEGEND, FF, doc= "Tuple of str for legend", dtype=list),
      ExKwarg(LINESTYLE, LL, doc= "Line style", dtype=str),
      ExKwarg(MARKER, LL, doc= "Marker for line", dtype=str),
      ExKwarg(MARKERSIZE, LL, doc="Size of marker for the line; >0",
      dtype=float),
      ExKwarg(NUM_ROW, FF, doc= "rows of plots", dtype=int),
      ExKwarg(NUM_COL, FF, doc= "columns of plots", dtype=int),
      ExKwarg(SUBPLOT_WIDTH_SPACE, FF, doc= "horizontal space between plots",
      dtype=float),
      ExKwarg(TIMESERIES2, FF, doc= "second timeseries"),
      ExKwarg(TITLE, PP, doc= "plot title", dtype=str),
      ExKwarg(TITLE_FONTSIZE, FF, doc= "point size for title", dtype=float),
      ExKwarg(TITLE_POSITION, FF,
      doc= "(x, y) relative position; x,y in [0, 1]; (0,0) is lower left."),
      ExKwarg(SUPTITLE, FF, doc= "Figure title", dtype=str),
      ExKwarg(XLABEL, PP, doc= "x axis title", dtype=str),
      ExKwarg(XLIM, FF, doc= "order pair of lower and upper", dtype=list),
      ExKwarg(XTICKLABELS, FF, doc= "list of labels for x ticks", dtype=list),
      ExKwarg(YLABEL, FF, doc= "label for x axis", dtype=str),
      ExKwarg(YLIM, FF, doc= "order pair of lower and upper", dtype=str),
      ExKwarg(YTICKLABELS, FF, doc= "list of labels for y ticks", dtype=list),
      ]
KWARG_DCT = {k.name: k for k in KWARGS}
AX_STATEMENT_KW = {
      MARKERSIZE: 's',
      }
TRAILER = """

A figure may contain 1 or more plot, and each plot may contain
1 or more line. Figure (f), plot (p), and line (c) are the possible
scope of an option.
If the option is singled valued, then it applies to all instances
of its scope. If it has multiple values, then the index of the value
corresponds to the instance within the scope. A figure scope is
always single valued.
"""
   
 
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

    def get(self, name, figIdx=None, plotIdx:int=None, lineIdx:int=None):
        """
        Return the value for this instance of the option.

        Parameters
        ----------
        name: str
            option name
        figIdx: int
            index of the Figure. Always 0.
        plotIdx: int
            index of the plot
        lineIdx: int
            index of the line
       
        Returns
        -------
        object

        Notes
        -----
        1. Must detect single vs. multi-valued instances.
        """
        # Initialize and validate
        exkwarg = KWARG_DCT[name]
        idxDct = {
              ExKwarg.FIGURE: figIdx,
              ExKwarg.PLOT: plotIdx,
              ExKwarg.LINE: lineIdx,
              }
        # Get the value
        value = self.__getattribute__(name)
        idx = idxDct[exkwarg.scope]
        if idx is None:
            return value
        if value is None:
            return value
        if isinstance(value, exkwarg.dtype):
            return value
        if not isinstance(value, list):
            try:
                # Try to coerce type
                value = exkwarg.dtype(value)
                return value
            except:
                pass
            raise ValueError("Invalid data type for option %s" % name)
        return value[idxDct[exkwarg.scope]]

    def do(self, ax, statement:StatementManager=None, **kwargs):
        """
        Enacts options taking into account the scope of the option.
        Note that options related to NUM_ROW, NUM_COL are handled elsewhere.

        Parameters
        ----------
        ax: Matplotlib.Axes
        statement: StatementManager
        kwargs: dict
            arguments for get
        """
        def setLineAttribute(ax, name:str, statement:StatementManager=None,
              **kwargs):
            """
            Updates the statement for the line being plotted.
            """
            if statement is None:
                return
            if "Axes.plot" in str(statement.func):
                # Some options are not alloed for line plots
                if name in [MARKER, MARKERSIZE]:
                    return
            value = self.get(name, **kwargs)
            if value is not None:
                if name in AX_STATEMENT_KW.keys():
                    dct={AX_STATEMENT_KW[name]: value}
                else:
                    dct={name: value}
                statement.addKwargs(**dct)
        #
        def setFigPlotAttribute(ax, name:str, **kwargs):
            value = self.__getattribute__(name)
            if value is not None:
                func = eval("ax.set_%s" % name)
                statement = StatementManager(func)
                statement.addPosarg(self.get(name, **kwargs))
                statement.execute()
        # Attributes processed by this method
        names = [ALPHA, COLOR, LINESTYLE, MARKER, MARKERSIZE, XLABEL, YLABEL,
             XLIM, XTICKLABELS, YLIM, YTICKLABELS]
        for name in names:
            kwarg = KWARG_DCT[name]
            if kwarg.scope == ExKwarg.LINE:
                setLineAttribute(ax, name, statement=statement, **kwargs)
            else:
                setFigPlotAttribute(ax, name, **kwargs)
        if statement is not None:
            statement.execute()
        # Other attributes
        if self.title is not None:
            title = self.get(TITLE, **kwargs)
            titlePosition = self.get(TITLE_POSITION, **kwargs)
            titleFontsize = self.get(TITLE_FONTSIZE, **kwargs)
            statement = StatementManager(ax.set_title)
            statement.addPosarg(title)
            if self.titlePosition is not None:
                statement.addKwargs(position=titlePosition)
                statement.addKwargs(transform=ax.transAxes)
            if self.titleFontsize is not None:
                statement.addKwargs(fontsize=titleFontsize)
            statement.execute()
        value = self.__getattribute__(SUBPLOT_WIDTH_SPACE)
        if value is not None:
            plt.subplots_adjust(wspace=value)
        if self.legend is not None:
            ax.legend(self.legend)
        if self.suptitle is not None:
            plt.suptitle(self.suptitle)
