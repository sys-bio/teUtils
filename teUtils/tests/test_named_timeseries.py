# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.named_timeseries import NamedTimeseries, mkNamedTimeseries
import teUtils.named_timeseries as named_timeseries

import numpy as np
import os
import tellurium as te
import unittest


IGNORE_TEST = False
IS_PLOT = False
VARIABLE_NAMES = ["S%d" % d for d in range(1, 7)]
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
TEST_BAD_DATA_PATH = os.path.join(DIR, "missing.txt")
TEMP_FILE = os.path.join(DIR, "temp.csv")
LENGTH = 30
TIME = "time"
ANTIMONY_MODEL = """
# Reactions   
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
    J3: S3 -> S4; k3*S3
    J4: S4 -> S5; k4*S4
    J5: S5 -> S6; k5*S5;
# Species initializations     
    S1 = 10;
    k1 = 1; k2 = 2; k3 = 3; k4 = 4; k5 = 5;
    S1 = 0; S2 = 0; S3 = 0; S4 = 0; S5 = 0; S6 = 0;
"""


class TestNamedTimeseries(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)
        self.model = te.loada(ANTIMONY_MODEL)

    def tearDown(self):
        if os.path.isfile(TEMP_FILE):
            os.remove(TEMP_FILE)

    def testConstructor1(self):
        if IGNORE_TEST:
            return
        self.assertGreater(len(self.timeseries.values), 0)
        # colnames doesn't include TIME
        self.assertEqual(len(self.timeseries.colnames),
               np.shape(self.timeseries.values)[1] - 1)

    def testConstructor2(self):
        if IGNORE_TEST:
            return
        COLNAMES = [TIME, "S1", "S2"]
        def test(timeseries):
            for name in COLNAMES:
                self.assertTrue(np.isclose(sum(timeseries[name]
                      - self.timeseries[name]), 0))
        #
        new_timeseries = NamedTimeseries(colnames=COLNAMES,
              array=self.timeseries[COLNAMES])
        test(new_timeseries)

    def testConstructorNamedArray(self):
        if IGNORE_TEST:
            return
        named_array = self.model.simulate(0, 100, 30)
        ts = NamedTimeseries(named_array=named_array)
        self.assertTrue(named_timeseries.arrayEquals(named_array.flatten(),
              ts.values.flatten()))

    def testSizeof(self):
        if IGNORE_TEST:
            return
        self.assertEqual(len(self.timeseries), LENGTH)

    def testGetitem(self):
        if IGNORE_TEST:
            return
        times = self.timeseries[TIME]
        self.assertEqual(len(times), len(self.timeseries))
        self.assertEqual(min(times), self.timeseries.start)
        self.assertEqual(max(times), self.timeseries.end)
        # Get multiple values at once
        values = self.timeseries[self.timeseries.colnames]
        trues = np.array([v1 == v2 for v1, v2 in 
              zip(values, self.timeseries.values[:, 1:])])
        self.assertTrue(all(trues.flatten()))

    def testMissingData(self):
        if IGNORE_TEST:
            return
        with self.assertRaises(ValueError):
            timeseries = NamedTimeseries(csv_path=TEST_BAD_DATA_PATH)

    def testCopyExisting(self):
        if IGNORE_TEST:
            return
        timeseries = NamedTimeseries(timeseries=self.timeseries)
        #
        def checkVector(attribute):
            length = len(self.timeseries.__getattribute__(attribute))
            trues = [timeseries.__getattribute__(attribute)[k]==
                  self.timeseries.__getattribute__(attribute)[k]
                  for k in range(length)]
            self.assertTrue(all(trues))
        def checkMatrix(attribute):
            trues = []
            for row_idx, row in enumerate(
                  timeseries.__getattribute__(attribute)):
                for col_idx, val in enumerate(row):
                    trues.append(val == 
                          self.timeseries.__getattribute__(attribute)[
                          row_idx, col_idx])
            self.assertTrue(all(trues))
        #
        for variable in ["start", "end"]:
            self.assertEqual(timeseries.__getattribute__(variable),
                  self.timeseries.__getattribute__(variable))
        for variable in ["colnames"]:
            checkVector(variable)
        for variable in ["values"]:
            checkMatrix(variable)

    def testFlattenValues(self):
        if IGNORE_TEST:
            return
        values = self.timeseries.flattenValues()
        self.assertTrue(np.isclose(sum(values - 
              self.timeseries.values[:, 1:].flatten()), 0))

    def testSelectTimes(self):
        if IGNORE_TEST:
            return
        selector_function = lambda t: t > 2
        array = self.timeseries.selectTimes(selector_function)
        self.assertLess(len(array), len(self.timeseries))

    def testMkNamedTimeseries(self):
        if IGNORE_TEST:
            return
        # Create a new time series that subsets the old one
        colnames = ["time", "S1", "S2"]
        new_timeseries = named_timeseries.mkNamedTimeseries(
              colnames, self.timeseries[colnames])
        self.assertEqual(len(self.timeseries), len(new_timeseries))
        # Create a new timeseries with a subset of times
        array = self.timeseries.selectTimes(lambda t: t > 2)
        new_timeseries = named_timeseries.mkNamedTimeseries(
              self.timeseries.all_colnames, array)
        self.assertGreater(len(self.timeseries), len(new_timeseries))
        #
        ts = mkNamedTimeseries(self.timeseries)
        self.assertTrue(self.timeseries.equals(ts))
        #
        ts = mkNamedTimeseries(TEST_DATA_PATH)
        self.assertTrue(self.timeseries.equals(ts))
        #
        with self.assertRaises(ValueError):
            ts = mkNamedTimeseries(3)
       

    def testToPandas(self):
        if IGNORE_TEST:
            return
        df = self.timeseries.to_dataframe()
        timeseries = NamedTimeseries(dataframe=df)
        diff = set(df.columns).symmetric_difference(timeseries.colnames)
        self.assertEqual(len(diff), 0)
        total = sum(timeseries.values.flatten() - self.timeseries.values.flatten())
        self.assertTrue(np.isclose(total, 0))

    def testArrayEquals(self):
        if IGNORE_TEST:
            return
        arr1 = np.array([1, 2, 3, 4])
        arr1 = np.reshape(arr1, (2, 2))
        self.assertTrue(named_timeseries.arrayEquals(arr1, arr1))
        arr2 = 1.0001*arr1
        self.assertFalse(named_timeseries.arrayEquals(arr1, arr2))


    def testEquals(self):
        if IGNORE_TEST:
            return
        self.assertTrue(self.timeseries.equals(self.timeseries))
        new_timeseries = self.timeseries.copy()
        new_timeseries["S1"] = -1
        self.assertFalse(self.timeseries.equals(new_timeseries))
 
    def testCopy(self):
        if IGNORE_TEST:
            return
        ts2 = self.timeseries.copy()
        self.assertTrue(self.timeseries.equals(ts2))

    def testSetitem(self):
        if IGNORE_TEST:
            return
        self.timeseries["S1"] = self.timeseries["S2"]
        self.assertTrue(named_timeseries.arrayEquals(
              self.timeseries["S1"], self.timeseries["S2"]))
        value = -20
        self.timeseries["S19"] = value
        self.assertEqual(self.timeseries["S19"].sum(), len(self.timeseries)*value)

    def testGetitemRows(self):
        if IGNORE_TEST:
            return
        start = 1
        stop = 3
        ts1 = self.timeseries[start:stop]
        self.assertTrue(isinstance(ts1, NamedTimeseries))
        self.assertEqual(len(ts1), stop - start)
        #
        ts2 = self.timeseries[[1, 2]]
        self.assertTrue(ts1.equals(ts2))
        #
        ts3 = self.timeseries[1]
        self.assertEqual(np.shape(ts3.values), (1, len(ts2.all_colnames)))

    def testExamples(self):
        if IGNORE_TEST:
            return
        # Create from file
        timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)
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

    def testDelitem(self):
        if IGNORE_TEST:
            return
        ts1 = self.timeseries.copy()
        del ts1["S1"]
        stg = str(ts1)
        self.assertEqual(len(ts1), len(self.timeseries))
        self.assertEqual(len(ts1.colnames) +1, len(self.timeseries.colnames))

    def testToCsv(self):
        if IGNORE_TEST:
            return
        self.timeseries.to_csv(TEMP_FILE)
        self.assertTrue(os.path.isfile(TEMP_FILE))

    def testConcatenateColumns(self):
        if IGNORE_TEST:
            return
        ts = self.timeseries.concatenateColumns(self.timeseries)
        new_names = ["%s_" % c for c in self.timeseries.colnames]
        self.assertTrue(named_timeseries.arrayEquals(ts[new_names],
              self.timeseries[self.timeseries.colnames]))
        self.assertEquals(len(ts), len(self.timeseries))
        self.assertTrue(named_timeseries.arrayEquals(ts[TIME],
              self.timeseries[TIME]))
        #
        ts = self.timeseries.concatenateColumns(self.timeseries, self.timeseries)
        self.assertEqual(3*len(self.timeseries.colnames), len(ts.colnames))

    def testConcatenateRows(self):
        if IGNORE_TEST:
            return
        ts = self.timeseries.concatenateRows(self.timeseries)
        diff = set(ts.colnames).symmetric_difference(self.timeseries.colnames)
        self.assertEqual(len(diff), 0)
        length = len(self.timeseries)
        ts1 = ts[length:]
        self.assertTrue(self.timeseries.equals(ts1))
        #
        ts = self.timeseries.concatenateRows(self.timeseries, self.timeseries)
        self.assertEqual(3*len(self.timeseries), len(ts))

    def testSubsetColumns(self):
        if IGNORE_TEST:
            return
        ts = self.timeseries.concatenateColumns(self.timeseries)
        ts1 = ts.subsetColumns(*self.timeseries.colnames)
        self.assertTrue(self.timeseries.equals(ts1))
   

if __name__ == '__main__':
  unittest.main()
