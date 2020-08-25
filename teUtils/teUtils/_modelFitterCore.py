# -*- coding: utf-8 -*-
"""
 Created on August 18, 2020

@author: joseph-hellerstein

Core logic of model fitter. Does not include plots.
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME, mkNamedTimeseries
import teUtils.timeseriesPlotter as tp
from teUtils import namedTimeseries
from teUtils import _helpers

import collections
import lmfit
from multiprocessing import Pool
import numpy as np
import pandas as pd
import random
import roadrunner
import tellurium as te
import typing

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10
#  Minimizer methods
METHOD_BOTH = "both"
METHOD_DIFFERENTIAL_EVOLUTION = "differential_evolution"
METHOD_LEASTSQR = "leastsqr"
MAX_CHISQ_MULT = 5
PERCENTILES = [2.5, 97.55]  # Percentile for confidence limits
INDENTATION = "  "
NULL_STR = ""
IS_REPORT = False


##############################
class ModelFitterCore(object):

    def __init__(self, modelSpecification, observed, parametersToFit,
                 selectedColumns=None, method=METHOD_BOTH,
                 parameterLowerBound=PARAMETER_LOWER_BOUND,
                 parameterUpperBound=PARAMETER_UPPER_BOUND,
                 isPlot=True
                 ):
        """
        Parameters
        ---------
        modelSpecification: ExtendedRoadRunner/str
            roadrunner model or antimony model
        observed: NamedTimeseries/str
            str: path to CSV file
        parametersToFit: list-str/None
            parameters in the model that you want to fit
            if None, no parameters are fit
        selectedColumns: list-str
            species names you wish use to fit the model
            default: all columns in observed
        parameterLowerBound: float
            lower bound for the fitting parameters
        parameterUpperBound: float
            upper bound for the fitting parameters
        method: str
            method used for minimization

        Usage
        -----
        f = ModelFitter(roadrunnerModel, "observed.csv", ['k1', 'k2'])
        """
        self.modelSpecification = modelSpecification
        self.parametersToFit = parametersToFit
        self.LowerBound = parameterLowerBound
        self.UpperBound = parameterUpperBound
        self.observedTS = mkNamedTimeseries(observed)
        if selectedColumns is None:
            selectedColumns = self.observedTS.colnames
        self.selectedColumns = selectedColumns
        self._method = method
        self._isPlot = isPlot
        self._plotter = tp.TimeseriesPlotter(isPlot=self._isPlot)
        # The following are calculated during fitting
        self.roadrunnerModel = None
        self.minimizer = None  # lmfit.minimizer
        self.minimizerResult = None  # Results of minimization
        self.params = None  # params property in lmfit.minimizer
        self.fittedTS = self.observedTS.copy()  # Initialization of columns
        self.residualsTS = None  # Residuals for selectedColumns
        self.bootstrapResult = None  # Result from bootstrapping

    def copy(self):
        """
        Creates a copy of the model fitter.
        """
        if not isinstance(self.modelSpecification, str):
            modelSpecification = self.modelSpecification.getAntimony()
        else:
            modelSpecification = self.modelSpecification
        newModelFitter = self.__class__(
              modelSpecification,
              self.observedTS,
              self.parametersToFit,
              selectedColumns=self.selectedColumns,
              method=self._method,
              parameterLowerBound=self.LowerBound,
              parameterUpperBound=self.UpperBound,
              isPlot=self._isPlot)
        return newModelFitter

    def _initializeRoadrunnerModel(self):
        """
        Sets self.roadrunnerModel.
        """
        if isinstance(self.modelSpecification,
              te.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            self.roadrunnerModel = self.modelSpecification
        elif isinstance(self.modelSpecification, str):
            self.roadrunnerModel = te.loada(self.modelSpecification)
        else:
            msg = 'Invalid model.'
            msg = msg + "\nA model must either be a Roadrunner model "
            msg = msg + "an Antimony model."
            raise ValueError(msg)

    def _simulate(self, params=None):
        """
        Runs a simulation. Updates self.fittedTS.

        Parameters
        ----------
        params: lmfit.Parameters

        Instance Variables Updated
        --------------------------
        self.fittedTS
        """
        self._setupModel(params=params)
        self.fittedTS[self.fittedTS.allColnames] = self.roadrunnerModel.simulate(
              self.observedTS.start, self.observedTS.end, len(self.observedTS))

    def _residuals(self, params:lmfit.Parameters=None)->np.ndarray:
        """
        Compute the residuals between objective and experimental data

        Parameters
        ----------
        params: Parameters to use for residual calculation.

        Instance Variables Updated
        --------------------------
        self.residualsTS

        Returns
        -------
        1-d ndarray of residuals
        """
        self._simulate(params=params)
        cols = self.selectedColumns
        if self.residualsTS is None:
            self.residualsTS = self.observedTS.subsetColumns(cols)
        self.residualsTS[cols] = self.observedTS[cols] - self.fittedTS[cols]
        return self.residualsTS.flatten()

    def fitModel(self, params:lmfit.Parameters=None):
        """
        Fits the model by adjusting values of parameters based on
        differences between simulated and provided values of
        floating species.

        Parameters
        ----------
        params: starting values of parameters

        Example
        -------
        f.fitModel()
        """
        self._initializeRoadrunnerModel()
        if self.parametersToFit is None:
            # Compute fit and residuals for base model
            self.params = None
        else:
            if params is None:
                params = self._initializeParams()
            # Fit the model to the data
            # Use two algorithms:
            #   Global differential evolution to get us close to minimum
            #   A local Levenberg-Marquardt to getsus to the minimum
            if self._method in [METHOD_BOTH, METHOD_DIFFERENTIAL_EVOLUTION]:
                minimizer = lmfit.Minimizer(self._residuals, params)
                self.minimizerResult = minimizer.minimize(
                      method=METHOD_DIFFERENTIAL_EVOLUTION)
            if self._method in [METHOD_BOTH, METHOD_LEASTSQR]:
                minimizer = lmfit.Minimizer(self._residuals, params)
                self.minimizerResult = minimizer.minimize(method='leastsqr')
            self.params = self.minimizerResult.params
            self.minimizer = minimizer
            if not self.minimizer.success:
                msg = "*** Minimizer failed for this model and data."
                raise ValueError(msg)
        # Ensure that residualsTS and fittedTS match the parameters
        self._residuals(params=self.params)

    def getFittedModel(self):
        """
        Provides the roadrunner model with fitted parameters

        Returns
        -------
        ExtendedRoadrunner
        """
        self._checkFit()
        self.roadrunnerModel.reset()
        self._setupModel(params=self.params)
        return self.roadrunnerModel

    def _setupModel(self, params=None):
        """
        Sets up the model for use based on the parameter parameters

        Parameters
        ----------
        params: lmfit.Parameters

        """
        self.roadrunnerModel.reset()
        if params is not None:
            pp = params.valuesdict()
            for parameter in self.parametersToFit:
               self.roadrunnerModel.model[parameter] = pp[parameter]

    def _initializeParams(self):
        params = lmfit.Parameters()
        value = np.mean([self.LowerBound, self.UpperBound])
        for parameter in self.parametersToFit:
           params.add(parameter, value=value,
                 min=self.LowerBound, max=self.UpperBound)
        return params

    def _checkFit(self):
        if self.params is None:
            raise ValueError("Must use fitModel before using this method.")
