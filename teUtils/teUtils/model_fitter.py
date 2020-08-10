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
         parameters_to_fit=["k1", "k2"])
   # Fit the model parameters and view parameters
   f.fitModel()
   print(f.getFittedParamters())
   # Print observed, fitted and residual values
   print(f.observed_ts)
   print(f.fitted_ts)
   print(f.residuals_ts)
"""

from teUtils.named_timeseries import NamedTimeseries, TIME, mkNamedTimeseries
from teUtils import named_timeseries
from teUtils.timeseries_plotter import TimeseriesPlotter, PlotOptions
from teUtils import timeseries_plotter as tp
from teUtils import helpers

import copy
import lmfit; 
import numpy as np
import pandas as pd
import roadrunner
import tellurium as te

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10
#  Minimizer methods
METHOD_BOTH = "both"
METHOD_DIFFERENTIAL_EVOLUTION = "differential_evolution"
METHOD_LEASTSQR = "leastsqr"


class BootstrapResult():

    """Result from bootstrap"""
    def __init__(self, parameter_dct):
        """
        Parameters
        ----------
        parameter_dct: dict
            key: parameter name
            value: list of values
        """
        # population of parameter values
        self.parameter_dct = dict(parameter_dct)
        # list of parameters
        self.parameters = list(self.parameter_dct.keys())
        # means of parameter values
        self.mean_dct = {p: np.mean(parameter_dct[p])
              for p in self.parameters}
        # standard deviation of parameter values
        self.std_dct = {p: np.std(parameter_dct[p])
              for p in self.parameters}


class ModelFitter(object):
          
    def __init__(self, model_specification, observed, parameters_to_fit,
                 selected_columns=None, method=METHOD_BOTH,
                 parameter_lower_bound=PARAMETER_LOWER_BOUND,
                 parameter_upper_bound=PARAMETER_UPPER_BOUND,
                 is_plot=True
                 ):      
        """
        Parameters
        ---------
        model_specification: ExtendedRoadRunner/str
            roadrunner model or antimony model
        observed: NamedTimeseries/str
            str: path to CSV file
        parameters_to_fit: list-str/None
            parameters in the model that you want to fit
            if None, no parameters are fit
        selected_columns: list-str
            species names you wish use to fit the model
            default: all columns in observed
        parameter_lower_bound: float
            lower bound for the fitting parameters
        parameter_upper_bound: float
            upper bound for the fitting parameters
        method: str
            method used for minimization
               
        Usage
        -----
        f = ModelFitter(roadrunner_model, "observed.csv", ['k1', 'k2'])
        """
        self.model_specification = model_specification
        self.observed_ts = mkNamedTimeseries(observed)
        self.parameters_to_fit = parameters_to_fit
        self._lower_bound = parameter_lower_bound
        self._upper_bound = parameter_upper_bound
        if selected_columns is None:
            selected_columns = self.observed_ts.colnames
        self.selected_columns = selected_columns
        self._method = method
        self._is_plot = is_plot
        # The following are calculated during fitting
        self.roadrunner_model = None
        self.minimizer = None  # lmfit.minimizer
        self.minimizer_result = None  # Results of minimization
        self.params = None  # params property in lmfit.minimizer
        self.fitted_ts = None
        self.residuals_ts = None  # Residuals for selected_columns
        self.bootstrap_result = None  # Result from bootstrapping
     
    def _initializeRoadrunnerModel(self):
        """
            Sets self.roadrunner_model.
        """
        if isinstance(self.model_specification,
              te.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            self.roadrunner_model = self.model_specification
        elif isinstance(self.model_specification, str):
            self.roadrunner_model = te.loada(self.model_specification)
        else:
            msg = 'Invalid model.'
            msg = msg + "\nA model must either be a Roadrunner model "
            msg = msg + "an Antimony model."
            raise ValueError(msg)

    def _simulate(self, params=None):
        """
        Runs a simulation. Updates self.fitted_ts.

        Parameters
        ----------
        params: lmfit.Parameters

        Instance Variables Updated
        --------------------------
        self.fitted_ts
        """
        self._setupModel(params=params)
        named_array = self.roadrunner_model.simulate(
              self.observed_ts.start, self.observed_ts.end, len(self.observed_ts))
        self.fitted_ts = NamedTimeseries(named_array=named_array)

    def _residuals(self, params):
        """
        Compute the residuals between objective and experimental data

        Parameters
        ----------
        params: lmfit.Parameters

        Instance Variables Updated
        --------------------------
        self.fitted_ts

        Returns
        -------
        1-d ndarray of residuals
        """
        self._simulate(params=params)
        cols = self.selected_columns
        if self.residuals_ts is None:
            self.residuals_ts = self.observed_ts.subsetColumns(cols)
        self.residuals_ts[cols] = self.observed_ts[cols]  \
              - self.fitted_ts[cols]
        return self.residuals_ts.flatten()
        
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
        if self.parameters_to_fit is None:
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
                self.minimizer_result = minimizer.minimize(method='differential_evolution')
            if self._method in [METHOD_BOTH, METHOD_LEASTSQR]:
                minimizer = lmfit.Minimizer(self._residuals, params)
                self.minimizer_result = minimizer.minimize(method='leastsqr')
            self.params = self.minimizer_result.params
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
        if self.bootstrap_result is None:
            return [self.params[p].value for p in self.parameters_to_fit]
        else:
            return self.bootstrap_result.mean_dct.values()

    def getFittedParameterStds(self):
        """
        Returns the standard deviations for fitted values.
              
        Example
        -------
              f.getFittedParameterStds()
        """
        self._checkFit()
        if self.bootstrap_result is None:
            raise ValueError("Must use bootstrap first.")
        return list(self.bootstrap_result.std_dct.values())

    def getFittedModel(self):
        """
        Provides the roadrunner model with fitted parameters
    
        Returns
        -------
        ExtendedRoadrunner
        """
        self._checkFit()
        self.roadrunner_model.reset()
        self._setupModel(params=self.params)
        return self.roadrunner_model

    def calcResidualsStd(self):
        return np.std(self.residuals_ts[self.selected_columns])

    def calcNewObserved(self):
        """
        Calculates synthetic observations. All observed values must be
        non-negative.
        
        Returns
        -------
        NamedTimeseries
            new synthetic observations
        """
        MAX_ITERATION = 1000
        self._checkFit()
        num_row = len(self.observed_ts)
        num_col = len(self.selected_columns)
        #
        residuals_arr = self.residuals_ts.flatten()
        fitted_arr = self.fitted_ts[self.selected_columns].flatten()
        all_idxs = list(range(len(fitted_arr)))
        length = len(all_idxs)
        sel_idxs = []
        new_observed_arr = np.repeat(np.nan, length)
        num_iteration = 0
        while len(sel_idxs) < length:
            num_iteration += 1
            if num_iteration > MAX_ITERATION:
                msg = "No suitable synthetic observed values for bootstrap."
                raise ValueError(msg)
            missing_idxs = [s for s in set(all_idxs).difference(sel_idxs)]
            num_missing = len(missing_idxs)
            new_observed_arr[missing_idxs] = np.random.choice(
                  residuals_arr[missing_idxs], num_missing, replace=True)  \
                  + fitted_arr[missing_idxs]
            sel_idxs = [i for i, v in enumerate(new_observed_arr) if v >= 0]
            if len(sel_idxs) == length:
                break
        #
        new_observed_ts = self.observed_ts.copy()
        new_observed_ts[self.selected_columns] = np.reshape(
              new_observed_arr, (num_row, num_col))
        #
        return new_observed_ts

    def bootstrap(self, num_iteration=10, max_incr_residual_std=0.50,
          report_interval=None):
        """
        Constructs a bootstrap estimate of parameter values.
    
        Parameters
        ----------
        num_iteration: int
            number of bootstrap iterations
        max_incr_residual_std: float
            maximum fractional increase in the residual std
            from the original fit to consider this fit sucessful
        report_interval: int
            number of iterations between progress reports
              
        Example
        -------
            f.bootstrap()
            f.getFittedParameters()  # Mean values
            f.getFittedParameterStds()  # Standard deviations of values
        """


        ITERATION_MULTIPLIER = 10  # Determines maximum iterations
        self._checkFit()
        parameter_dct = {p: [] for p in self.parameters_to_fit}
        base_residual_std = self.calcResidualsStd()
        count = 0
        for _ in range(num_iteration*ITERATION_MULTIPLIER):
            if count > num_iteration:
                # Performed the iterations
                break
            try:
                new_observed_ts = self.calcNewObserved()
            except ValueError:
                # Couldn't find valid synthetic observations
                continue
            # Do a fit with these observeds
            new_fitter = ModelFitter(self.roadrunner_model,
                  new_observed_ts,
                  self.parameters_to_fit,
                  selected_columns=self.selected_columns,
                  method=METHOD_LEASTSQR,
                  parameter_lower_bound=self._lower_bound,
                  parameter_upper_bound=self._upper_bound,
                  is_plot=self._is_plot)
            try:
                new_fitter.fitModel(params=self.params)
            except ValueError:
                # Problem with the fit. Don't count it.
                continue
            new_residual_std = new_fitter.calcResidualsStd()
            if new_residual_std > base_residual_std*(1 + max_incr_residual_std):
                # Standard deviation of residuals is unacceaptable as a valid fit
                continue
            count += 1
            dct = new_fitter.params.valuesdict()
            [parameter_dct[p].append(dct[p]) for p in self.parameters_to_fit]
            if report_interval is not None:
                if count % report_interval == 0:
                    print("bootstrap completed %d iterations" % (count + 1))
        self.bootstrap_result = BootstrapResult(parameter_dct)

    def _setupModel(self, params=None):
        """
        Sets up the model for use based on the parameter parameters
    
        Parameters
        ----------
        params: lmfit.Parameters
 
        """
        self.roadrunner_model.reset()  
        if params is not None:
            pp = params.valuesdict()
            for parameter in self.parameters_to_fit:
               self.roadrunner_model.model[parameter] = pp[parameter]

    def _initializeParams(self):
        params = lmfit.Parameters()
        value = np.mean([self._lower_bound, self._upper_bound])
        for parameter in self.parameters_to_fit:
           params.add(parameter, value=value, 
                 min=self._lower_bound, max=self._upper_bound)
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
        if self.minimizer_result is None:
            raise ValueError("Must do fitModel before reportFit.")
        return str(lmfit.fit_report(self.minimizer_result))

    def plotResiduals(self, **kwargs):
        """
        Plots residuals of a fit over time.
    
        Parameters
        ----------
        kwargs: dict. Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
        """
        self._checkFit()
        options = PlotOptions()
        plotter = TimeseriesPlotter(is_plot=self._is_plot)
        if not tp.MARKER1 in kwargs:
            kwargs[tp.MARKER1] = "o"
        plotter.plotTimeSingle(self.residuals_ts, **kwargs)

    def plotFitAll(self, is_multiple=False, **kwargs):
        """
        Plots the fit with observed data over time.
    
        Parameters
        ----------
        is_multiple: bool
            plots all variables on a single plot
        kwargs: dict. Plotting options.
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
        """
        self._checkFit()
        plotter = TimeseriesPlotter(is_plot=self._is_plot)
        self._addKeyword(kwargs, tp.MARKER2, "o")
        if is_multiple:
            plotter.plotTimeMultiple(self.fitted_ts, timeseries2=self.observed_ts,
                  **kwargs)
        else:
            self._addKeyword(kwargs, tp.LEGEND, ["fitted", "observed"])
            plotter.plotTimeSingle(self.fitted_ts, timeseries2=self.observed_ts,
                  **kwargs)

    def _addKeyword(self, kwargs, key, value):
        if not key in kwargs:
            kwargs[key] = value

    def plotParameterEstimates(self, **kwargs):
        """
        Does pairwise plots of parameter estimates.
        
        Parameters
        ----------
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseries_plotter.EXPAND_KEYPRHASE.)
        """
        if self.bootstrap_result is None:
            raise ValueError("Must run bootstrap before plotting parameter estimates.")
        df = pd.DataFrame(self.bootstrap_result.parameter_dct)
        df.index.name = named_timeseries.TIME
        ts = NamedTimeseries(dataframe=df)
        plotter = TimeseriesPlotter()
        # Construct pairs
        names = list(self.bootstrap_result.parameter_dct.keys())
        pairs = []
        compares = list(names)
        for name in names:
            compares.remove(name)
            pairs.extend([(name, c) for c in compares])
        #
        plotter.plotValuePairs(ts, pairs, **kwargs)
        
       

# Update the docstrings 
helpers.updatePlotDocstring(ModelFitter)
