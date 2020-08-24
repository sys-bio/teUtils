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
   timeseries = NamedTimeseries(csvPath="myfile.txt")
   print(timeseries)  # dispaly a tabular view of the timeseries
   # NamedTimeseries can use len function
   length = len(timeseries)  # number of rows
   # Extract the numpy array values using indexing
   timeValues = timeseries["time"]
   s1Values = timeseries["S1"]
   # Get the start and end times
   startTime = timeseries.start
   endTime = timeseries.end
   # Create a new time series that subsets the variables of the old one
   colnames = ["time", "S1", "S2"]
   newTimeseries = mkNamedTimeseries(colnames, timeseries[colnames])
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
            return NamedTimeseries(csvPath=args[0])
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
          csvPath=None,
          colnames=None, array=None,
          namedArray=None,
          dataframe=None,
          timeseries=None):
        """
        Parameters
        ---------
        csvPath: str
            path to CSV file
        colnames: list-str
        array: np.ndarray
            values corresponding to colnames
        namedArray: NamedArray
        dataframe: pd.DataFrame
            index: time
        timeseries: NamedTimeseries
               
       Usage
       -----
           data = NamedTimeseries(csvPath="mydata.csv")
     
       Notes
       -----
           At one of the following most be non-None:
             csvPath, colnames & array, dataframe, timeseries
        """
        if timeseries is not None:
            # Copy the existing object
            for k in timeseries.__dict__.keys():
                self.__setattr__(k, 
                      copy.deepcopy(timeseries.__dict__[k]))
        else:
            if csvPath is not None:
                allColnames, self.values = self._load(csvPath)
            elif (colnames is not None) and (array is not None):
                allColnames = colnames
                self.values = array
            elif namedArray is not None:
                allColnames = cleanColnames(namedArray.colnames)
                self.values = namedArray
            elif dataframe is not None:
                if dataframe.index.name == TIME:
                    df = dataframe.reset_index()
                else:
                    df = dataframe
                allColnames = df.columns.tolist()
                self.values = df.to_numpy()
            else:
                msg = "Source should be a file path, colnames & array"
                raise ValueError(msg)
            timeIdxs = [i for i, c in enumerate(allColnames) if c.lower() == TIME]
            if len(timeIdxs) != 1:
                raise ValueError("Must have exactly one time column")
            allColnames[timeIdxs[0]] = TIME
            self.allColnames = []  # all column names
            self.colnames = []  # Names of non-time columns
            self._indexDct = {} # index for columns
            [self._addColname(n) for n in allColnames]
            times = self.values[:, self._indexDct[TIME]]
            self.start = min(times)
            self.end = max(times)

    def __str__(self):
        df = self.to_dataframe()
        return str(df)

    def _addColname(self, name):
        self.allColnames.append(name)
        self._indexDct[name] = self.allColnames.index(name)
        self.colnames = list(self.allColnames)
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
        indices = self._getColumnIndices(reference, isValidate=False)
        if indices is None:
            # New column
            if not isinstance(reference, str):
                 raise ValueError("New column must be a string.")
            else:
                # New column is being added
                self._addColname(reference)
                numDim = len(np.shape(value))
                numRow = np.shape(self.values)[0]
                if numDim == 0:
                    # Make it 1-d
                    value = np.repeat(value, numRow)
                    numDim = len(np.shape(value))
                if numDim == 1:
                    if len(value) != numRow:
                        raise ValueError("New column has %d elements not %d"
                              % (len(value), numRow))
                    arr = np.reshape(value, (numRow, 1))
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

    def _getColumnIndices(self, reference, isValidate=True):
        """
            Returns indices for reference.
            
            Parameters
            ---------
            reference: str/list-str
            isValidate: boolean
                raise an error if index doesn't exist
    
            Returns
            -------
            list-int
        """
        try:
            if isinstance(reference, str):
                indices = self._indexDct[reference]
            elif isinstance(reference, list):
                indices = [v for k, v in self._indexDct.items()
                      if k in reference]
            else:
                raise (KeyKerror)
        except KeyError:
            if isValidate:
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
        self.allColnames.remove(reference)
        self._indexDct = {n: self.allColnames.index(n)
              for n in self.allColnames}

    def __getitem__(self, reference):
        """
        Returns data for the requested variables or rows.
        Columns are specified by a str or list-str.
        Rows are indicated by an int, list-int, or slice.
        
        Parameters
        ---------
        reference: str/list-str/slice/list-int/int

        Returns
        -------
        np.array/NamedTimeseries
            np.ndarray for column type reference
            NamedTimeseries for row type reference
        """
        def handleStr(reference):
            indices = self._getColumnIndices(reference)
            return self.values[:, indices]
        # indicate types
        isInt = False
        isListInt = False
        isSlice = False
        isStr = False
        isListStr = False
        if isinstance(reference, str):
            isStr = True
        elif isinstance(reference, list):
            if isinstance(reference[0], str):
                isListStr = True
            elif isinstance(reference[0], int):
                isListInt = True
        elif isinstance(reference, int):
            isInt = True
        elif isinstance(reference, slice):
            isSlice = True
        # Process row type references
        if isStr:
            if reference.lower() == TIME:
                reference = TIME
            return handleStr(reference)
        if isListStr:
            timeStrs = [c for c in reference if c.lower() == TIME]
            if len(timeStrs) == 1:
                ref = timeStrs[0]
                idx = reference.index(ref)
                reference.insert(idx, TIME)
                reference.remove(ref)
            elif len(timeStrs) == 0:
                pass
            else:
                raise ValueError("Reference to multiple different time columns.")
            return handleStr(reference)
        if isListInt:
            return NamedTimeseries(colnames=self.allColnames,
                  array=self.values[reference, :])
        if isInt:
            return NamedTimeseries(colnames=self.allColnames,
                  array=self.values[[reference], :])
        if isSlice:
            allIndices = list(range(len(self)))
            indices = allIndices[reference]
            return NamedTimeseries(colnames=self.allColnames,
                  array=self.values[indices, :])
            indices = self._getColumnIndices(reference)
        #
        raise ValueError("Invalid reference to NamedTimeseries.")

    def __len__(self):
       return np.shape(self.values)[0]
       
    def _load(self, filePath):
        """
        Load data from a CSV file.
        
        Parameters
        ----------
        
        filePath: str
              Path to the file containing time series data. Data should be arranged
              in columns, first colums representing time, remaining columns will
              be whatever timeseries data is avaialble.
        selectedVariables : list of strings
        """
        indices = self._getColumnIndices(reference)
        return self.values[:, indices]

    def __len__(self):
       return np.shape(self.values)[0]
       
    def _load(self, filePath):
        """
        Load data from a CSV file.
        
        Parameters
        ----------
        
        filePath: str
              Path to the file containing time series data. Data should be arranged
              in columns, first colums representing time, remaining columns will
              be whatever timeseries data is avaialble.
        selectedVariables : list of strings
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
            with open(filePath, 'r') as f:
                reader = csv.reader(f, delimiter=DELIMITER)
                variablesStr = f.readline()
                variablesStr = variablesStr.strip()
                names = variablesStr.split(DELIMITER)
                values = np.array(list(reader)).astype(float)
        except IOError:
            raise ValueError("There is a problem with the data path %s" % filePath)
        if not all([isinstance(v, str) for v in names]):
            raise ValueError('No column headers for file: %s' % filePath)
        #
        return names, values

    def flatten(self):
        """
        Creates a one dimensional array of values
        
        Returns
        ------
        array
        """
        indices = [self._indexDct[c] for c in self.colnames]
        arr = self.values[:, indices]
        return arr.flatten()

    def selectTimes(self, selectorFunction):
        """
            Selects a subset of rows based on time values by using
            a boolean valued selector function.
            
            Parameters
            ----------
     
            selectorFunction: Function
                argument: time value
                returns: boolean
            
            Returns
            ------
            array
        """
        rowIdxs = [i for i, t in enumerate(self[TIME])
              if selectorFunction(t)]
        colIdxs = [i for i in self._indexDct.values()
              if self._indexDct[TIME] != i]
        array = self.values[rowIdxs, :]
        return array[:, colIdxs]

    def copy(self):
        return copy.deepcopy(self)

    def equals(self, other):
        diff = set(self.allColnames).symmetric_difference(other.allColnames)
        if len(diff) > 0:
            return False
        checks = []
        for col in self.allColnames:
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
        dct = {c: self.values[:, i] for c, i in self._indexDct.items()}
        df = pd.DataFrame(dct)
        return df.set_index(TIME)

    def to_csv(self, path):
        df = self.to_dataframe()
        df = df.reset_index()
        df.to_csv(path, index=False)

    def _getTimeseriesOrList(self, others):
        if isinstance(others, NamedTimeseries):
            others = [others]
        return others

    def concatenateColumns(self, others):
        """
        Creates a NamedTimeseries that is the column concatenation of the current
        with others. Duplicate column names are resolved by adding a "_".

        Parameters
        ----------
        others: single or list-NamedTimeseries
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        newTS = ts.concatenateColumns(ts1, ts2, ts3)
        """
        others = self._getTimeseriesOrList(others)
        dfs = [self.to_dataframe()]
        colnames = list(self.colnames)
        for ts in others:
            if len(ts) != len(self):
                raise ValueError("NamedTimeseries must have the same length")
            df = ts.to_dataframe()
            for col in df.columns:
                if col in colnames:
                    newName = "%s_" % col
                    df = df.rename(columns={col: newName})
                    colnames.append(newName)
            dfs.append(df)
        concatDF = pd.concat(dfs, axis=1)
        return NamedTimeseries(dataframe=concatDF)

    def concatenateRows(self, others):
        """
        Creates a NamedTimeseries that is the concatenation of the current
        rows with others.

        Parameters
        ----------
        others: single or list-NamedTimeseries
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        newTS = ts.concatenateRows(ts1, ts2, ts3)
        """
        others = self._getTimeseriesOrList(others)
        dfs = [self.to_dataframe()]
        for ts in others:
            diff = set(self.allColnames).symmetric_difference(ts.allColnames)
            if len(diff) > 0:
                raise ValueError("NamedTimeseries must have the same columns.")
            df = ts.to_dataframe()
            dfs.append(df)
        concatDF = pd.concat(dfs, axis=0)
        return NamedTimeseries(dataframe=concatDF)

    def _getStringOrListstring(self, arg):
        if isinstance(arg, str):
            return [arg]
        else:
            return arg

    def subsetColumns(self, colnames):
        """
        Creates a NamedTimeseries consisting of a subset of columns.

        Parameters
        ----------
        colnames: single column name or list of column names
        
        Returns
        ------
        NamedTimeseries

        Usage
        -----
        newTS = ts.subsetColumns("S1", "S2")  # The new timeseries only has S1, S2
        """
        colnames = self._getStringOrListstring(colnames)
        df = self.to_dataframe()
        return NamedTimeseries(dataframe=df[colnames])

    def isEqualShape(self, otherTS):
        """
        Verifies that data shape and column names are the same.

        Parameters
        ----------
        otherTS: NamedTimeseries
        
        Returns
        ------
        boolean
        """
        diff = set(self.colnames).symmetric_difference(otherTS.colnames)
        if len(diff) > 0:
            return False
        return np.shape(self.values) == np.shape(otherTS.values)

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
        valueArr = self[column]
        timeArr = self[TIME]
        values = [1 if v > reference + SMALL_FRAC else -1 if v < reference - SMALL_FRAC
              else 0 for v in valueArr]
        last = 0
        times = []
        # Look for when cross 0
        for idx, value  in enumerate(values):
            if value == 0:
                # Found an exact match
                times.append(timeArr[idx])
            elif last == 0:
                # Do nothing
                pass         
            elif last == value:
                # Does not cross 0
                pass
            elif last != value:
                # Interpolate
                if last < value:
                  lrgIdx = idx
                  smlIdx = idx - 1
                else:
                  lrgIdx = idx - 1
                  smlIdx = idx
                frac = (reference - valueArr[smlIdx])/(
                      valueArr[lrgIdx] - valueArr[smlIdx])
                timeDiff = timeArr[lrgIdx] - timeArr[smlIdx]
                time = timeArr[smlIdx] + frac*timeDiff
                times.append(time)
            else:
                raise RuntimeError("Should not get here")
            last = value
        return times
