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

from teUtils.named_timeseries import NamedTimeseries, TIME
from teUtils import helpers

import copy
import matplotlib.pyplot as plt
import numpy as np


PLOT = "plot"  # identifies a plotting function
EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)"
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
NUM_ROW = "num_row"
NUM_COL = "num_col"
COLUMNS = "columns"
TIMESERIES2 = "timeseries2"
MARKER1 = "marker1"
MARKER2 = "marker2"
LEGEND = "legend"
TITLE_POSITION = "title_position"
   
 
#########################
class PlotOptions(object):
    """
    Container for plot options. Common method for activating options for an axis.
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
        self.title_position = None  # Relative position in plot (x, y)
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
                columns: List of columns to plot
                figsize: (horizontal width, vertical height)
                legend: Tuple of str for legend
                marker1: Marker for timerseries1
                marker2: Marker for timeseries2
                num_row: rows of plots
                num_col: columns of plots
                timeseries2: second timeseries
                title: plot title
                title_position: relative position in plot (x, y)
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

    def initialize(self, timeseries, num_row=None, num_col=None, **kwargs):
        """
        Initializes information for plotting.

        Parameters
        ---------
        timeseries: NamedTimeseries
            a timeseries to be plotted
        num_row: int
        num_cow: int
        kwargs: dict
        """
        if num_row is not None:
            self.num_row = num_row
        if num_col is not None:
            self.num_col = num_col
        self.setDict(kwargs, excludes=[NUM_ROW, NUM_COL])  # Record the options
        if len(self.columns) == 0:
            self.columns = timeseries.colnames
        if self.figsize is None:
             self.figsize = plt.gca().figure.get_size_inches()

    def do(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        if self.title_position is None:
            ax.set_title(self.title)
        else:
            ax.set_title(self.title, 
                  position=self.title_position,
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

    def __init__(self, options, num_plot):
        """
        Manages allocation of space in subplot and sets up options
        accordingly.

        Parameters
        ---------
        options: PlotOptions
        """
        self.options = options
        self.num_plot = num_plot
        # Number of plot positions in the figure
        self.num_plot_position = self.options.num_row*self.options.num_col
        self.figure, self.axes, self.row_col_list = self._setAxes()

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
        row = index // self.options.num_col
        col = index % self.options.num_col
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
        _, col = self.row_col_list[index]
        return col == 0

    def isFirstRow(self, index):
        row, _ = self.row_col_list[index]
        return row == 0

    def isLastCol(self, index):
        _, col = self.row_col_list[index]
        return col == self.options.num_col - 1

    def isLastRow(self, index):
        row, _ = self.row_col_list[index]
        return row == self.options.num_row - 1


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
        row_col_list = []
        for index in range(self.num_plot_position):
            row, col = self._calcRowColumn(index)
            if index < self.num_plot:
                ax = plt.subplot2grid( (self.options.num_row,
                      self.options.num_col), (row, col))
                row_col_list.append((row, col))
            axes.append(ax)
        return figure, axes, row_col_list


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
        row_col_list = []
        row = 0
        col = 0
        for index in range(self.num_plot_position):
            if row >= col:
                ax = plt.subplot2grid(
                      (self.options.num_row, self.options.num_col), (row, col))
                axes.append(ax)
                row_col_list.append((row, col))
            # Update row, col
            if row == self.options.num_row - 1:
                row = 0
                col += 1
            else:
                row += 1
        return figure, axes, row_col_list


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

    def _mkPlotOptionsMatrix(self, timeseries1, max_col=None, **kwargs):
        """
        Creates PlotOptions for a dense matrix of plots.
        
        Parameters
        ----------
        timeseries1: NamedTimeseries
        is_lower_triangular: bool
            is a lower triangular matix
        max_col: int
            maximum number of columns
        kwargs: dict

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
        has_row, has_col = self._getOptionState(kwargs, options)
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
        options.initialize(timeseries1, **kwargs)
        #
        return options

    def _getOptionState(self, kwargs, options):
        has_col = False
        has_row = False
        if NUM_ROW in kwargs:
            options.num_row = kwargs[NUM_ROW]
            has_row = True
        if NUM_COL in kwargs:
            options.num_col = kwargs[NUM_COL]
            has_col = True
        return has_row, has_col

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
            assigns values to options.num_row, options.num_col
        """
        size = len(pairs)
        # Find the size of the matrix
        for mm in range(size*size):
            if 2*size - mm <= mm**2:
                mat_size = mm
                break
        # Assign options
        options = PlotOptions()
        options.num_row = mat_size
        options.num_col = mat_size
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
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
               
        Example
        -------
        plotter = TimeseriesPlotter()
        plotter.plotTimeSingle(timeseries)
        """
        # Adjust rows and columns
        options = self._mkPlotOptionsMatrix(timeseries1, **kwargs)
        num_plot = len(options.columns)  # Number of plots
        if NUM_COL in kwargs.keys():
            options.num_row = int(np.ceil(num_plot/options.num_col))
        else:
            options.num_col = int(np.ceil(num_plot/options.num_row))
        # Create the LayoutManager
        layout = self._mkManager(options, num_plot)
        # Construct the plots
        base_options = copy.deepcopy(options)
        for index, variable in enumerate(options.columns):
            options = copy.deepcopy(base_options)
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
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
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
        num_plot = 2 if TIMESERIES2 in kwargs else 1
        max_col = num_plot
        options = self._mkPlotOptionsMatrix(timeseries1, max_col=max_col, **kwargs)
        # Update rows and columns
        if options.timeseries2 is None:
            options.num_row = 1
            options.num_col = 1
        else:
            if (NUM_ROW in kwargs):
                options.num_col = int(np.ceil(2/options.num_row))
            else:
                options.num_row = int(np.ceil(2/options.num_col))
        # Create the LayoutManager
        layout = self._mkManager(options, num_plot)
        # Construct the plots
        multiPlot(timeseries1, layout.getAxis(0), marker = options.marker1)
        if options.timeseries2 is not None:
            ax = layout.getAxis(num_plot-1)
            multiPlot(options.timeseries2, ax, marker = options.marker2)
        if self.is_plot:
            plt.show()

    def _mkManager(self, options, num_plot, is_lower_triangular=False):
        if num_plot == 1:
            layout = LayoutManagerSingle(options, num_plot)
        elif is_lower_triangular:
            options.title_position = (POS_MID, POS_TOP)
            layout = LayoutManagerLowerTriangular(options, num_plot)
        else:
            options.title_position = (POS_MID, POS_TOP)
            layout = LayoutManagerMatrix(options, num_plot)
        return layout

    def plotValuePairs(self, timeseries, pairs, 
              is_lower_triangular=False, **kwargs):
        """
        Constructs plots of values of column pairs for a single
        timeseries.

        Parameters
        ---------
        timeseries: NamedTimeseries
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
        """
        num_plot = len(pairs)
        if is_lower_triangular:
            options = self._mkPlotOptionsLowerTriangular(
                  timeseries, pairs, **kwargs)
        else:
            options = self._mkPlotOptionsMatrix(timeseries, max_col=num_plot, **kwargs)
        layout = self._mkManager(options, num_plot,
              is_lower_triangular==is_lower_triangular)
        options.xlabel = ""
        base_options = copy.deepcopy(options)
        for index, pair in enumerate(pairs):
            options = copy.deepcopy(base_options)
            x_var = pair[0]
            y_var = pair[1]
            ax = layout.getAxis(index)
            if is_lower_triangular:
                if layout.isLastRow(index):
                    options.xlabel = x_var
                else:
                    options.title = ""
                    options.xticklabels = []
                if layout.isFirstColumn(index):
                    options.ylabel = y_var
                else:
                    options.ylabel = ""
                    options.yticklabels = []
            else:
                # Matrix plot
                options.xlabel = ""
                options.ylabel = ""
                options.title = "%s v. %s" % (x_var, y_var)
            ax.scatter(timeseries[x_var], timeseries[y_var], marker='o')
            options.do(ax)
        if self.is_plot:
            plt.show()

    def plotHistograms(self, timeseries, **kwargs):
        """
        Constructs a matrix of histographs for timeseries values.

        Parameters
        ---------
        timeseries: NamedTimeseries
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
        """
        options = self._mkPlotOptionsMatrix(timeseries, **kwargs)
        num_plot = len(options.columns)
        layout = self._mkManager(options, num_plot)
        base_options = copy.deepcopy(options)
        for index, column in enumerate(options.columns):
            options = copy.deepcopy(base_options)
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
            ax.hist(timeseries[column], density=True)
            options.do(ax)
        if self.is_plot:
            plt.show()


# Update docstrings
helpers.updatePlotDocstring(TimeseriesPlotter)
