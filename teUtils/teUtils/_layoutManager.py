# -*- coding: utf-8 -*-
"""
Created on Aug 2020

@author: joseph-hellerstein

Manages the layout of a matrix of plots.
    LayoutManager - abstract class 
    LayoutManagerSingle - single plot
    LayoutManagerMatrix - dense matrix of plots
    LayoutManagerLowerTriangular - plots in lower triangle
"""

import matplotlib.pyplot as plt
import numpy as np


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
        if (self.options.numRow is not None)   \
              and (self.options.numCol is not None):
            self.numPlotPosition = self.options.numRow*self.options.numCol
        else:
            self.numPlotPosition = None
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


########################################
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


########################################
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

    def __init__(self, options, numPlot):
        """
        Manages allocation of space in subplot and sets up options
        accordingly.

        Parameters
        ---------
        options: PlotOptions
        """
        self.options = options
        # Adjust rows and columns for the number of plots
        # by creating a square matrix with the right number of
        # plot positions to accommodate the number of plots.
        matSize = None
        for mm in range(numPlot**3):
            if 2*numPlot - mm <= mm**2:
                matSize = mm
                break
        if matSize is None:
            raise RuntimeError("Could not find matrix size.")
        # Number of plot positions in the figure
        self.options.numRow = matSize
        self.options.numCol = matSize
        self.numPlotPosition = self.options.numRow*self.options.numCol
        self.figure, self.axes, self.axisPositions = self._setAxes()

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
