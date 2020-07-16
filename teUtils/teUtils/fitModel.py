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

class fitter:
          
     def __init__(self, roadrunner_model=None, antimony_model=None, 
                     time_series_file_name=None, selected_time_series_ids=None, 
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
               f = fitter()
               f = fitter(r)
               f = fitter (r, time_series_file_name='mydata.txt', parameters_to_fit=['k1', 'k2'])
         """
        
         if roadrunner_model != None:
            if type (roadrunner_model) != te.roadrunner.extended_roadrunner.ExtendedRoadRunner:
               raise Exception ('Roadrunner argument is not a roadrunner variable, please use a roadrunner variable')

         # Public fields 
         self.parameters_to_fit = parameters_to_fit
         self.selected_time_series_ids = selected_time_series_ids
         self.time_to_simulate = 4 # Now computed for us  
         self.number_of_data_points = 30  # Now computed for us
         self.time_series_data = 0
         
         self._lowerBounds = 0
         self._upperBounds = 10
    
         # Private fields
         self._antimony_model = antimony_model
         self._indices_of_selected_species = [] 
        
         if not roadrunner_model is None:
            self._roadrunner_model = roadrunner_model
         if not antimony_model is None:
            self._roadrunner_model = te.loada (antimony_model)
            
         if (not time_series_file_name == None) or (not selected_time_series_ids == None):
             self.setTimeSeriesData (time_series_file_name, selected_time_series_ids)   
     
        
     def setRoadrunnerModel (self, roadrunner_model):
         """
           If the roadrunner model wasn't loaded when fitter was created, this
           method allows one to set roadrunner object at a later time
           
           Parameters
           ---------
           roadrunner_model : Roadrunner model         
         """
         if type (roadrunner_model) != te.roadrunner.extended_roadrunner.ExtendedRoadRunner:
             raise Exception ('Model not set, please set the model first')

         self._roadrunner_model = model
         
         
     def setAntimonyModel (self, antimony_model):
         """
           This allows one to set a new model to the fitter object 
           
           Parameters
           ---------
           roadrunner_model : Roadrunner model         
         """
         self._roadrunner_model = antimony_model
         
         
     def getRoadRunnerModel (self):
         if self._roadrunner_model is None:
            raise Exception ('There is no roadrunner model, use setRoadRunnermodel first')
         return self._roadrunner_model
        
        
     def getAntimonyModel (self):
         if self._antimony_model is None:
             if self._roadrunner_model is None:
                 raise Exception ('There is no roadrunner model to get antimony string from')
             self._antimony_model = te.sbmlToAntimony(self._roadrunner_model.getSBML())
         return self._antimony_model
     
        
     def setParametersToFit (self, parameters_to_fit):
         self.parameters_to_fit = parameters_to_fit
        
     # Do we need a get parameter fit here, not sure if there is any point?
     
     def setTimeSeriesData (self, time_series_file_name, selected_time_series_ids=None):
         """
         Load the experimental data stored in the file 'fileWithData'
         This data will be used to fit the parameters of the model
         
         Parameters
         ----------
         
         data_file_name : string
               Name of file containing time series data. Data should be arranged
               in columns, first colums representing time, remaining columns will
               be whatever timeseries data is avaialble.
               
        selected_time_series_ids : list of strings
               List of names of floating species that are the columns in the 
               time series data. If the list of names is missing then it is assumed that
               all the time series columns should be used in the fit
               
         Examples:
               f.setTimeSeriesData ('mydata.txt', ['S1', 'S2'])
               f.setTimeSeriesData ('mydata.txt')
         """
         
         # Id lists:
         # selected_time_series_ids : list of species selected by user to be used in the fit
         # model_species_ids : list of species in the mode itself
         # time_series_ids : list of species columns in the time series data file
         
         # The same variable with indices_ in front represent the equivalent index
         # in the list of model floaating species
         if type (self._roadrunner_model) != te.roadrunner.extended_roadrunner.ExtendedRoadRunner:
             raise Exception ('Model not set, please set the model first')
         
         self.model_species_ids = self._roadrunner_model.getFloatingSpeciesIds();
         
         # Open the data file and look for the header line         
         with open(time_series_file_name, 'r') as f:
              reader = csv.reader(f, delimiter=',')
              if csv.Sniffer().has_header(f.readline()):
                 f.seek(0)
                 self.time_series_ids = next(reader)
                 # Add a check that the first column is time
                 del self.time_series_ids[0] # remove time
              else:
                 #headers = self._roadrunner_model.getFloatingSpeciesIds()
                 raise Exception ('Error: This data file has no column headers')
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
        
       
     def setLowerParameterBounds (self, lowerBounds):
         """
         Sets the lower bonds for the parameters
               
         Example:
               f.setLowerParameterBounds (0.0)
         """
         self._lowerBounds = lowerBounds
        
         
     def setLowerParameterBounds (self, upperBounds):
         """
         Sets the upper bonds for the parameters
               
         Example:
               f.setUpperParameterBounds (20.0)
         """
         self._upperBounds =  upperBounds
         
         
     def fitModel(self):
         """
         Fit the model
               
         Example:
               f.fitModel ()
         """
         print ('Starting fit...')
         
         self.params = lmfit.Parameters()
         self.nParameters = len (self.parameters_to_fit)
         for k in self.parameters_to_fit:
            self.params.add(k, value=1, min=self._lowerBounds, max=self._upperBounds) # need to allow user to change bounds
            
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

    # Alternative way to start fitter
    # f = fitter (roadrunner_model=r, time_series_file_name='testdata.txt',
    #         selected_time_series_ids=['S1', 'S2', 'S3', 'S4']),
    #         parameters_to_fit=['k1', 'k2', 'k3', 'k4', 'k5']) 
    # f.fitModel()
    
    f = fitter(r)

    f.setParametersToFit (['k1', 'k2', 'k3', 'k4', 'k5'])
    f.setTimeSeriesData ('testdata.txt', ['S1', 'S2', 'S3', 'S4'])

    f.fitModel()
    print ("Fitted Parameters are:")
    print (f.getFittedParameters())
    f.plotTimeSeries()
    return f
  
        
