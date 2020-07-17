"""Data Used for a Simulation Model."""

import copy
import csv
import numpy as np

DELIMITER = ","


class ModelData(object):
          
    def __init__(self, description):
        """
        Parameters
        ---------
        description: str/ModelData
               str: file path to the CSV file
               ModelData: object to copy
               
       Examples:
            data = ModelData("mydata.csv")
        """
        ### PUBLIC FIELDS
        if isinstance(description, ModelData):
            self = copy.deepcopy(description)
        else:
            data_file_path = description
            self.last_time= None  # last time in sequence
            self.number_of_data_values = None  # length of data
            self.time_values = None  # array of time values in data
            self.variable_names = None  # Name of data columns
            self.variable_values = None  # rows: variable, column: time
            self._load(data_file_path)  # Assign values to instance variables

    def get(self, variable_names):
        """
        Returns data for the requested variables.
        
        Parameters
        ---------
        variable_names: list-str

        Returns
        -------
        np.array: variable values
        """
        # Find indices of the desired variables
        name_idxs = [self.variable_names.index(v) for v in variable_names]
        if -1 in name_idxs:
             msg = 'The columns: ' % " ".join(missing_species)
             msg += ' in the data file do not correspond to a species in the model'
             raise Exception (msg)
        # Construct the y data 
        variable_values = np.empty((0,self.number_of_data_values))
        for index in range(len(variable_names)):
            variable_values = np.vstack((variable_values, self.variable_values[:,index]))
        return variable_values
       
    def _load(self, file_path):
        """
        Load data from a CSV file.
        
        Parameters
        ----------
        
        file_path: str
              Path to the file containing time series data. Data should be arranged
              in columns, first colums representing time, remaining columns will
              be whatever timeseries data is avaialble.
        selected_variables : list of strings
              List of names of floating species that are the columns in the 
              time series data. If the list of names is missing then it is assumed that
              all the time series columns should be used in the fit

        Instance variables
        ------
        
        self.last_time: float
        self.number_of_data_values: int
        self.time_values: 
        self.variable_names: list-str
            variables in CSV data
        self.variable_values: list-str
        """
        # Open the data file and look for the header line         
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f, delimiter=DELIMITER)
                variables_str = f.readline()
                variables_str = variables_str.strip()
                self.variable_names = variables_str.split(DELIMITER)
                if all([isinstance(v, str) for v in self.variable_names]):
                    del self.variable_names[0] # remove time
                else:
                    raise ValueError('No column headers %s' % file_path)
                data_values = np.array(list(reader)).astype(float)
        except IOError:
            raise ValueError("There is a problem with the data path %s" % file_path)
        #
        self.time_values = data_values[:,0]  
        self.last_time = self.time_values[-1]
        self.number_of_data_values = len(self.time_values)
        self.variable_values = data_values[:, 1:]
