# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
"""

# TODO:
#  1. separate test file with unittests instead of print
#  2. Travis
#  3. Constructor handles model and data, and model may be string
#  4. Constants are default values

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 


class Fitter:
     
    def __init__(self, model_stg, path, parameters=[],
          sim_time=4, len_data=30, species_list=[],
          rmodel=None):
        """
        Parameters
        ---------
        
        model_stg: str
            antimony model
        path: str
            path to data
        parameters: list-str
            parameters to estimate
        sim_time: float
            length of a simulation run
        len_data: int
            length of data produced
        species_list: list-str
            list of floating species
        rmodel: ExtendedRoadRunner
        """
        #### PRIVATE ####
        self._model_stg = model_stg
        self._path = path
        self._sim_time = sim_time
        self._len_data = len_data
        self._species_indices = None
        self._params =  None
        self._species_indices = [] # column indices of species
        #
        #### PUBLIC ####
        self.parameters = parameters  # List of parameter names
        self.species_list = species_list  # list of species names
        self.time_series = np.loadtxt(self._path, delimiter=",")
        if rmodel is None:  # roadrunner model
            self.rmodel = te.loada(model_stg)
        else:
            self.rmodel = rmodel
        self.result = None  # Result from the minimizer
        self.parameter_values = None  # Parameter estimates
        self.setTimeSeriesData(self.species_list)
         
    def setTimeSeriesData(self, species_list):
        """
        Initializes time series when setting the species_list

        Parameters
        ---------

        species_list: list-str
              list of floating species
        """
        self.species_list = species_list
        self._species_indices = []
        for i in range (len(self.species_list)):
            if self.species_list[i] in self.rmodel.getFloatingSpeciesIds():
                self._species_indices.append (i+1) # index start from 1 not zero, hence add 1
        self.x_data = self.time_series[:,0]
        self.y_data = self.time_series[:,1:len(self._species_indices)].T
        
    def computeSimulationData(self, p, SIndex):

        self.rmodel.reset()  
        pp = p.valuesdict()
        for i in range(0, self.nParameters):
           self.rmodel.model[self.parameters[i]] = pp[self.parameters[i]]
        m = self.rmodel.simulate (0, self.sim_time, self.len_data)
        return m[:,SIndex]

    # Compute the residuals between objective and experimental data
    def residuals(self, p):
        y1 = (self.y_data[0] - self.computeSimulationData (p, self._species_indices[0])); 
        y1 = np.concatenate ((y1, ))
        for k in range (0, len (self._species_indices)-1):
            y1 = np.concatenate ((y1, (self.y_data[k] - self.computeSimulationData (p, self._species_indices[k]))))
        return y1
    
    def fit(self):
        print ('Starting fit...')
        
        self._params = lmfit.Parameters()
        self.nParameters = len(self.parameters)
        for k in self.parameters:
           self._params.add(k, value=1, min=0, max=10)
        # Fit the model to the data
        # Use two algorotums:
        # global differential evolution to get us close to minimum
        # A local Levenberg-Marquardt to getsus to the minimum
        minimizer = lmfit.Minimizer(self.residuals, self._params)
        self.result = minimizer.minimize(method='differential_evolution')
        self.result = minimizer.minimize(method='leastsqr')
        self.parameter_values = self._getFittedParameters()

    def _getFittedParameters(self):
        values = []
        for i in range(0, len(self.parameters)):
            values.append (self.result.params[self.parameters[i]].value)
        return values
