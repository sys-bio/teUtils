# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
"""

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 
import matplotlib.pyplot as plt
import csv

# Constants
PARAMETER_LOWER_BOUNDS = 0
PARAMETER_UPPER_BOUNDS = 10


class Fitter:
          
    def __init__(self, roadrunner_model=None, antimony_model=None, 
                    time_series_file_path=None, selected_time_series_ids=None, 
                    parameters_to_fit=None):      
        """
        Parameters
        ---------
        roadrunner_model : roadrunner object
               roadrunner model
        antimony_model : string
               antimony string of a model
        data_file_name : stirng
               file path to the file containing the time series data
        selected_time_series_ids : list
               list of species names in the time series file that you wish use to fit the model
        parameters_to_fit : list
               list pf parameter names that you wish to fit in the model
               
       Examples:
            f = Fitter()
            f = Fitter(roadrunnder_model=r)
            f = Fitter (roadrunner_model=r, time_series_file_path='mydata.txt', parameters_to_fit=['k1', 'k2'])
        """
        ### PUBLIC FIELDS
        self.parameters_to_fit = parameters_to_fit
        self.selected_time_series_ids = selected_time_series_ids
        self.time_to_simulate = None  # Computed later
        self.number_of_data_points = None  # Computed later
        self.time_series_data = None  # Set later
        self._lower_bound = PARAMETER_LOWER_BOUNDS
        self._upper_bound = PARAMETER_UPPER_BOUNDS
        ### PRIVATE FIELDS
        self._antimony_model = antimony_model
        self._roadrunner_model = roadrunner_model
        self._indices_of_selected_species = [] 
        # Model selection       
        if not roadrunner_model is not None:
            self.setRoadrunnerModel(roadrunner_model)
        elif not antimony_model is not None:
            self.setAntimonyModel(antimony_model)
        # Acquire the data
        if (not time_series_file_path == None) or (not selected_time_series_ids == None):
            self.setTimeSeriesData(time_series_file_path, selected_time_series_ids)   
     
    def setRoadrunnerModel (self, roadrunner_model):
        """
        If the roadrunner model wasn't loaded when Fitter was created, this
        method allows one to set roadrunner object at a later time
        
        Parameters
        ---------
        roadrunner_model : Roadrunner model         
        """
        self._validateRoadrunnerModel(roadrunner_model)
        self._roadrunner_model = model
        self._antimony_model = te.sbmlToAntimony(self._roadrunner_model.getSBML())
        
    def setAntimonyModel (self, antimony_model):
        """
        This allows one to set a new model to the Fitter object 
        
        Parameters
        ---------
        roadrunner_model : Roadrunner model         
        """
        self._antimony_model = antimony_model
        try:
            self._roadrunner_model = te.loada(antimony_model)
        except Exception:
            raise ValueError(
                  "Invalid antimony_model:\n%s" % antomony_model)

    def _validateRoadrunnerModel(self, roadrunner_model):
        if roadrunner_model is None:
           raise ValueError(
                 'No roadrunner model. Use setRoadRunnerModel.')
        if type(roadrunner_model)  \
              != te.roadrunner.extended_roadrunner.ExtendedRoadRunner:
            msg = 'Invalid roadrunner model.'
            msg = msg + "\nYou can create a roadrunner model using tellurium.loada."
            raise Exception (msg)

    def _validateAntimonyModel(self, antimony_model):
        if self._antimony_model is None:
           raise ValueError(
                 'No antimony model. Use setAntimonyModel')
        if not instance(antimony_model, str):
            raise Exception ('Antimony model must be a string. Please try again.')
        
    def getRoadRunnerModel(self):
        self._validateRoadrunnerModel(self._roadrunner_model)
        return self._roadrunner_model
       
    def getAntimonyModel(self):
        if self._antimony_model is None:
           raise ValueError(
                 'No antimony model. Use setAntimonyModel')
        return self._antimony_model
       
    def setParametersToFit(self, parameters_to_fit):
        self.parameters_to_fit = parameters_to_fit
       
    def getParametersToFit(self):
        return self.parameters_to_fit
       
    def setTimeSeriesData(self, time_series_file_path, selected_time_series_ids=None):
        """
        Load the experimental data stored in the file 'fileWithData'
        This data will be used to fit the parameters of the model
        
        Parameters
        ----------
        
        time_series_file_path : string
              Path to the file containing time series data. Data should be arranged
              in columns, first colums representing time, remaining columns will
              be whatever timeseries data is avaialble.
       selected_time_series_ids : list of strings
              List of names of floating species that are the columns in the 
              time series data. If the list of names is missing then it is assumed that
              all the time series columns should be used in the fit
              
        Examples:
              f.setTimeSeriesData('mydata.txt', ['S1', 'S2'])
              f.setTimeSeriesData('mydata.txt')
        
        Note on Id and Index lists:
        selected_time_series_ids : list of species selected by user to be used in the fit
        model_species_ids : list of species in the mode itself
        time_series_ids : list of species columns in the time series data file
        
        The same variable with "indices_" in front represent list of integers
        where the integer are indices that map to the order of floating
        floaating species in the model itself. 
        """
        self._validateRoadrunnerModel(self._roadrunner_model)
        self.model_species_ids = self._roadrunner_model.getFloatingSpeciesIds();
        # Open the data file and look for the header line         
        try:
            with open(time_series_file_path, 'r') as f:
                reader = csv.reader(f, delimiter=',')
                if csv.Sniffer().has_header(f.readline()):
                    f.seek(0)
                    self.time_series_ids = next(reader)
                    # Add a check that the first column is time
                    del self.time_series_ids[0] # remove time
                else:
                    raise ValueError('No column headers %s' % time_series_file_path)
        except IOError:
            raise ValueError("There is a problem with the data path %s" %
       self.time_series_data = np.array(list(reader)).astype(float)
    
        # if the user didn't specify any variable that wantto use then default to 
        # all variables indicated in the time series file
        if selected_time_series_ids == None:
           selected_time_series_ids = self.time_series_ids
           
        # Some sanity checks:
           
        # Check that the columns in the time series data file exist in the model
        for id in self.model_species_ids:
            if not id in self.time_series_ids:
               raise Exception ('Error: The following column in the data file: ' + id + ' does not correspond to a species in the model')

        # Check that the selected_time_series_ids exist inthe model
        #print (selected_time_series_ids)
        for id in selected_time_series_ids:
            #print (id)
            if not id in self.model_species_ids:
               raise Exception ('Error: The column: ' + id + ' in the data file does not correspond to a species in the model')
       
       
        # Find the indices of the data series columns, indices reference the roadrunner species indices
        self.indices_of_time_series_ids = []
        for index, id in enumerate (self.time_series_ids):
            if id in self._roadrunner_model.getFloatingSpeciesIds():
               self.indices_of_time_series_ids.append (index+1) 
            
        self.number_of_data_points = len(self.time_series_data)
        self.time_to_simulate = self.time_series_data[len(self.time_series_data)-1][0]
        
        # Get the indices of the seleted species, these also directly map to the roadrunner species indices
        self._indices_of_selected_species_ids = []        
        for i in range (len (selected_time_series_ids)):
            if selected_time_series_ids[i] in self._roadrunner_model.getFloatingSpeciesIds():
                # Add one because index must start from 1 not zero
                self._indices_of_selected_species_ids.append (self.model_species_ids.index (selected_time_series_ids[i])+1)
               
        #print ('indices_of_selected_species_ids = ', self._indices_of_selected_species_ids)
        #print ('self.indices_of_time_series_ids = ', self.indices_of_time_series_ids)
        self.x_data = self.time_series_data[:,0]  

        # Pluck out times series columns as defined by  
        # indices_of_time_series_ids and put them into y_data 
        self._nColumns = len (self._indices_of_selected_species_ids)
         
        self.y_data = np.empty((0,self.number_of_data_points))
        for index in self._indices_of_selected_species_ids:
            self.y_data = np.vstack((self.y_data, self.time_series_data[:,index]))       
        
           
    def getTimeSeriesData (self):
        """
        
        Returns
        -------
        numpy array
            Time series data

        """
        try:
            return self.time_series_data
        except AttributeError:
           raise Exception ('Error: Time series data has not yet been set. Use setTimeSeriesData()')
        
           
    def _computeSimulationData(self, p, speciesIndex):

        self._roadrunner_model.reset()  
        pp = p.valuesdict()
        for i in range(0, self.nParameters):
           self._roadrunner_model.model[self.parameters_to_fit[i]] = pp[self.parameters_to_fit[i]]
        m = self._roadrunner_model.simulate (0, self.time_to_simulate, self.number_of_data_points)
        return m[:,speciesIndex]


    # Compute the residuals between objective and experimental data
    # Python optimizers often require the residual rather than the sum
    # of squares themselves. Hence we just copute the residuals which are
    # the difference between the simulated data the time read in time series data 
    def _residuals(self, p):
        # The following is inefficient it will do for now
        # Simulate one species column at a time
        y1 = (self.y_data[0] - self._computeSimulationData (p, self._indices_of_selected_species_ids[0])); 
        y1 = np.concatenate ((y1, ))
        for k in range (0, len (self._indices_of_selected_species_ids)-1):
            y1 = np.concatenate ((y1, (self.y_data[k] - self._computeSimulationData (p, self._indices_of_selected_species_ids[k]))))
        return y1
    
    def plotTimeSeries(self):

        for i in range (len (self._indices_of_selected_species_ids)):
            plt.plot (self.x_data, self.y_data[i,:])
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
        print ('Starting fit...')
        
        self.params = lmfit.Parameters()
        self.nParameters = len (self.parameters_to_fit)
        # Update parameters in case user has changed bounds
        for k in self.parameters_to_fit:
           self.params.add(k, value=1, 
                 min=self._lower_bound, max=self._upper_bound)
           
        # Fit the model to the data
        # Use two algorithms:
        #   Global differential evolution to get us close to minimum
        #   A local Levenberg-Marquardt to getsus to the minimum
        minimizer = lmfit.Minimizer(self._residuals, self.params)
        self.result = minimizer.minimize(method='differential_evolution')
        self.result = minimizer.minimize(method='leastsqr')


    def getFittedParameters (self):
        """
        Returns an array of the fitted parameters 
              
        Example:
              f.getFittedParameters ()
        """
        fittedParameters = []
        for i in range(0, self.nParameters):
            fittedParameters.append (self.result.params[self.parameters_to_fit[i]].value)
        return fittedParameters
     
        
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
    #         selected_time_series_ids=['S1', 'S2', 'S3', 'S4']),
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
  
        
