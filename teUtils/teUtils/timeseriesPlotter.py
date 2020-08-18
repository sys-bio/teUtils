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

from teUtils import _plotOptions as po
from teUtils import _layoutManager as lm
from teUtils.namedTimeseries import NamedTimeseries, TIME
from teUtils import _helpers
from teUtils._statementManager import StatementManager

import copy
import matplotlib.pyplot as plt
import numpy as np


EXPAND_KEYPHRASE = "Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)"
LABEL1 = "1"
LABEL2 = "2"
COLORS = ['r', 'g', 'b', 'c', 'pink', 'grey']
NULL_STR = ""
# Ensure lots of colors
COLORS.extend(COLORS)
COLORS.extend(COLORS)
# Title positions
POS_MID = 0.5
POS_TOP = 0.9


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
        options = po.PlotOptions()
        if maxCol is None:
            if po.COLUMNS in kwargs:
                maxCol = len(kwargs[po.COLUMNS])
            else:
                maxCol = len(timeseries1.colnames)
        # States
        hasRow, hasCol = self._getOptionValueState(kwargs, options)
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

    def _getOptionValueState(self, kwargs, options):
        hasCol = False
        hasRow = False
        if po.NUM_ROW in kwargs:
            options.numRow = kwargs[po.NUM_ROW]
            hasRow = True
        if po.NUM_COL in kwargs:
            options.numCol = kwargs[po.NUM_COL]
            hasCol = True
        return hasRow, hasCol

    def _mkPlotOptionsLowerTriangular(self, timeseries1,
         numPlot,  **kwargs):
        """
        Creates PlotOptions for a lower triangular matrix of plots.
        2*len(pairs) - N = N**2
        
        Parameters
        ----------
        timeseries1: NamedTimeseries
        numPlot: int
        kwargs: dict

        Returns
        -------
        PlotOptions
            assigns values to options.numRow, options.numCol
        """
        options = po.PlotOptions()
        if numPlot == 1:
            options.numRow = 1
            options.numCol = 1
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
        options = self._mkPlotOptionsMatrix(timeseries1, **kwargs)
        def doPlot(ax, timeseries, variable, lineNum):
            def getOptionValue(options, option_str):
                return eval("options.%s%d" % (option_str, lineNum))
            #
            marker = options.__getattribute__("marker%d" % lineNum)
            if marker is None:
                manager = StatementManager(ax.plot)
            else:
                manager = StatementManager(ax.scatter)
            #
            manager.addPosarg(timeseries[TIME])
            manager.addPosarg(timeseries[variable])
            manager.addKwargs(color=getOptionValue(options, "color"))
            #
            marker_value = getOptionValue(options, "marker")
            if marker_value is not None:
                manager.addKwargs(marker=marker)
            #
            markersize_value = getOptionValue(options, "markersize")
            if markersize_value is not None:
                manager.addKwargs(s=markersize_value)
            return manager.execute()
        #
        # Adjust rows and columns
        numPlot = len(options.columns)  # Number of plots
        if po.NUM_COL in kwargs.keys():
            options.numRow = int(np.ceil(numPlot/options.numCol))
        else:
            options.numCol = int(np.ceil(numPlot/options.numRow))
        # Create the LayoutManager
        layout = self._mkManager(options, numPlot)
        # Construct the plots
        baseOptions = copy.deepcopy(options)
        for index, variable in enumerate(options.columns):
            ax = layout.getAxis(index)
            options = copy.deepcopy(baseOptions)
            #ax = axes[row, col]
            options.set(po.YLABEL, "concentration")
            options.title = variable
            if not layout.isFirstColumn(index):
                options.ylabel =  NULL_STR
                options.set(po.YLABEL, "", isOverride=True)
            if not layout.isLastRow(index):
                options.set(po.XLABEL, "", isOverride=True)
            # Construct the plot
            doPlot(ax, timeseries1, variable, 1)
            if options.timeseries2 is not None:
                doPlot(ax, options.timeseries2, variable, 2)
                options.set(po.LEGEND, [LABEL1, LABEL2])
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
        def multiPlot(options, timeseries, ax, marker=None):
            if marker is None:
                for idx, col in enumerate(timeseries.colnames):
                    ax.plot(timeseries[TIME], timeseries[col], color=COLORS[idx])
            else:
                for idx, col in enumerate(timeseries.colnames):
                    if options.markersize1 is None:
                        ax.scatter(timeseries[TIME], timeseries[col], color=COLORS[idx],
                              marker=marker)
                    else:
                        ax.scatter(timeseries[TIME], timeseries[col], color=COLORS[idx],
                              marker=marker, s=options.markersize1)
            options.legend = timeseries.colnames
            options.do(ax)
        #
        numPlot = 2 if po.TIMESERIES2 in kwargs else 1
        maxCol = numPlot
        options = self._mkPlotOptionsMatrix(timeseries1, maxCol=maxCol, **kwargs)
        # Update rows and columns
        if options.timeseries2 is None:
            options.numRow = 1
            options.numCol = 1
        else:
            if (po.NUM_ROW in kwargs):
                options.numCol = int(np.ceil(2/options.numRow))
            else:
                options.numRow = int(np.ceil(2/options.numCol))
        # Create the LayoutManager
        layout = self._mkManager(options, numPlot)
        # Construct the plots
        multiPlot(options, timeseries1, layout.getAxis(0), marker = options.marker1)
        if options.timeseries2 is not None:
            ax = layout.getAxis(numPlot-1)
            multiPlot(options, options.timeseries2, ax, marker=options.marker2)
        if self.isPlot:
            plt.show()

    def _mkManager(self, options, numPlot, 
          isLowerTriangular=False):
        if numPlot == 1:
            layout = lm.LayoutManagerSingle(
                   options, numPlot)
        elif isLowerTriangular:
            options.set(po.TITLE_POSITION, 
                (POS_MID, POS_TOP))
            layout = lm.LayoutManagerLowerTriangular(
                   options, numPlot)
        else:
            options.set(po.TITLE_POSITION, 
                (POS_MID, POS_TOP))
            layout = lm.LayoutManagerMatrix(options,
                  numPlot)
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
                  timeseries, numPlot, **kwargs)
        else:
            options = self._mkPlotOptionsMatrix(timeseries,
                  maxCol=numPlot, **kwargs)
        layout = self._mkManager(options, numPlot,
              isLowerTriangular=isLowerTriangular)
        options.xlabel = NULL_STR
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
                    options.title = NULL_STR
                    options.xticklabels = []
                if layout.isFirstColumn(index):
                    options.ylabel = yVar
                else:
                    options.ylabel = NULL_STR
                    options.yticklabels = []
            else:
                # Matrix plot
                options.xlabel = NULL_STR
                options.ylabel = NULL_STR
                options.title = "%s v. %s" % (xVar, yVar)
            if options.markersize1 is None:
                ax.scatter(timeseries[xVar], timeseries[yVar], marker='o')
            else:
                ax.scatter(timeseries[xVar], timeseries[yVar], marker='o',
                      s=options.markersize1)
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
        if po.BINS in kwargs.keys():
            bins = kwargs[po.BINS]
            del kwargs[po.BINS]
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
                options.ylabel = NULL_STR
            if layout.isLastRow(index):
                options.xlabel = "value"
            else:
                options.xlabel = NULL_STR
            # Matrix plot
            options.title = column
            manager = StatementManager(ax.hist)
            manager.addPosarg(timeseries[column])
            manager.addKwargs(density=True)
            if options.bins is not None:
                manager.addKwargs(bins=options.bins)
            manager.execute()
            options.do(ax)
        if self.isPlot:
            plt.show()

    def plotCompare(self, 
           ts1: NamedTimeseries, 
           ts2: NamedTimeseries,
           **kwargs: dict):
        """
        Plots columns against each other.
        
        Parameters
        ----------
        kwargs: 
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        mergedTS = ts1.concatenateColumns(ts2)
        pairs = [(c, "%s_" % c) for c in ts1.colnames]
        #
        self.plotValuePairs(mergedTS, pairs, **kwargs)


# Update docstrings
_helpers.updatePlotDocstring(TimeseriesPlotter)
