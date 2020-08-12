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
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME
from teUtils import _helpers

import copy
import matplotlib.pyplot as plt
import numpy as np


PLOT = "plot"  # identifies a plotting function
EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)"
LABEL1 = "1"
LABEL2 = "2"
COLORS = ['r', 'g', 'b', 'c', 'pink', 'grey']
# Ensure lots of colors
COLORS.extend(COLORS)
COLORS.extend(COLORS)
# Title positions
POS_MID = 0.5
POS_TOP = 0.9
# Options
BINS = "bins"
COLUMNS = "columns"
LEGEND = "legend"
MARKER1 = "marker1"
MARKER2 = "marker2"
NUM_COL = "numCol"
NUM_ROW = "numRow"
TIMESERIES2 = "timeseries2"
TITLE_POSITION = "titlePosition"
   
 
#########################
class PlotOptions(object):
    """
    Container for plot options. Common method for activating options for an axis.
    """

    def __init__(self):
        self.columns = []  # Columns to plot
        self.figsize = (8, 6)
        self.legend = None # Tuple of str for legend
        self.numCol = None  # Default value
        self.numRow = 1  # Default value
        self.marker1 = None  # Marker for timerseries1
        self.marker2 = None  # Marker for timeseries2
        self.numRow = None  # rows of plots
        self.numCol = None  # columns of plots
        self.timeseries2 = None  # second timeseries
        self.title = None
        self.titlePosition = None  # Relative position in plot (x, y)
        self.suptitle = None  # Figure title
        self.xlabel = "time"  # x axis title
        self.xlim = None  # order pair of lower and upper
        self.xticklabels = None
        self.ylabel = None
        self.ylim = None  # order pair of lower and upper
        self.yticklabels = None
        self.figure = None
        ############### PRIVATE ##################
        self._axes = None

    def __str__(self):
        stg = """
            Supported plotting options are:
                bins: int for number of bins in a histogram plot
                columns: List of columns to plot
                figsize: (horizontal width, vertical height)
                legend: Tuple of str for legend
                marker1: Marker for timerseries1
                marker2: Marker for timeseries2
                numRow: rows of plots
                numCol: columns of plots
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

    def set(self, attribute, value, isOverride=True):
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
        if self.titlePosition is None:
            ax.set_title(self.title)
        else:
            ax.set_title(self.title, 
                  position=self.titlePosition,
                  transform=ax.transAxes)
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
class LayoutManager(object):
    """
    Manages the position of plots on the figure by creating
    a mapping from a linear sequence of plots to positions
    in a 2-dimensional grid.

    The top level class is abstract. Subclasses must override
    the method _setAxes that mplements the above mapping.
    """

    def __init__(self, options, numPlot):
        """
        Manages allocation of space in subplot and sets up options
        accordingly.

        Parameters
        ---------
        options: PlotOptions
        """
        self.options = options
        self.numPlot = numPlot
        # Number of plot positions in the figure
        self.numPlotPosition = self.options.numRow*self.options.numCol
        self.figure, self.axes, self.axisPositions = self._setAxes()

    def _initializeAxes(self):
        """
        Common codes for setAxes() methods.
        
        Returns
        -------
        Maplotlib.Figure, Matplotlib.Axes
        """
        figure = plt.figure(figsize=self.options.figsize)
        axes = []
        plt.subplots_adjust(wspace=0.5)
        return figure, axes

    def _setAxes(self):
        """
        Implements the mapping from a linear sequence to positions in
        a two dimension grid for the figure.
        Must override.
        
        Returns
        -------
        Maplotlib.Figure, Matplotlib.Axes, list-tuple
        """
        raise RuntimeError("Must override.")

    def _calcRowColumn(self, index):
        """
        Returns row and column with 0 indexing for plot coordinates in figure.

        Parameters
        ----------
        index: int
        
        Returns
        -------
        int, int
        """
        row = index // self.options.numCol
        col = index % self.options.numCol
        return row, col

    def getAxis(self, index):
        """
        Returns the axis to use for the plot index.

        Parameters
        ----------
        index: int
        
        Returns
        -------
        Matplotlib.axes
        """
        return self.axes[index]

    def isFirstColumn(self, index):
        _, col = self.axisPositions[index]
        return col == 0

    def isFirstRow(self, index):
        row, _ = self.axisPositions[index]
        return row == 0

    def isLastCol(self, index):
        _, col = self.axisPositions[index]
        return col == self.options.numCol - 1

    def isLastRow(self, index):
        row, _ = self.axisPositions[index]
        return row == self.options.numRow - 1


####
class LayoutManagerSingle(LayoutManager):
    """
    LayoutManager for a figure consisting of one plot.
    """

    def _setAxes(self):
        """
        len(self.axes) == 1
        
        Returns
        -------
        Maplotlib.Figure, Matplotlib.Axes
        """
        figure, _ = self._initializeAxes()
        axes = np.array([plt.subplot(1, 1, 1)])
        return figure, axes, [(0, 0)]


####
class LayoutManagerMatrix(LayoutManager):
    """
    LayoutManager for a figure that is a matrix
    of plots, although not all entries need be present.
    """

    def _setAxes(self):
        """
        Linearizes the matrix counting across rows and then down
        by column.
        
        Returns
        -------
        Maplotlib.Figure, Matplotlib.Axes
        """
        figure, axes = self._initializeAxes()
        axisPositions = []
        for index in range(self.numPlotPosition):
            row, col = self._calcRowColumn(index)
            if index < self.numPlot:
                ax = plt.subplot2grid( (self.options.numRow,
                      self.options.numCol), (row, col))
                axisPositions.append((row, col))
            axes.append(ax)
        return figure, axes, axisPositions


####
class LayoutManagerLowerTriangular(LayoutManager):
    """
    LayoutManager for a figure that is an upper triangular plot.
    """

    def _setAxes(self):
        """
        Linearizes the lower triangular matrix counting down successive columns
        starting at row=col.
        
        Returns
        -------
        Maplotlib.Figure, Matplotlib.Axes
        """
        figure, axes = self._initializeAxes()
        axisPositions = []
        row = 0
        col = 0
        for index in range(self.numPlotPosition):
            if row >= col:
                ax = plt.subplot2grid(
                      (self.options.numRow, self.options.numCol), (row, col))
                axes.append(ax)
                axisPositions.append((row, col))
            # Update row, col
            if row == self.options.numRow - 1:
                row = 0
                col += 1
            else:
                row += 1
        return figure, axes, axisPositions


########################################
class TimeseriesPlotter(object):
          
    def __init__(self, isPlot=True):
        """
        Parameters
        ---------
        isPlot: boolean
            display the plot
               
        Example
        -------
        plotter = TimeseriesPlotter(timeseries)
        plotter.plotTimeSingle()  # Single variable plots for one timeseries
        """
        self.isPlot = isPlot

    def _mkPlotOptionsMatrix(self, timeseries1, maxCol=None, **kwargs):
        """
        Creates PlotOptions for a dense matrix of plots.
        
        Parameters
        ----------
        timeseries1: NamedTimeseries
        isLowerTriangular: bool
            is a lower triangular matix
        maxCol: int
            maximum number of columns
        kwargs: dict

        Returns
        -------
        PlotOptions
            assigns values to options.numRow, options.numCol
        """
        options = PlotOptions()
        if maxCol is None:
            if COLUMNS in kwargs:
                maxCol = len(kwargs[COLUMNS])
            else:
                maxCol = len(timeseries1.colnames)
        # States
        hasRow, hasCol = self._getOptionState(kwargs, options)
        # Assignments based on state
        if hasRow and hasCol:
            # Have been assigned
            pass
        elif hasRow and (not hasCol):
            options.numCol = int(maxCol/options.numRow)
        elif (not hasRow) and hasCol:
            options.numRow = int(maxCol/options.numCol)
        else:
           options.numRow = 1
           options.numCol = maxCol
        if maxCol > options.numRow*options.numCol:
           options.numRow += 1
        options.initialize(timeseries1, **kwargs)
        #
        return options

    def _getOptionState(self, kwargs, options):
        hasCol = False
        hasRow = False
        if NUM_ROW in kwargs:
            options.numRow = kwargs[NUM_ROW]
            hasRow = True
        if NUM_COL in kwargs:
            options.numCol = kwargs[NUM_COL]
            hasCol = True
        return hasRow, hasCol

    def _mkPlotOptionsLowerTriangular(self,
              timeseries1, pairs, **kwargs):
        """
        Creates PlotOptions for a lower triangular matrix of plots.
        2*len(pairs) - N = N**2
        
        Parameters
        ----------
        pairs: list-tuple-str
        kwargs: dict

        Returns
        -------
        PlotOptions
            assigns values to options.numRow, options.numCol
        """
        size = len(pairs)
        if size == 1:
            matSize = 1
        else:
            # Find the size of the matrix
            matSize = None
            for mm in range(size**3):
                if 2*size - mm <= mm**2:
                    matSize = mm
                    break
            if matSize is None:
                raise RuntimeError("Could not find matrix size.")
        # Assign options
        options = PlotOptions()
        options.numRow = matSize
        options.numCol = matSize
        options.initialize(timeseries1, **kwargs)
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
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
               
        Example
        -------
        plotter = TimeseriesPlotter()
        plotter.plotTimeSingle(timeseries)
        """
        # Adjust rows and columns
        options = self._mkPlotOptionsMatrix(timeseries1, **kwargs)
        numPlot = len(options.columns)  # Number of plots
        if NUM_COL in kwargs.keys():
            options.numRow = int(np.ceil(numPlot/options.numCol))
        else:
            options.numCol = int(np.ceil(numPlot/options.numRow))
        # Create the LayoutManager
        layout = self._mkManager(options, numPlot)
        # Construct the plots
        baseOptions = copy.deepcopy(options)
        for index, variable in enumerate(options.columns):
            options = copy.deepcopy(baseOptions)
            ax = layout.getAxis(index)
            #ax = axes[row, col]
            if options.ylabel is None:
                options.set("ylabel", "concentration")
            options.title = variable
            if not layout.isFirstColumn(index):
                options.ylabel =  ""
                options.set("ylabel", "")
            if not layout.isLastRow(index):
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
        if self.isPlot:
            plt.show()

    def plotTimeMultiple(self, timeseries1, **kwargs):
        """
        Constructs a plot with all columns in a timeseries.
        If there is a second timeseries, then there are 2 plots.

        Parameters
        ---------
        timeseries1: NamedTimeseries
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
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
        numPlot = 2 if TIMESERIES2 in kwargs else 1
        maxCol = numPlot
        options = self._mkPlotOptionsMatrix(timeseries1, maxCol=maxCol, **kwargs)
        # Update rows and columns
        if options.timeseries2 is None:
            options.numRow = 1
            options.numCol = 1
        else:
            if (NUM_ROW in kwargs):
                options.numCol = int(np.ceil(2/options.numRow))
            else:
                options.numRow = int(np.ceil(2/options.numCol))
        # Create the LayoutManager
        layout = self._mkManager(options, numPlot)
        # Construct the plots
        multiPlot(timeseries1, layout.getAxis(0), marker = options.marker1)
        if options.timeseries2 is not None:
            ax = layout.getAxis(numPlot-1)
            multiPlot(options.timeseries2, ax, marker = options.marker2)
        if self.isPlot:
            plt.show()

    def _mkManager(self, options, numPlot, isLowerTriangular=False):
        if numPlot == 1:
            layout = LayoutManagerSingle(options, numPlot)
        elif isLowerTriangular:
            options.titlePosition = (POS_MID, POS_TOP)
            layout = LayoutManagerLowerTriangular(options, numPlot)
        else:
            options.titlePosition = (POS_MID, POS_TOP)
            layout = LayoutManagerMatrix(options, numPlot)
        return layout

    def plotValuePairs(self, timeseries, pairs, 
              isLowerTriangular=False, **kwargs):
        """
        Constructs plots of values of column pairs for a single
        timeseries.

        Parameters
        ---------
        timeseries: NamedTimeseries
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        numPlot = len(pairs)
        if isLowerTriangular:
            options = self._mkPlotOptionsLowerTriangular(
                  timeseries, pairs, **kwargs)
        else:
            options = self._mkPlotOptionsMatrix(timeseries,
                  maxCol=numPlot, **kwargs)
        layout = self._mkManager(options, numPlot,
              isLowerTriangular=isLowerTriangular)
        options.xlabel = ""
        baseOptions = copy.deepcopy(options)
        for index, pair in enumerate(pairs):
            options = copy.deepcopy(baseOptions)
            xVar = pair[0]
            yVar = pair[1]
            ax = layout.getAxis(index)
            if isLowerTriangular:
                if layout.isLastRow(index):
                    options.xlabel = xVar
                else:
                    options.title = ""
                    options.xticklabels = []
                if layout.isFirstColumn(index):
                    options.ylabel = yVar
                else:
                    options.ylabel = ""
                    options.yticklabels = []
            else:
                # Matrix plot
                options.xlabel = ""
                options.ylabel = ""
                options.title = "%s v. %s" % (xVar, yVar)
            ax.scatter(timeseries[xVar], timeseries[yVar], marker='o')
            options.do(ax)
        if self.isPlot:
            plt.show()

    def plotHistograms(self, timeseries, **kwargs):
        """
        Constructs a matrix of histographs for timeseries values.

        Parameters
        ---------
        timeseries: NamedTimeseries
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        if BINS in kwargs.keys():
            bins = kwargs[BINS]
            del kwargs[BINS]
        else:
            bins = None
        options = self._mkPlotOptionsMatrix(timeseries, **kwargs)
        numPlot = len(options.columns)
        layout = self._mkManager(options, numPlot)
        baseOptions = copy.deepcopy(options)
        for index, column in enumerate(options.columns):
            options = copy.deepcopy(baseOptions)
            ax = layout.getAxis(index)
            if layout.isFirstColumn(index):
                options.ylabel = "density"
            if not layout.isFirstColumn(index):
                options.ylabel = ""
            if layout.isLastRow(index):
                options.xlabel = "value"
            else:
                options.xlabel = ""
            # Matrix plot
            options.title = column
            if bins is None:
                ax.hist(timeseries[column], density=True)
            else:
                ax.hist(timeseries[column], bins=bins, density=True)
            options.do(ax)
        if self.isPlot:
            plt.show()


# Update docstrings
_helpers.updatePlotDocstring(TimeseriesPlotter)
