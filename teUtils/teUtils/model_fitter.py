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
from teUtils.timeseries_plotter import TimeseriesPlotter, PlotOptions
from teUtils import timeseries_plotter as tp

import lmfit; 
import numpy as np
import roadrunner
import tellurium as te

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10
#  Minimizer methods
METHOD_BOTH = "both"
METHOD_DIFFERENTIAL_EVOLUTION = "differential_evolution"
METHOD_LEASTSQR = "leastsqr"


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
        self.minimizer = None
        self.minimizer_result = None  # Results of minimization
        self.params = None
        self.fitted_ts = None
        self.residuals_ts = self.observed_ts.copy()
     
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
        cols = self.residuals_ts.colnames
        self.residuals_ts[cols] = self.observed_ts[cols] - self.fitted_ts[cols]
        arr = self.residuals_ts[self.selected_columns]
        self.residuals_ts[self.selected_columns] = arr
        return arr.flatten()
        
    def fitModel(self):
        """
        Fits the model by adjusting values of parameters based on
        differences between simulated and provided values of
        floating species.
              
        Example:
              f.fitModel()
        """
        self._initializeRoadrunnerModel()
        if self.parameters_to_fit is None:
            # Compute fit and residuals for base model
            _ = self._residuals(None)
        else:
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

    def getFittedParameters(self):
        """
        Returns an array of the fitted parameters 
              
        Example:
              f.getFittedParameters ()
        """
        self._checkFit()
        return [self.params[p].value for p in self.parameters_to_fit]

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
        kwargs: dict
           plot options
        """
        self._checkFit()
        options = PlotOptions()
        plotter = TimeseriesPlotter(is_plot=self._is_plot)
        if not tp.MARKER1 in kwargs:
            kwargs[tp.MARKER1] = "o"
        plotter.plotTimeSingle(self.residuals_ts, **kwargs)

    def plotFit(self, is_multiple=False, **kwargs):
        """
        Plots the fit with observed data over time.
    
        Parameters
        ----------
        is_multiple: bool
            plots all variables on a single plot
        kwargs: dict
            plot options
        """
        self._checkFit()
        plotter = TimeseriesPlotter(is_plot=self._is_plot)
        self._addKeyword(kwargs, tp.MARKER2, "o")
        if is_multiple:
            plotter.plotTimeMultiple(self.fitted_ts, timeseries2=self.observed_ts,
                  **kwargs)
        else:
            if not tp.LEGEND in kwargs:
                kwargs[tp.LEGEND] = ["observed", "fited"]
            plotter.plotTimeSingle(self.fitted_ts, timeseries2=self.observed_ts,
                  **kwargs)

    def _addKeyword(self, kwargs, key, value):
        if not key in kwargs:
            kwargs[key] = value

    def plotAll(self, **kwargs):
        """
        Plots fitted and observed values on a single plot.
    
        Parameters
        ----------
        kwargs: dict
           plot options
        """
        plotter = TimeseriesPlotter(is_plot=self._is_plot)
        self._addKeyword(kwargs, tp.MARKER1, "o")
        plotter.plotTimeMultiple(self.observed_ts, timeseries2=self.fitted_ts, num_col=1, num_row=1,
              **kwargs)
        
