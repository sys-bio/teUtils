"""
A NamedTimeseries is a container of multiple vairables that are obtained at the
same timepoints. Variables can be accessed by time using ("[", "]").
Various properties of the common timepoints can be accessed, such as start
and end.

Usage:
   # Create from file
   timeseries = NamedTimeseries("myfile.txt")
   # NamedTimeseries can use len function
   length = len(timeseries)  # number of rows
   # Extract the time values using indexing
   time_values = timeseries["time"]
   # Get the start and end times
   start_time = timeseries.start
   end_time = timeseries.end
   # Create a new time series that subsets the old one
   colnames = ["time", "S1", "S2"]
   new_timeseries = mkNamedTimeseries(colnames, timeseries[colnames])
   # Create a new timeseries with a subset of times
   array = timeseries.selectTime(lambda t: t > 2)
   new_timeseries = mkNamedTimeseries(self.all_colnames, timeseries.values)
"""

import collections
import copy
import csv
import numpy as np
import pandas as pd

DELIMITER = ","
TIME = "time"


################## FUNCTIONS ########################
def mkNamedTimeseries(colnames, array):
    args = ConstructorArguments(colnames=colnames, array=array)
    return NamedTimeseries(args)


################## CLASSES ########################
ConstructorArguments = collections.namedtuple(
      "ConstructorArguments", "colnames array")

######
class NamedTimeseries(object):
          
    def __init__(self, source):
        """
        Parameters
        ---------
        source: str/NamedTimeseries/ConstructorArgument/DataFrame
               str: file path to the CSV file
               NamedTimeseries: object to copy
               
       Examples:
            data = NamedTimeseries("mydata.csv")
        """
        if isinstance(source, NamedTimeseries):
            # Copy the existing object
            for k in source.__dict__.keys():
                self.__setattr__(k, 
                      copy.deepcopy(source.__dict__[k]))
        else:
            if isinstance(source, str):
                # Names of all columns and array of all values
                self.all_colnames, self.values = self._load(source)
            elif isinstance(source, ConstructorArguments):
                self.all_colnames = source.colnames
                self.values = source.array
            elif isinstance(source, pd.DataFrame):
                df = source.reset_index()
                self.all_colnames = df.columns.tolist()
                self.values = df.to_numpy()
            else:
                msg = "source should be a file path, tupe or a NamedTuple. Got: %s" % str(source)
                raise ValueError(msg)
            if not TIME in self.all_colnames:
                raise ValueError("Must have a time column")
            self._index_dct = {c: self.all_colnames.index(c)
                  for c in self.all_colnames}
            self.colnames = list(self.all_colnames)
            self.colnames.remove(TIME)  # Value column names
            times = self.values[:, self._index_dct[TIME]]
            self.start = min(times)
            self.end = max(times)

    def __str__(self):
        df = self.to_pandas()
        return str(df.head())

    def __getitem__(self, reference):
        """
        Returns data for the requested variables.
        
        Parameters
        ---------
        variable_names: str/list-str

        Returns
        -------
        np.array: variable values
        """
        if isinstance(reference, str):
            indices = self._index_dct[reference]
        elif isinstance(reference, list):
            indices = [v for k, v in self._index_dct.items()
                  if k in reference]
        else:
            raise ValueError("Reference not found: %s" % reference)
        return self.values[:, indices]

    def __len__(self):
       return np.shape(self.values)[0]
       
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

        Returns
        ------
        list-str, array
            list-str: colnames
            array: values
        """
        # Open the data file and look for the header line         
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f, delimiter=DELIMITER)
                variables_str = f.readline()
                variables_str = variables_str.strip()
                names = variables_str.split(DELIMITER)
                values = np.array(list(reader)).astype(float)
        except IOError:
            raise ValueError("There is a problem with the data path %s" % file_path)
        if not all([isinstance(v, str) for v in names]):
            raise ValueError('No column headers for file: %s' % file_path)
        #
        return names, values

    def flattenValues(self):
        """
        Creates a one dimensional array of values
        
        Returns
        ------
        array
        """
        indices = [self._index_dct[c] for c in self.colnames]
        arr = self.values[:, indices]
        return arr.flatten()

    def selectTimes(self, selector_function):
        """
            Selects a subset of rows based on time values by using
            a boolean valued selector function.
            
            Parameters
            ----------
     
            selector_function: Function
                argument: time value
                returns: boolean
            
            Returns
            ------
            array
        """
        row_indices = [i for i, t in enumerate(self[TIME])
              if selector_function(t)]
        col_indices = [i for i in self._index_dct.values()
              if self._index_dct[TIME] != i]
        array = self.values[row_indices, :]
        return array[:, col_indices]

    def to_pandas(self):
        """
            Creates a pandas dataframe from the NamedTimeseries.
            
            Returns
            ------
            pd.DataFrame
                columns: self.colnames
                index: Time
        """
        dct = {c: self.values[:, i] for c, i in self._index_dct.items()}
        df = pd.DataFrame(dct)
        return df.set_index(TIME)
