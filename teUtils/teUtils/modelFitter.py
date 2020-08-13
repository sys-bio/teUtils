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
from teUtils.timeseriesPlotter import TimeseriesPlotter, PlotOptions
from teUtils import timeseriesPlotter as tp
from teUtils import _helpers

import copy
import lmfit; 
import numpy as np
import pandas as pd
import random
import roadrunner
import tellurium as te

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10
#  Minimizer methods
METHOD_BOTH = "both"
METHOD_DIFFERENTIAL_EVOLUTION = "differential_evolution"
METHOD_LEASTSQR = "leastsqr"
MAX_CHISQ = 200


class BootstrapResult():

    """Result from bootstrap"""
    def __init__(self, parameterDct):
        """
        Parameters
        ----------
        parameterDct: dict
            key: parameter name
            value: list of values
        """
        # population of parameter values
        self.parameterDct = dict(parameterDct)
        # list of parameters
        self.parameters = list(self.parameterDct.keys())
        # means of parameter values
        self.meanDct = {p: np.mean(parameterDct[p])
              for p in self.parameters}
        # standard deviation of parameter values
        self.stdDct = {p: np.std(parameterDct[p])
              for p in self.parameters}


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
        self._plotter = TimeseriesPlotter(isPlot=self._isPlot)
        # The following are calculated during fitting
        self.roadrunnerModel = None
        self.minimizer = None  # lmfit.minimizer
        self.minimizerResult = None  # Results of minimization
        self.params = None  # params property in lmfit.minimizer
        self.fittedTS = None
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
        namedArray = self.roadrunnerModel.simulate(
              self.observedTS.start, self.observedTS.end, len(self.observedTS))
        self.fittedTS = NamedTimeseries(namedArray=namedArray)

    def _residuals(self, params):
        """
        Compute the residuals between objective and experimental data

        Parameters
        ----------
        params: lmfit.Parameters

        Instance Variables Updated
        --------------------------
        self.fittedTS

        Returns
        -------
        1-d ndarray of residuals
        """
        self._simulate(params=params)
        cols = self.selectedColumns
        if self.residualsTS is None:
            self.residualsTS = self.observedTS.subsetColumns(cols)
        self.residualsTS[cols] = self.observedTS[cols]  \
              - self.fittedTS[cols]
        return self.residualsTS.flatten()
        
    def fitModel(self, params=None):
        """
        Fits the model by adjusting values of parameters based on
        differences between simulated and provided values of
        floating species.

        Parameters
        ----------
        params: lmfit.Parameters
              
        Example:
              f.fitModel()
        """
        self._initializeRoadrunnerModel()
        if self.parametersToFit is None:
            # Compute fit and residuals for base model
            _ = self._residuals(None)
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
        return np.std(self.residualsTS[self.selectedColumns])

    def calcNewObserved(self):
        """
        Calculates synthetic observations. All observed values must be
        non-negative.
        
        Returns
        -------
        NamedTimeseries
            new synthetic observations
        """
        MAX_ITERATION = 100
        self._checkFit()
        numRow = len(self.observedTS)
        #
        newObservedTS = self.observedTS.copy()
        for column in self.selectedColumns:
            newObservedTS[column] = np.random.choice(self.residualsTS[column],
                  numRow, replace=False)  + self.fittedTS[column]
            newObservedTS[column] =  \
                  np.random.permutation(self.residualsTS[column])  \
                  + self.fittedTS[column]
        #
        return newObservedTS

    def calcNewObservedOld3(self):
        """
        Calculates synthetic observations. All observed values must be
        non-negative.
        
        Returns
        -------
        NamedTimeseries
            new synthetic observations
        """
        MAX_ITERATION = 100
        self._checkFit()
        numRow = len(self.observedTS)
        #
        newObservedTS = self.observedTS.copy()
        for _ in range(MAX_ITERATION):
            isSuccess = True
            for column in self.selectedColumns:
                baseResidualStd = np.std(self.residualsTS[column])
                newObservedTS[column] = np.random.choice(self.residualsTS[column],
                      numRow, replace=True)  + self.fittedTS[column]
                residualsArr = newObservedTS[column].flatten() - self.observedTS[column].flatten()
                residualStd = np.std(residualsArr)
                if residualStd > baseResidualStd:
                    # Excessive variance
                    isSuccess = False
                    break
            if isSuccess:
                break
        #
        return newObservedTS

    def calcNewObservedOld2(self):
        """
        Calculates synthetic observations. All observed values must be
        non-negative.
        
        Returns
        -------
        NamedTimeseries
            new synthetic observations
        """
        MAX_ITERATION =100
        MAX_STD_RATIO = 1.05
        self._checkFit()
        numRow = len(self.observedTS)
        numCol = len(self.selectedColumns)
        #
        residualsArr = self.residualsTS.flatten()
        fittedArr = self.fittedTS[self.selectedColumns].flatten()
        observedArr = self.observedTS[self.selectedColumns].flatten()
        observed_std = np.std(observedArr)
        num = len(observedArr)
        done = False
        num_iteration = 0
        for _ in range(MAX_ITERATION):
            num_iteration += 1
            newObservedArr = np.random.choice(residualsArr, 
                  num, replace=True) + fittedArr
            stdRatio = np.std(newObservedArr)/observed_std
            if stdRatio <= MAX_STD_RATIO:
                done = True
                break
        if not done:
            msg = "No suitable synthetic observed values for bootstrap."
            raise ValueError(msg)
        #
        newObservedTS = self.observedTS.copy()
        newObservedTS[self.selectedColumns] = np.reshape(
              newObservedArr, (numRow, numCol))
        #
        return newObservedTS

    def calcNewObservedOld(self):
        """
        Calculates synthetic observations. All observed values must be
        non-negative.
        
        Returns
        -------
        NamedTimeseries
            new synthetic observations
        """
        MAX_ITERATION = 1
        self._checkFit()
        numRow = len(self.observedTS)
        numCol = len(self.selectedColumns)
        #
        residualsArr = self.residualsTS.flatten()
        fittedArr = self.fittedTS[self.selectedColumns].flatten()
        allIdxs = list(range(len(fittedArr)))
        length = len(allIdxs)
        selIdxs = []
        newObservedArr = np.repeat(np.nan, length)
        numIteration = 0
        while len(selIdxs) < length:
            if numIteration > MAX_ITERATION:
                msg = "No suitable synthetic observed values for bootstrap."
                raise ValueError(msg)
            missingIdxs = [s for s in set(allIdxs).difference(selIdxs)]
            numMissing = len(missingIdxs)
            newObservedArr[missingIdxs] = np.random.choice(
                  residualsArr[missingIdxs], numMissing, replace=True)  \
                  + fittedArr[missingIdxs]
            selIdxs = [i for i, v in enumerate(newObservedArr) if v >= 0]
            if len(selIdxs) == length:
                break
            numIteration += 1
        #
        newObservedTS = self.observedTS.copy()
        newObservedTS[self.selectedColumns] = np.reshape(
              newObservedArr, (numRow, numCol))
        #
        return newObservedTS

    def bootstrap(self, numIteration=10, maxIncrResidualStd=0.50,
          reportInterval=None):
        """
        Constructs a bootstrap estimate of parameter values.
    
        Parameters
        ----------
        numIteration: int
            number of bootstrap iterations
        maxIncrResidualStd: float
            maximum fractional increase in the residual std
            from the original fit to consider this fit sucessful
        reportInterval: int
            number of iterations between progress reports
              
        Example
        -------
            f.bootstrap()
            f.getFittedParameters()  # Mean values
            f.getFittedParameterStds()  # Standard deviations of values
        """


        ITERATION_MULTIPLIER = 10  # Determines maximum iterations
        self._checkFit()
        base_redchi = self.minimizerResult.redchi
        parameterDct = {p: [] for p in self.parametersToFit}
        baseResidualStd = self.calcResidualsStd()
        count = 0
        newFitter = ModelFitter(self.roadrunnerModel,
              self.observedTS,
              self.parametersToFit,
              selectedColumns=self.selectedColumns,
              method=METHOD_LEASTSQR,
              parameterLowerBound=self.LowerBound,
              parameterUpperBound=self.UpperBound,
              isPlot=self._isPlot)
        last_report = 0
        for _ in range(numIteration*ITERATION_MULTIPLIER):
            if (reportInterval is not None) and (count != last_report):
                if count % reportInterval == 0:
                    print("bootstrap completed %d iterations" % count)
                    last_report = count
            if count > numIteration:
                # Performed the iterations
                break
            # Do a fit with these observeds
            newFitter.observedTS = self.calcNewObserved()
            try:
                newFitter.fitModel(params=self.params)
            except ValueError:
                # Problem with the fit. Don't count it.
                continue
            newResidualStd = newFitter.calcResidualsStd()
            if newResidualStd > baseResidualStd*(1 + maxIncrResidualStd):
                # Standard deviation of residuals is unacceaptable as a valid fit
                continue
            if newFitter.minimizerResult.redchi > base_redchi:
                continue
            count += 1
            dct = newFitter.params.valuesdict()
            [parameterDct[p].append(dct[p]) for p in self.parametersToFit]
        self.bootstrapResult = BootstrapResult(parameterDct)

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
        options = PlotOptions()
        if not tp.MARKER1 in kwargs:
            kwargs[tp.MARKER1] = "o"
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
        self._addKeyword(kwargs, tp.MARKER2, "o")
        if isMultiple:
            self._plotter.plotTimeMultiple(self.fittedTS, timeseries2=self.observedTS,
                  **kwargs)
        else:
            self._addKeyword(kwargs, tp.LEGEND, ["fitted", "observed"])
            self._plotter.plotTimeSingle(self.fittedTS, timeseries2=self.observedTS,
                  **kwargs)

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
        self._plotter.plotValuePairs(ts, pairs, isLowerTriangular=True, **kwargs)

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
