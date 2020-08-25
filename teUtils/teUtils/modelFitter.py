# -*- coding: utf-8 -*-
"""
 Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein

A ModelFitter estimates parameters of a roadrunner model by using observed values
of floating species concentrations to construct fitted values with 
small residuals (the difference between fitted and observed values).

The user can access:
    estimated parameter values
    roadrunner model with estimated parameter values
    observed values of floating species concentrations
    fitted values of floating species concentrations
    residuals of observed - fitted

Usage
-----
   # The constructor takes either a roadrunner or antimony model
   f = ModelFitter(model, "mydata.txt",
         parametersToFit=["k1", "k2"])
   # Fit the model parameters and view parameters
   f.fitModel()
   print(f.getFittedParamters())
   # Print observed, fitted and residual values
   print(f.observedTS)
   print(f.fittedTS)
   print(f.residualsTS)

The code is arranged as a hierarchy of classes that use the previous class:
    _modelFitterCore.ModelFitterCore - model fitting
    _modelFitterBootstrap.ModelFitterBootstrap - bootstrapping
    _modelFitterReport.ModelFitterReport - reports on results of fitting and bootstrapping
    modelFitter - plot routines
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME, mkNamedTimeseries
import teUtils._plotOptions as po
from teUtils import timeseriesPlotter as tp
from teUtils import _helpers
from teUtils._modelFitterReport import ModelFitterReport
from teUtils.residualsAnalyzer import ResidualsAnalyzer

from docstring_expander.expander import Expander
import numpy as np
import pandas as pd
import typing


class ModelFitter(ModelFitterReport):

    @Expander(po.KWARGS, po.BASE_OPTIONS, indent=8)
    def plotResidualsAll(self, **kwargs):
        """
        Plots a set of residual plots
    
        Parameters
        ----------
        #@expand
        """
        self._checkFit()
        analyzer = ResidualsAnalyzer(self.observedTS, self.fittedTS,
              isPlot=self._isPlot)
        analyzer.plotAll(**kwargs)

    @Expander(po.KWARGS, po.BASE_OPTIONS, indent=8)
    def plotResiduals(self, **kwargs):
        """
        Plots residuals of a fit over time.
    
        Parameters
        ----------
        #@expand
        """
        self._checkFit()
        analyzer = ResidualsAnalyzer(self.observedTS, self.fittedTS,
              isPlot=self._isPlot)
        analyzer.plotResidualsOverTime(**kwargs)

    @Expander(po.KWARGS, po.BASE_OPTIONS, indent=8)
    def plotFitAll(self, isMultiple=False, **kwargs):
        """
        Plots the fit with observed data over time.
    
        Parameters
        ----------
        isMultiple: bool
            plots all variables on a single plot
        #@expand
        """
        self._checkFit()
        analyzer = ResidualsAnalyzer(self.observedTS, self.fittedTS,
              isPlot=self._isPlot)
        analyzer.plotFittedObservedOverTime(**kwargs)

    def _addKeyword(self, kwargs, key, value):
        if not key in kwargs:
            kwargs[key] = value

    def _mkParameterDF(self, parameters=None):
        df = pd.DataFrame(self.bootstrapResult.parameterDct)
        if parameters is not None:
            df = df[parameters]
        df.index.name = TIME
        return NamedTimeseries(dataframe=df)

    @Expander(po.KWARGS, po.BASE_OPTIONS, indent=8)
    def plotParameterEstimatePairs(self, parameters=None, **kwargs):
        """
        Does pairwise plots of parameter estimates.
        
        Parameters
        ----------
        parameters: list-str
            List of parameters to do pairwise plots
        #@expand
        """
        if self.bootstrapResult is None:
            raise ValueError("Must run bootstrap before plotting parameter estimates.")
        ts = self._mkParameterDF(parameters=parameters)
        # Construct pairs
        names = list(self.bootstrapResult.parameterDct.keys())
        pairs = []
        compares = list(names)
        for name in names:
            compares.remove(name)
            pairs.extend([(name, c) for c in compares])
        #
        self._plotter.plotValuePairs(ts, pairs,
              isLowerTriangular=True, **kwargs)

    @Expander(po.KWARGS, po.BASE_OPTIONS, includes=[po.BINS], indent=8)
    def plotParameterHistograms(self, parameters=None, **kwargs):
        """
        Plots histographs of parameter values from a bootstrap.
        
        Parameters
        ----------
        parameters: list-str
            List of parameters to do pairwise plots
        #@expand
        """
        self._checkBootstrap()
        ts = self._mkParameterDF(parameters=parameters)
        self._plotter.plotHistograms(ts, **kwargs)
