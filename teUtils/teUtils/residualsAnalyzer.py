"""
 Created on Aug 20, 2020

@author: joseph-hellerstein

Codes that provide various analyses of residuals.

There are 3 types of timeseries: observed, fitted, and residuals
(observed - fitted). 

Plots are organized by the timeseries and the characteristic analyzed. These
characteristics are: (a) over time, (b) histogram.
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME, mkNamedTimeseries
import teUtils._plotOptions as po
from teUtils import modelFitter as mf
from teUtils import timeseriesPlotter as tp
from teUtils import _helpers

import numpy as np
import pandas as pd
import typing

PLOT = "plot"


class ResidualsAnalyzer(object):

    def __init__(self, observedTS:NamedTimeseries, fittedTS:NamedTimeseries,
              isPlot:bool=True):
        self.observedTS = observedTS
        self.fittedTS = fittedTS
        self.residualsTS = self.observedTS.copy()
        cols = self.residualsTS.colnames
        self.residualsTS[cols] -= self.fittedTS[cols]
        ### Plotter
        self._plotter = tp.TimeseriesPlotter(isPlot=isPlot)

    def _addKeyword(self, kwargs:dict, key:str, value:object):
        if not key in kwargs:
            kwargs[key] = value

    def plotAll(self, **kwargs:dict):
        """
        Does all residual plots.
    
        Parameters
        ----------
        kwargs: Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        for name in dir(self):
            if name == "plotAll":
                continue
            if name[0:4] == PLOT:
                statement = "self.%s(**kwargs)" % name
                exec(statement)

    def plotResidualsOverTime(self, **kwargs:dict):
        """
        Plots residuals of a fit over time.
    
        Parameters
        ----------
        kwargs: Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._addKeyword(kwargs, po.MARKER1, "o")
        self._addKeyword(kwargs, po.SUPTITLE, "Residuals Over Time")
        self._plotter.plotTimeSingle(self.residualsTS, **kwargs)

    def plotFittedObservedOverTime(self, isMultiple:bool=False,
          **kwargs:dict):
        """
        Plots the fit with observed data over time.
    
        Parameters
        ----------
        isMultiple: plots all variables on a single plot
        kwargs: dict. Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._addKeyword(kwargs, po.MARKER2, "o")
        self._addKeyword(kwargs, po.SUPTITLE, "Residuals And Fitted Over Time")
        if isMultiple:
            self._plotter.plotTimeMultiple(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)
        else:
            self._addKeyword(kwargs, po.LEGEND, ["fitted", "observed"])
            self._plotter.plotTimeSingle(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)

    def plotResidualsHistograms(self, **kwargs:dict):
        """
        Plots histographs of parameter values from a bootstrap.
        
        Parameters
        ----------
        parameters: List of parameters to do pairwise plots
        kwargs: 
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._addKeyword(kwargs, po.SUPTITLE, "Residual Distributions")
        self._plotter.plotHistograms(self.residualsTS, **kwargs)

    def plotResidualAutoCorrelations(self, **kwargs:dict):
        """
        Plots auto correlations between residuals of columns.
        
        Parameters
        ----------
        parameters: List of parameters to do pairwise plots
        kwargs: 
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._addKeyword(kwargs, po.SUPTITLE, "Residual Autocorrelations")
        self._plotter.plotAutoCorrelations(self.residualsTS, **kwargs)

    def plotResidualCrossCorrelations(self, **kwargs:dict):
        """
        Plots cross correlations between residuals of columns.
        
        Parameters
        ----------
        parameters: List of parameters to do pairwise plots
        kwargs: 
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._addKeyword(kwargs, po.SUPTITLE, "Residual Cross Correlations")
        self._plotter.plotCrossCorrelations(self.residualsTS, **kwargs)
        

# Update the docstrings 
_helpers.updatePlotDocstring(ResidualsAnalyzer)
