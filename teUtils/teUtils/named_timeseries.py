# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein

A NamedTimeseries is a container of multiple vairables that are obtained at the
same timepoints. Variables can be accessed by time using ("[", "]").
Various properties of the common timepoints can be accessed, such as start
and end.

Usage:
   # Create from file
   timeseries = NamedTimeseries(csv_path="myfile.txt")
   print(timeseries)  # dispaly a tabular view of the timeseries
   # NamedTimeseries can use len function
   length = len(timeseries)  # number of rows
   # Extract the numpy array values using indexing
   time_values = timeseries["time"]
   s1_values = timeseries["S1"]
   # Get the start and end times
   start_time = timeseries.start
   end_time = timeseries.end
   # Create a new time series that subsets the variables of the old one
   colnames = ["time", "S1", "S2"]
   new_timeseries = mkNamedTimeseries(colnames, timeseries[colnames])
   # Create a new timeseries that excludes time 0
   ts2 = timeseries[1:] 
   # Create a new column variable
   timeseries["S8"] = timeseries["time"]**2 + 3*timeseries["S1"]
   timeseries["S9"] = 10  # Assign a constant to all rows
"""

import collections
import copy
import csv
import numpy as np
import pandas as pd

DELIMITER = ","
TIME = "time"


################## FUNCTIONS ########################
def mkNamedTimeseries(*args):
    """
    Constructs a NamedTimeseries from different arguments.
    
    Parameters
    ----------
    args: list
        [list-str, np.ndarray]
        [NamedTimeseries]
        [str]
    """
    if len(args) == 2:
        return NamedTimeseries(colnames=args[0], array=args[1])
    if len(args) == 1:
        if isinstance(args[0], NamedTimeseries):
            return args[0]
        elif isinstance(args[0], str):
            return NamedTimeseries(csv_path=args[0])
    raise ValueError("Specification for NameTimeseries: %s"
          % str(args))
    

def arrayEquals(arr1, arr2):
    """
        Tests equality of two numpy arrays.
        
        Parameters
        ---------
        arr1: numpy array
        arr2: numpy array
        
        Returns
        -------
        boolean
    """
    if np.shape(arr1) != np.shape(arr2):
        return False
    value = sum([np.abs(v1 - v2) for v1, v2 in 
        zip(arr1.flatten(), arr2.flatten())])
    return np.isclose(value, 0)

def cleanColnames(colnames):
    """
    Fixes column names by deleting '[', ']'

    Parameters
    ----------
    colnames: list-str

    Returns
    -------
    list-str
    """
    return [s[1:-1] if s[0] == '[' else s for s in colnames]


################## CLASSES ########################
class NamedTimeseries(object):
          
    def __init__(self,
          csv_path=None,
          colnames=None, array=None,
          named_array=None,
          dataframe=None,
          timeseries=None):
        """
            Parameters
            ---------
            csv_path: str
                path to CSV file
            colnames: list-str
            array: np.ndarray
                values corresponding to colnames
            named_array: NamedArray
            dataframe: pd.DataFrame
                index: time
            timeseries: NamedTimeseries
                   
           Usage
           -----
               data = NamedTimeseries(csv_path="mydata.csv")
         
           Notes
           -----
               At one of the following most be non-None:
                 csv_path, colnames & array, dataframe, timeseries
        """
        if timeseries is not None:
            # Copy the existing object
            for k in timeseries.__dict__.keys():
                self.__setattr__(k, 
                      copy.deepcopy(timeseries.__dict__[k]))
        else:
            if csv_path is not None:
                all_colnames, self.values = self._load(csv_path)
            elif (colnames is not None) and (array is not None):
                all_colnames = colnames
                self.values = array
            elif named_array is not None:
                all_colnames = cleanColnames(named_array.colnames)
                self.values = named_array
            elif dataframe is not None:
                if dataframe.index.name == TIME:
                    df = dataframe.reset_index()
                else:
                    df = dataframe
                all_colnames = df.columns.tolist()
                self.values = df.to_numpy()
            else:
                msg = "Source should be a file path, colnames & array"
                raise ValueError(msg)
            if not TIME in all_colnames:
                raise ValueError("Must have a time column")
            self.all_colnames = []  # all column names
            self.colnames = []  # Names of non-time columns
            self._index_dct = {} # index for columns
            [self._addColname(n) for n in all_colnames]
            times = self.values[:, self._index_dct[TIME]]
            self.start = min(times)
            self.end = max(times)

    def __str__(self):
        df = self.to_dataframe()
        return str(df)

    def _addColname(self, name):
        self.all_colnames.append(name)
        self._index_dct[name] = self.all_colnames.index(name)
        self.colnames = list(self.all_colnames)
        self.colnames.remove(TIME)

    def __setitem__(self, reference, value):
        """
            Assigns a value, and optionally, creates a new columns.
            The value may be 0 or 1 dimenson for a new column.
            If reference is a list of columns, then the dimension
            must be <length of timeseries> X <number of columns in reference>
            
            Parameters
            ---------
            reference: str or str/list-str
            value: scalar, array
        """
        indices = self._getColumnIndices(reference, is_validate=False)
        if indices is None:
            # New column
            if not isinstance(reference, str):
                 raise ValueError("New column must be a string.")
            else:
                # New column is being added
                self._addColname(reference)
                num_dim = len(np.shape(value))
                num_row = np.shape(self.values)[0]
                if num_dim == 0:
                    # Make it 1-d
                    value = np.repeat(value, num_row)
                    num_dim = len(np.shape(value))
                if num_dim == 1:
                    if len(value) != num_row:
                        raise ValueError("New column has %d elements not %d"
                              % (len(value), num_row))
                    arr = np.reshape(value, (num_row, 1))
                else: 
                    msg = "New column must be a scalar or a 1-d array"
                    raise ValueError(msg)
                self.values = np.concatenate([self.values, arr],
                      axis=1)
        else:
            # Not a new column
            if isinstance(value, np.ndarray):
                values = value
            else:
                values = np.repeat(value, np.shape(self.values[:, indices]))
            self.values[:, indices] = values

    def _getColumnIndices(self, reference, is_validate=True):
        """
            Returns indices for reference.
            
            Parameters
            ---------
            variable_names: str/list-str
            is_validate: boolean
                raise an error if index doesn't exist
    
            Returns
            -------
            list-int
        """
        try:
            if isinstance(reference, str):
                indices = self._index_dct[reference]
            elif isinstance(reference, list):
                indices = [v for k, v in self._index_dct.items()
                      if k in reference]
            else:
                raise (KeyKerror)
        except KeyError:
            if is_validate:
                raise ValueError(
                      "NamedTimeseries invalid index: %s" % reference)
            else:
                indices = None
        return indices

    def __delitem__(self, reference):
        if not isinstance(reference, str):
            raise ValueError("del takes a string column names as its argument.")
        idx = self._getColumnIndices(reference)
        self.values = np.delete(self.values, idx, axis=1)
        self.colnames.remove(reference)
        self.all_colnames.remove(reference)
        self._index_dct = {n: self.all_colnames.index(n)
              for n in self.all_colnames}

    def __getitem__(self, reference):
        """
            Returns data for the requested variables or rows.
            Columns are specified by a str or list-str.
            Rows are indicated by an int, list-int, or slice.
            
            Parameters
            ---------
            variable_names: str/list-str/slice/list-int/int
    
            Returns
            -------
            np.array/NamedTimeseries
                np.ndarray for column type reference
                NamedTimeseries for row type reference
        """
        # indicate types
        is_int = False
        is_list_int = False
        is_slice = False
        is_str = False
        is_list_str = False
        if isinstance(reference, int):
            is_int = True
        elif isinstance(reference, list):
            if isinstance(reference[0], int):
                is_list_int = True
            elif isinstance(reference[0], str):
                is_list_str = True
        elif isinstance(reference, slice):
            is_slice = True
        # Process row type references
        if is_list_int:
            return NamedTimeseries(colnames=self.all_colnames,
                  array=self.values[reference, :])
        if is_int:
            return NamedTimeseries(colnames=self.all_colnames,
                  array=self.values[[reference], :])
        elif is_slice:
            all_indices = list(range(len(self)))
            indices = all_indices[reference]
            return NamedTimeseries(colnames=self.all_colnames,
                  array=self.values[indices, :])
        else:
            indices = self._getColumnIndices(reference)
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
        """
        indices = self._getColumnIndices(reference)
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

    def copy(self):
        return copy.deepcopy(self)

    def equals(self, other):
        diff = set(self.all_colnames).symmetric_difference(other.all_colnames)
        if len(diff) > 0:
            return False
        checks = []
        for col in self.all_colnames:
             checks.append(arrayEquals(self[col], other[col]))
        return all(checks)   

    def to_dataframe(self):
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

    def to_csv(self, path):
        df = self.to_dataframe()
        df = df.reset_index()
        df.to_csv(path, index=False)

    def concatenateColumns(self, *others):
        """
        Creates a NamedTimeseries that is the column concatenation of the current
        with others. Duplicate column names are resolved by adding a "_".

        Parameters
        ----------
        others: list-NamedTimeseries
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        new_ts = ts.concatenateColumns(ts1, ts2, ts3)
        """
        dfs = [self.to_dataframe()]
        colnames = list(self.colnames)
        for ts in others:
            if len(ts) != len(self):
                raise ValueError("NamedTimeseries must have the same length")
            df = ts.to_dataframe()
            for col in df.columns:
                if col in colnames:
                    new_name = "%s_" % col
                    df = df.rename(columns={col: new_name})
                    colnames.append(new_name)
            dfs.append(df)
        df_concat = pd.concat(dfs, axis=1)
        return NamedTimeseries(dataframe=df_concat)

    def concatenateRows(self, *others):
        """
        Creates a NamedTimeseries that is the concatenation of the current
        rows with others.

        Parameters
        ----------
        others: list-NamedTimeseries
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        new_ts = ts.concatenateRows(ts1, ts2, ts3)
        """
        dfs = [self.to_dataframe()]
        for ts in others:
            diff = set(self.all_colnames).symmetric_difference(ts.all_colnames)
            if len(diff) > 0:
                raise ValueError("NamedTimeseries must have the same columns.")
            df = ts.to_dataframe()
            dfs.append(df)
        df_concat = pd.concat(dfs, axis=0)
        return NamedTimeseries(dataframe=df_concat)

    def subsetColumns(self, *colnames):
        """
        Creates a NamedTimeseries consisting of a subset of columns.

        Parameters
        ----------
        colnames: list of column names
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        new_ts = ts.subsetColumns("S1", "S2")  # The new timeseries only has S1, S2
        """
        df = self.to_dataframe()
        return NamedTimeseries(dataframe=df[list(colnames)])

    def isEqualShape(self, other_ts):
        """
        Verifies that data shape and column names are the same.

        Parameters
        ----------
        other_ts: NamedTimeseries
        
        Returns
        ------
        boolean
        """
        diff = set(self.colnames).symmetric_difference(other_ts.colnames)
        if len(diff) > 0:
            return False
        return np.shape(self.values) == np.shape(other_ts.values)

    def getTimesForValue(self, column, reference):
        """
        Finds the times at which the column assumes the specified value.
        Does linear interpolation to find times.

        Parameters
        ----------
        column: str
        reference: float
            value that is searched/interpolated
        
        Returns
        ------
        float
        """
        SMALL_FRAC = 10e-6
        value_arr = self[column]
        time_arr = self[TIME]
        values = [1 if v > reference + SMALL_FRAC else -1 if v < reference - SMALL_FRAC
              else 0 for v in value_arr]
        last = 0
        times = []
        # Look for when cross 0
        for idx, value  in enumerate(values):
            if value == 0:
                # Found an exact match
                times.append(time_arr[idx])
            elif last == 0:
                # Do nothing
                pass         
            elif last == value:
                # Does not cross 0
                pass
            elif last != value:
                # Interpolate
                if last < value:
                  idx_lrg = idx
                  idx_sml = idx - 1
                else:
                  idx_lrg = idx - 1
                  idx_sml = idx
                frac = (reference - value_arr[idx_sml])/(
                      value_arr[idx_lrg] - value_arr[idx_sml])
                time_diff = time_arr[idx_lrg] - time_arr[idx_sml]
                time = time_arr[idx_sml] + frac*time_diff
                times.append(time)
            else:
                raise RuntimeError("Should not get here")
            last = value
        return times
            
            
        


