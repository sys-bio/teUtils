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
       # Fit the model parameters
       f.fit()
       # View the parameters
       list_of_values_of_fitted_parameters = f.getFittedParamters()
       # Run a simulation with the fitted parameters
       timeseries = f.simulate()
       # Get the model with the fitted parameters and do another simulation
       roadrunner_model = f.getFittedModel()
       data = roadrunner_model.simulate(0, 100, 1000)
       # Run the same model with the same timeseries but different parameters
       # and different a subset of the floating species. (By default, all
       # floating species in the data are used.)
       f2 = ModelFitter(f.roadrunner_model,  f.timeseries,
             parameters_to_fit=["k1", "k2", "k3"],
             selected_variable_names=["S1", "S2", "S3", "S4"])
"""

from named_timeseries import NamedTimeseries, ConstructorArguments, TIME

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 
import matplotlib.pyplot as plt

# Constants
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 10


class ModelFitter(object):
          
    def __init__(self, model, data, selected_variable_names=None, 
                 parameters_to_fit=None,
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
            selected_values: list-str
                species names you wish use to fit the model
                default: all variables in data
            parameters_to_fit: list-str
                parameters in the model that you want to fit
                default: fit no parameter
            parameter_lower_bound: float
                lower bound for the fitting parameters
            parameter_upper_bound: float
                upper bound for the fitting parameters
                   
           Examples:
                f = ModelFitter(roadrunner_model, "data.csv")
                f = ModelFitter(roadrunner_model, "data.csv",
                       parameters_to_fit=['k1', 'k2'])
        """
        self.timeseries = NamedTimeseries(data)
        if parameters_to_fit is None:
            parameters_to_fit = []
        self.parameters_to_fit = parameters_to_fit
        self._lower_bound = parameter_lower_bound
        self._upper_bound = parameter_upper_bound
        self.params = self._initializeParams()
        self.result = None  # Minimizer with the result of the fit
        if selected_variable_names is None:
            self.seleted_variable_names = self.timeseries.colnames
        self.roadrunner_model = self._setRoadrunnerModel(model)
     
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

    def simulate(self, params=None):
        """
            Runs a simulation and returns the species data produced.
    
            Parameters
            ----------
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
        _ = self.getFittedModel(params=params, is_reuse=True)
        named_array = self.roadrunner_model.simulate(
              self.timeseries.start, self.timeseries.end, len(self.timeseries))
        # Fix the column names by deleting '[', ']'
        colnames = [s[1:-1] if s[0] == '[' else s for s in named_array.colnames]
        timeseries = NamedTimeseries(ConstructorArguments(
              array=np.array(named_array), colnames=colnames))
        return timeseries

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
        return self.timeseries[self.selected_variable_names].flatten()  \
              - self.simulate(params=params)[
              self.selected_variable_names].flatten()
    
    def plotTimeSeries(self, y_data=None):
        """
        Plots the timeseries data.

        Parameters
        ----------
     
        y_data; np.array
            default is self._y_data
        """
        if y_data is None:
            y_data = self._y_data
        for i in range (len (self._indices_of_selected_species_ids)):
            plt.plot (self._x_data, y_data[i,:])
        plt.show()
        
    def fitModel(self):
        """
            Fits the model by adjusting values of parameters based on
            differences between simulated and provided values of
            floating species.
                  
            Example:
                  f.fitModel()
        """
        self.params = self._initializeParams()
        # Fit the model to the data
        # Use two algorithms:
        #   Global differential evolution to get us close to minimum
        #   A local Levenberg-Marquardt to getsus to the minimum
        self.result = lmfit.Minimizer(self._residuals, self.params)
        self.result.minimize(method='differential_evolution')
        self.result.minimize(method='leastsqr')

    def getFittedParameters(self):
        """
            Returns an array of the fitted parameters 
                  
            Example:
                  f.getFittedParameters ()
        """
        return [self.result.params[p].value for p in self.parameters_to_fit]

    def getFittedModel(self, params=None, is_reuse=False):
        """
            Returns a roadrunner model with parameters set to their fitted values.
        
            Parameters
            ----------
         
            params: lmfit.Parameters
            is_reuse: boolean
                Updates _roadrunner_model
    
            Returns
            -------
    
            ExtendedRoadrunnerModel
     
            Usage
            -----
                  f = ModelFitter(data, model, parameters_to_fit=parameters_to_fit)
                  f.fitModel()
                  fitted_model = f.getFittedModel()
        """
        if not is_reuse:
            model = copy.deepcopy(self.roadrunner_model)
        else:
            model = self.roadrunner_model
        if params is None:
            params = self.params
        model.reset()  
        pp = params.valuesdict()
        for parameter in self.parameters_to_fit:
           model.model[parameter] = pp[parameter]
        return model

    def _initializeParams(self):
        params = lmfit.Parameters()
        value = np.mean([self._lower_bound, self._upper_bound])
        for parameter in self.parameters_to_fit:
           params.add(parameter, value=value, 
                 min=self._lower_bound, max=self._upper_bound)
        return params

