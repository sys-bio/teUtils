"""
Abstraction for a matrix of timeseries data.
"time" references the time index.
Constructor argument may be CSV file, NamedTimeseries,
    or (names, matrix)
named_timeseries[name] returns a numpy array of type float.
Some instance variables
    colnames: list of non-time column names
    start: minimum value of the time column
    end: maximum value of the time column
Key methods
    flatten: returns a one dimensional array of
             all values in sequence by column
    __len__: called by len

Usage:
   timeseries = NamedTimeseries("myfile.txt")
   length = len(timeseries)  # number of rows
   time_values = timeseries["time"]
   cols = ["S1", "S2"]
   S1_S2_values = timeseries[cols]
   new_timeseries = NamedTimeseries((cols, S1_S2_values))
"""

import csv
import numpy as np

DELIMITER = ","
TIME = "time"


class NamedTimeseries(object):
          
    def __init__(self, source):
        """
        Parameters
        ---------
        source: str/NamedTimeseries/tupe
               str: file path to the CSV file
               NamedTimeseries: object to copy
               tuple: list-str, values array (n, #variables)
               
       Examples:
            data = NamedTimeseries("mydata.csv")
        """
        if isinstance(source, NamedTimeseries):
            # Copy the existing object
            for k in source.__dict__.keys():
                self.__setattr__(k, source.__dict__[k])
        else:
            if isinstance(source, str):
                colnames, self._value_arr = self._load(source)
            elif isinstance(source, tuple):
                colnames, self._value_arr = source
            else:
                msg = "source should be a file path, tupe or a NamedTuple. Got: %s" % str(source)
                raise ValueError(msg)
            if not TIME in colnames:
                raise ValueError("Must have a time column")
            self._index_dct = {c: colnames.index(c) for c in colnames}
            self.colnames = list(colnames)
            self.colnames.remove(TIME)
            times = self._value_arr[:, self._index_dct[TIME]]
            self.start = min(times)
            self.end = max(times)

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
        return self._value_arr[:, indices]

    def __len__(self):
       return np.shape(self._value_arr)[0]
       
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
        indices = [i for i in self._index_dct.values()
              if i != self._index_dct[TIME]]
        arr = self._value_arr[:, indices]
        return arr.flatten()
