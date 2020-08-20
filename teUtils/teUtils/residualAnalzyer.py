# -*- coding: utf-8 -*-
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
from teUtils import timeseriesPlotter as tp
from teUtils import _helpers

import numpy as np
import pandas as pd
import typing


class ResidualAnalyzer(object):

    def __init__(self, observedTS:NamedTimeseries, fittedTS:NamedTimeseries):
        self.observedTS = observedTS
        self.fittedTS = fittedTS
        self.residualsTS = self.observedTS.copy()
        self.residualsTS -= self.fittedTS
        ### Plotter
        self._plotter = tp.TimeseriesPlotter()

    def plotResidualsOverTime(self,
          **kwargs:dict):
        """
        Plots residuals of a fit over time.
    
        Parameters
        ----------
        kwargs: Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        options = po.PlotOptions()
        if not po.MARKER1 in kwargs:
            kwargs[po.MARKER1] = "o"
        self._plotter.plotTimeSingle(self.residualsTS, **kwargs)

    def plotFittedndObservedOverTime(self, isMultiple:bool=False,
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
        if isMultiple:
            self._plotter.plotTimeMultiple(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)
        else:
            self._addKeyword(kwargs, po.LEGEND, ["fitted", "observed"])
            self._plotter.plotTimeSingle(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)

    def plotResidualsHistogram(self, parameters:typing.List[str]=None,
          **kwargs:dict):
        """
        Plots histographs of parameter values from a bootstrap.
        
        Parameters
        ----------
        parameters: List of parameters to do pairwise plots
        kwargs: 
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        if self.bootstrapResult is None:
            raise ValueError("Must run bootstrap before plotting parameter estimates.")
        ts = self._mkParameterDF(parameters=parameters)
        self._plotter.plotHistograms(ts, **kwargs)

    def _addKeyword(self, kwargs:dict, key:str, value:object):
        if not key in kwargs:
            kwargs[key] = value
        

# Update the docstrings 
_helpers.updatePlotDocstring(ModelFitter)
