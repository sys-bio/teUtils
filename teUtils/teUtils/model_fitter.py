# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
"""

import model_data

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 
import matplotlib.pyplot as plt

# Constants
PARAMETER_LOWER_BOUNDS = 0
PARAMETER_UPPER_BOUNDS = 10
DELIMITER = ","


class ModelFitter(object):
          
    def __init__(self, model, data, selected_variable_names=None, 
                 parameters_to_fit=None):      
        """
        Parameters
        ---------
        model: ExtendedRoadRunner/str
            roadrunner model or antimony model
        data: ModelData/str
            str: path to CSV file
        selected_values: list-str
            species names you wish use to fit the model
            default: all variables in data
        parameters_to_fit : list-str
            parameters in the model that you want to fit
            default: fit no parameter
               
       Examples:
            f = ModelFitter(roadrunner_model, "data.csv")
            f = ModelFitter(roadrunner_model, "data.csv", parameters_to_fit=['k1', 'k2'])
        """
        ### PUBLIC FIELDS
        self.data = ModelData(data)
        self.parameters_to_fit = parameters_to_fit
        self.result = None  # Minimizer with the result of the fit
        self.seleted_variable_names = seleted_variable_names
        self.time_to_simulate = None  # Computed later
        self.time_series_data = None  # Set later
        self.antimony_model, self.roadrunner_model = self.setModel(model)
        ### PRIVATE FIELDS
        self._indices_of_selected_species = [] 
        self._lower_bound = PARAMETER_LOWER_BOUNDS
        self._num_parameter = None
        self._roadrunner_model = roadrunner_model
        self._upper_bound = PARAMETER_UPPER_BOUNDS
        self._x_data = None  # time values
        self._y_data = None  # species values
        # Model selection       
        if roadrunner_model is not None:
            self.setRoadrunnerModel(roadrunner_model)
        elif antimony_model is not None:
            self.setAntimonyModel(antimony_model)
        # Acquire the data
        if (not time_series_file_path == None) or (not seleted_variable_names == None):
            self.setTimeSeriesData(time_series_file_path, seleted_variable_names)   
     
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
        
    def _computeSimulationData(self, params, indices_of_selected_species):
        """
        Runs a simulation and returns the species data produced.

        Parameters
        ----------
        params: lmfit.Parameters
        indices_of_selected_species: list-int

        Returns
        -------
        numpy array
            Time series data
        """
        self._roadrunner_model.reset()  
        pp = params.valuesdict()
        for i in range(0, self._num_parameter):
           self._roadrunner_model.model[self.parameters_to_fit[i]] = pp[self.parameters_to_fit[i]]
        m = self._roadrunner_model.simulate (0, self.time_to_simulate, self.number_of_data_points)
        return m[:,indices_of_selected_species]

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
        numpy array
            Time series data
        """
        # FIXME: The following is inefficient it will do for now
        # Simulate one species column at a time
        def getData(idx):
            return self._y_data[0] - self._computeSimulationData(
                  params, self._indices_of_selected_species_ids[0])
        #
        y1 = (getData(0))
        y1 = np.concatenate ((y1, ))
        for k in range (0, len (self._indices_of_selected_species_ids)-1):
            y1 = np.concatenate ((y1, (getData(k))))
        return y1
    
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
      
    def setLowerParameterBounds (self, lower_bound):
        """
        Sets the lower bonds for the parameters
              
        Example:
              f.setLowerParameterBounds (0.0)
        """
        self._lower_bound = lower_bound
        
    def setLowerParameterBounds (self, upper_bound):
        """
        Sets the upper bonds for the parameters
              
        Example:
              f.setUpperParameterBounds(20.0)
        """
        self._upper_bound =  upper_bound
        
    def fitModel(self):
        """
        Fit the model
              
        Example:
              f.fitModel ()
        """
        self.params = lmfit.Parameters()
        self._num_parameter = len (self.parameters_to_fit)
        # Update parameters in case user has changed bounds
        for k in self.parameters_to_fit:
           self.params.add(k, value=1, 
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
     
        
r = te.loada("""
    # Reactions   
        J1: S1 -> S2; k1*S1
        J2: S2 -> S3; k2*S2
        J3: S3 -> S4; k3*S3
        J4: S4 -> S5; k4*S4
        J5: S5 -> S6; k5*S5;
    # Species initializations     
        S1 = 10;
    # Parameters:      
       k1 = 1; k2 = 2; k3 = 3; k4 = 4; k5 = 5
""")
      
def tryMe():
    """
      Runs a simple example
               
      Example:
            fitModel.tryMe()
     """    
    import tellurium as te
    import numpy as np
    
    r = te.loada("""
    # Reactions   
        J1: S1 -> S2; k1*S1
        J2: S2 -> S3; k2*S2
        J3: S3 -> S4; k3*S3
        J4: S4 -> S5; k4*S4
        J5: S5 -> S6; k5*S5;
    # Species initializations     
        S1 = 10;
    # Parameters:      
       k1 = 1; k2 = 2; k3 = 3; k4 = 4; k5 = 5
    """)

    # Alternative way to start Fitter
    # f = Fitter (roadrunner_model=r, time_series_file_path='testdata.txt',
    #         seleted_variable_names=['S1', 'S2', 'S3', 'S4']),
    #         parameters_to_fit=['k1', 'k2', 'k3', 'k4', 'k5']) 
    # f.fitModel()
    
    f = Fitter(r)

    f.setParametersToFit (['k1', 'k2', 'k3', 'k4', 'k5'])
    f.setTimeSeriesData ('testdata.txt', ['S1', 'S2', 'S3', 'S4'])

    f.fitModel()
    print ("Fitted Parameters are:")
    print (f.getFittedParameters())
    f.plotTimeSeries()
    return f
  
        
