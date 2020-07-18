# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
"""

from named_timeseries import NamedTimeseries

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 
import matplotlib.pyplot as plt

# Constants
PARAMETER_LOWER_BOUNDS = 0
PARAMETER_UPPER_BOUNDS = 10


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
            f = ModelFitter(roadrunner_model, "data.csv", parameters_to_fit=['k1', 'k2'])
        """
        ### PUBLIC FIELDS
        self.timeseries = NamedTimeseries(data)
        if parameters_to_fit is None:
            parameters_to_fit = []
        self.parameters_to_fit = parameters_to_fit
        self.result = None  # Minimizer with the result of the fit
        if selected_variable_names is None:
            self.seleted_variable_names = self.timeseries.colnames
        self.roadrunner_model = self._setRoadrunnerModel(model)
        ### PRIVATE FIELDS
        self._lower_bound = parameter_lower_bound
        self._upper_bound = parameter_upper_bound
     
    def _setRoadrunnerModel(self, model):
        """
        Set values for the roadrunner and antimony models.

        Parameters
        ----------

        model: ExtendedRoadRunnerModel/str
        """
        if isinstance(model,
              te.roadrunner.extended_roadrunner.ExtendedRoadRunner):
            self.roadrunner_model = model
            self.antimony_model =  \
                    te.sbmlToAntimony(self._roadrunner_model.getSBML())
        elif isinstance(model, str):
            self.antimony_model = model
            self.roadrunner_model = te.loada(self.antimony_model)
        else:
            msg = 'Invalid model.'
            msg = msg + "\nA model must either be a Roadrunner model "
            msg = msg + "an Antimony model."
            raise ValueError(msg)

    def _computeSimulationData(self, params):
        """
        Runs a simulation and returns the species data produced.

        Parameters
        ----------
        params: lmfit.Parameters

        Returns
        -------
        NamedTimeseries
        """
        self._roadrunner_model.reset()  
        pp = params.valuesdict()
        for parameter in self.parameters_to_fit:
           self._roadrunner_model.model[parameter] = pp[parameter]
        named_array = self._roadrunner_model.simulate(
              self.timeseries.start, self.timeseries.end, len(self.timeseries))
        # FIXME: what are the column names
        timeseries = NamedTimeseries((named_array.colnames, named_array))
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
        return self.timeseries[self.selected_variable_names].flatten()
              - self._computeSimulationData(params)[
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
        Fit the model
              
        Example:
              f.fitModel ()
        """
        self.params = lmfit.Parameters()
        # Update parameters in case user has changed bounds
        for parameter in self.parameters_to_fit:
           self.params.add(parameter, value=1, 
                 min=self._lower_bound, max=self._upper_bound)
        # Fit the model to the data
        # Use two algorithms:
        #   Global differential evolution to get us close to minimum
        #   A local Levenberg-Marquardt to getsus to the minimum
        self.result = lmfit.Minimizer(self._residuals, self.params)
        self.result.minimize(method='differential_evolution')
        self.result.minimize(method='leastsqr')

    def getFittedParameters (self):
        """
        Returns an array of the fitted parameters 
              
        Example:
              f.getFittedParameters ()
        """
        return [self.result.params[p].value for p in self.parameters_to_fit]
