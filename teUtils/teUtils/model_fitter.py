# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro

    A ModelFitter estimates parameters of a roadrunner model by fitting simulation
    results to a timeseries. The user can access values of the fitted parameters,
    can run simulations with these fitted parameters, can obtain a roadrunner model
    with the fitted parameters.
    
    Usage
    -----
       # The constructor takes either a roadrunner or antimony model
       f = ModelFitter(model, "mydata.txt",
             parameters_to_fit=["k1", "k2"])
       # Fit the model parameters and view parameters
       f.fit()
       print(f.getFittedParamters())
       # Run a simulation with the fitted parameters
       timeseries = f.simulate()
       # Get the model with the fitted parameters and simulate over a different time period
       roadrunner_model = f.getFittedModel()
       data = roadrunner_model.simulate(0, 100, 1000)
"""

from named_timeseries import NamedTimeseries, TIME

import lmfit; 
import numpy as np
import roadrunner
import tellurium as te 

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10


class ModelFitter(object):
          
    def __init__(self, model, data, parameters_to_fit,
                 selected_variable_names=None, 
                 parameter_lower_bound=PARAMETER_LOWER_BOUND,
                 parameter_upper_bound=PARAMETER_UPPER_BOUND,
                 ):      
        """
        Parameters
        ---------
        model: ExtendedRoadRunner/str
            roadrunner model or antimony model
        data: NamedTimeseries/str
            str: path to CSV file
        parameters_to_fit: list-str
            parameters in the model that you want to fit
        selected_values: list-str
            species names you wish use to fit the model
            default: all variables in data
        parameter_lower_bound: float
            lower bound for the fitting parameters
        parameter_upper_bound: float
            upper bound for the fitting parameters
               
        Usage
        -----
        f = ModelFitter(roadrunner_model, "data.csv", ['k1', 'k2'])
        """
        if isinstance(data, str):
            self.timeseries = NamedTimeseries(csv_path=data)
        elif isinstance(data, NamedTimeseries):
            self.timeseries = NamedTimeseries(timeseries=data)
        else:
            msg = "Invalid data specification."
            msg += " Must be either file path or NamedTimeseries."
            raise ValueError(msg)
        self.parameters_to_fit = parameters_to_fit
        self._lower_bound = parameter_lower_bound
        self._upper_bound = parameter_upper_bound
        self.minimizer = None  # Minimizer with the result of the fit
        if selected_variable_names is None:
            self.selected_variable_names = self.timeseries.colnames
        else:
            self.selected_variable_names = selected_variable_names
        self.roadrunner_model = self._setRoadrunnerModel(model)
        self.unoptimized_residual_variance  \
              = self._calculateUnoptimizedResidualVariance()
        # Variance of residuals of optimized model
        self.optimized_residual_variance = None

    def _calculateResidualVariance(self, timeseries):
        residuals = self.timeseries[self.selected_variable_names]  \
              - timeseries[self.selected_variable_names]
        return np.var(residuals)

    def _calculateUnoptimizedResidualVariance(self):
        return self._calculateResidualVariance(self.simulate())
     
    def _setRoadrunnerModel(self, model):
        """
            Set values for the roadrunner and antimony models.
    
            Parameters
            ----------
    
            model: ExtendedRoadRunnerModel/str
    
            Returns
            -------
            ExtendedRoadRunner
        """
        if isinstance(model,
              te.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            roadrunner_model = model
        elif isinstance(model, str):
            roadrunner_model = te.loada(model)
        else:
            msg = 'Invalid model.'
            msg = msg + "\nA model must either be a Roadrunner model "
            msg = msg + "an Antimony model."
            raise ValueError(msg)
        return roadrunner_model

    def simulate(self, model=None, params=None, is_reset=False):
        """
            Runs a simulation and returns the species data produced.
    
            Parameters
            ----------
            model: ExtendedRoadRunner
            params: lmfit.Parameters
    
            Returns
            -------
            NamedTimeseries
    
            Usage
            -----
            f = ModelFitter(data, model, parameters_to_fit=["k1", "k2"])
            f.fitModel()
            timeseries = f.simulate()
        """
        if model is None:
            model = self.roadrunner_model
        if is_reset:
            model.reset()
        _ = self.getFittedModel(params=params)
        named_array = model.simulate(
              self.timeseries.start, self.timeseries.end, len(self.timeseries))
        return NamedTimeseries(named_array=named_array)

    def _residuals(self, params):
        """
            Compute the residuals between objective and experimental data
            Python optimizers often require the residual rather than the sum
            of squares themselves. Hence we just copute the residuals which are
            the difference between the simulated data the time read in time series data 
            Runs a simulation and returns the species data produced.
    
            Parameters
            ----------
            params: lmfit.Parameters
    
            Returns
            -------
            NamedTimeseries
        """
        arr = self.timeseries[self.selected_variable_names]  \
              - self.simulate(params=params)[self.selected_variable_names]
        arr = arr.flatten()
        return arr
        
    def fitModel(self):
        """
        Fits the model by adjusting values of parameters based on
        differences between simulated and provided values of
        floating species.
              
        Example:
              f.fitModel()
        """
        is_error = False
        if not isinstance(self.parameters_to_fit, list):
            is_error = True
        if len(self.parameters_to_fit) == 0:
            is_error = True
        if is_error:
            raise ValueError("Must specify at least one parameter to fit")
        params = self._initializeParams()
        # Fit the model to the data
        # Use two algorithms:
        #   Global differential evolution to get us close to minimum
        #   A local Levenberg-Marquardt to getsus to the minimum
        minimizer = lmfit.Minimizer(self._residuals, params)
        result = minimizer.minimize(method='differential_evolution')
        minimizer = lmfit.Minimizer(self._residuals, result.params)
        self.minimizer = minimizer.minimize(method='leastsqr')
        # Calculate residuals for the fitted model
        fitted_model = self.getFittedModel()
        simulated_timeseries = self.simulate(model=fitted_model, is_reset=True)
        self.optimized_residual_variance =  \
              self._calculateResidualVariance(simulated_timeseries)

    def getFittedParameters(self):
        """
            Returns an array of the fitted parameters 
                  
            Example:
                  f.getFittedParameters ()
        """
        if self.minimizer is None:
            raise ValueError("Must fit model before extracting fitted parameters")
        return [self.minimizer.params[p].value for p in self.parameters_to_fit]

    def getFittedModel(self, params=None):
        """
            Returns a reset roadrunner model with parameters set to their fitted values.
        
            Parameters
            ----------
            params: lmfit.Parameters
    
            Returns
            -------
            ExtendedRoadrunnerModel
     
            Usage
            -----
                  f = ModelFitter(data, model, parameters_to_fit=parameters_to_fit)
                  f.fitModel()
                  fitted_model = f.getFittedModel()
        """
        # Set the parameters
        self.roadrunner_model.reset()  
        if (params is None) and (self.minimizer is not None):
            params = self.minimizer.params
        if params is not None:
            pp = params.valuesdict()
            for parameter in self.parameters_to_fit:
               self.roadrunner_model.model[parameter] = pp[parameter]
        return self.roadrunner_model

    def _initializeParams(self):
        params = lmfit.Parameters()
        value = np.mean([self._lower_bound, self._upper_bound])
        for parameter in self.parameters_to_fit:
           params.add(parameter, value=value, 
                 min=self._lower_bound, max=self._upper_bound)
        return params

