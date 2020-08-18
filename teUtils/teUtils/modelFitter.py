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
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME, mkNamedTimeseries
from teUtils import namedTimeseries
import teUtils._plotOptions as po
from teUtils import timeseriesPlotter as tp
from teUtils import _helpers

import copy
import lmfit; 
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


class BootstrapResult():

    """Result from bootstrap"""
    def __init__(self, numIteration: int,
          parameterDct: typing.Dict[str, np.ndarray]):
        """
        Parameters
        ----------
        numIteration: number of iterations for solution
        parameterDct: dict
            key: parameter name
            value: list of values
        """
        self.numIteration = numIteration
        # population of parameter values
        self.parameterDct = dict(parameterDct)
        # list of parameters
        self.parameters = list(self.parameterDct.keys())
        # Number of simulations
        self.numSimulation =  \
              len(self.parameterDct[self.parameters[0]])
        # means of parameter values
        self.meanDct = {p: np.mean(parameterDct[p])
              for p in self.parameters}
        # standard deviation of parameter values
        self.stdDct = {p: np.std(parameterDct[p])
              for p in self.parameters}
        # 95% Confidence limits for parameter values
        self.percentileDct = {
              p: np.percentile(self.parameterDct[p],
              PERCENTILES) for p in self.parameterDct}

    def __str__(self) -> str:
        """
        Bootstrap report.       
        """
        class _Report():

            def __init__(self):
                self.reportStr= NULL_STR
                self.numIndent = 0

            def indent(self, num: int):
                self.numIndent += num

            def _getIndentStr(self):
                return NULL_STR.join(np.repeat(
                      INDENTATION, self.numIndent))
            
            def addHeader(self, title:str):
                indentStr = self._getIndentStr()
                self.reportStr+= "\n%s%s" % (indentStr, title)

            def addTerm(self, name:str, value:object):
                indentStr = self._getIndentStr()
                self.reportStr+= "\n%s%s: %s" %  \
                      (indentStr, name, str(value))

            def get(self)->str:
                return self.reportStr
        #
        report = _Report()
        report.addHeader("Bootstrap Report.")
        report.addTerm("Total iterations", self.numIteration)
        report.addTerm("Total simulation", self.numSimulation)
        for par in self.parameters:
            report.addHeader(par)
            report.indent(1)
            report.addTerm("mean", self.meanDct[par])
            report.addTerm("std", self.stdDct[par])
            report.addTerm("%s Percentiles" % str(PERCENTILES),
                  self.percentileDct[par])
            report.indent(-1)
        return report.get()


##############################
class ModelFitter(object):
          
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
        self.observedTS = mkNamedTimeseries(observed)
        self.parametersToFit = parametersToFit
        self.LowerBound = parameterLowerBound
        self.UpperBound = parameterUpperBound
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
                self.minimizerResult = minimizer.minimize(method='differential_evolution')
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

    def getBootstrapReport(self):
        """
        Prints a report of the bootstrap results.
        ----------
        
        Example
        -------
        f.getBootstrapReport()
        """
        if self.bootstrapResult is None:
            print("Must run bootstrap before requesting report.")
        print(self.bootstrapResult)

    def getFittedParameters(self):
        """
        Returns a list of values for fitted
              
        Example
        -------
              f.getFittedParameters()
        """
        self._checkFit()
        if self.bootstrapResult is None:
            return [self.params[p].value for p in self.parametersToFit]
        else:
            return self.bootstrapResult.meanDct.values()

    def getFittedParameterStds(self):
        """
        Returns the standard deviations for fitted values.
              
        Example
        -------
              f.getFittedParameterStds()
        """
        self._checkFit()
        if self.bootstrapResult is None:
            raise ValueError("Must use bootstrap first.")
        return list(self.bootstrapResult.stdDct.values())

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

    def calcResidualsStd(self):
        return np.std(self.residualsTS[
              self.selectedColumns])

    @staticmethod
    def calcObservedTS(fitter,
          **kwargs: dict) -> NamedTimeseries:
        """
        Calculates synthetic observations.
        """
        fitter._checkFit()
        numRow = len(fitter.observedTS)
        newObservedTS = fitter.observedTS.copy()
        for column in fitter.selectedColumns:
            newObservedTS[column] = np.random.choice(
                  fitter.residualsTS[column],
                  numRow, replace=True) +  \
                  fitter.fittedTS[column]
        return newObservedTS

    @staticmethod
    def calcObservedTSNormal(fitter, std:float=0.1)  \
          -> NamedTimeseries:
        """
        Calculates synthetic observations.
        """
        fitter._checkFit()
        numRow = len(fitter.observedTS)
        newObservedTS = fitter.observedTS.copy()
        for column in fitter.selectedColumns:
            randoms = np.random.normal(0, std, numRow)
            newObservedTS[column] += randoms
        return newObservedTS

    def bootstrap(self, numIteration:int=10, 
          reportInterval:int=-1,
          calcObservedFunc=None, **kwargs: dict):
        """
        Constructs a bootstrap estimate of parameter values.
    
        Parameters
        ----------
        numIteration: number of bootstrap iterations
        reportInterval: number of iterations between progress reports
        calcObservedFunc: Function
            Function used to calculate new observed values
        kwargs: arguments passed to calcObservedFunct
              
        Example
        -------
            f.bootstrap()
            f.getFittedParameters()  # Mean values
            f.getFittedParameterStds()  # Standard deviations of values
        """


        ITERATION_MULTIPLIER = 10  # Determines maximum iterations
        if calcObservedFunc is None:
            calcObservedFunc = ModelFitter.calcObservedTS
        self._checkFit()
        base_redchi = self.minimizerResult.redchi
        parameterDct = {p: [] for p in self.parametersToFit}
        numSuccessIteration = 0
        newObservedTS = calcObservedFunc(self, **kwargs)
        lastReport = 0
        baseChisq = self.minimizerResult.redchi
        newFitter = ModelFitter(self.roadrunnerModel,
              newObservedTS,  
              self.parametersToFit,
              selectedColumns=self.selectedColumns,
              method=METHOD_LEASTSQR,
              parameterLowerBound=self.LowerBound,
              parameterUpperBound=self.UpperBound,
              isPlot=self._isPlot)
        for iteration in range(numIteration*ITERATION_MULTIPLIER):
            if (reportInterval > 0)  \
                      and (numSuccessIteration != lastReport):
                if numSuccessIteration % reportInterval == 0:
                    print("bootstrap completed %d iterations"
                          % numSuccessIteration)
                    lastReport = numSuccessIteration
            if numSuccessIteration >= numIteration:
                # Performed the iterations
                break
            try:
                newFitter.fitModel(params=self.params)
            except ValueError:
                # Problem with the fit. Don't numSuccessIteration it.
                if IS_REPORT:
                    print("Fit failed")
                continue
            if newFitter.minimizerResult.redchi > MAX_CHISQ_MULT*baseChisq:
                if IS_REPORT:
                    print("Fit has high chisq: %2.2f" 
                          % newFitter.minimizerResult.redchi)
                continue
            numSuccessIteration += 1
            dct = newFitter.params.valuesdict()
            [parameterDct[p].append(dct[p]) 
                  for p in self.parametersToFit]
            newFitter.observedTS = calcObservedFunc(self, **kwargs)
        self.bootstrapResult = BootstrapResult(iteration,
              parameterDct)

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

    def reportFit(self):
        """
        Provides details of the parameter fit.
    
        Returns
        -------
        str
        """
        self._checkFit()
        if self.minimizerResult is None:
            raise ValueError("Must do fitModel before reportFit.")
        return str(lmfit.fit_report(self.minimizerResult))

    def plotResiduals(self, **kwargs):
        """
        Plots residuals of a fit over time.
    
        Parameters
        ----------
        kwargs: dict. Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._checkFit()
        options = po.PlotOptions()
        if not po.MARKER1 in kwargs:
            kwargs[po.MARKER1] = "o"
        self._plotter.plotTimeSingle(self.residualsTS, **kwargs)

    def plotFitAll(self, isMultiple=False, **kwargs):
        """
        Plots the fit with observed data over time.
    
        Parameters
        ----------
        isMultiple: bool
            plots all variables on a single plot
        kwargs: dict. Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        self._checkFit()
        self._addKeyword(kwargs, po.MARKER2, "o")
        if isMultiple:
            self._plotter.plotTimeMultiple(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)
        else:
            self._addKeyword(kwargs, po.LEGEND, ["fitted", "observed"])
            self._plotter.plotTimeSingle(self.fittedTS,
                  timeseries2=self.observedTS, **kwargs)

    def _addKeyword(self, kwargs, key, value):
        if not key in kwargs:
            kwargs[key] = value

    def _mkParameterDF(self, parameters=None):
        df = pd.DataFrame(self.bootstrapResult.parameterDct)
        if parameters is not None:
            df = df[parameters]
        df.index.name = namedTimeseries.TIME
        return NamedTimeseries(dataframe=df)

    def plotParameterEstimatePairs(self, parameters=None, **kwargs):
        """
        Does pairwise plots of parameter estimates.
        
        Parameters
        ----------
        parameters: list-str
            List of parameters to do pairwise plots
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
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

    def plotParameterHistograms(self, parameters=None, **kwargs):
        """
        Plots histographs of parameter values from a bootstrap.
        
        Parameters
        ----------
        parameters: list-str
            List of parameters to do pairwise plots
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        """
        if self.bootstrapResult is None:
            raise ValueError("Must run bootstrap before plotting parameter estimates.")
        ts = self._mkParameterDF(parameters=parameters)
        self._plotter.plotHistograms(ts, **kwargs)
        

# Update the docstrings 
_helpers.updatePlotDocstring(ModelFitter)
