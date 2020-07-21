from named_timeseries import NamedTimeseries, mkNamedTimeseries
import named_timeseries

import numpy as np
import os
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
        

class TestNamedTimeseries(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)

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

    def testConstructor3(self):
        if IGNORE_TEST:
            return

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
        self.assertEquals(self.timeseries["S19"].sum(), len(self.timeseries)*value)

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
   

        

if __name__ == '__main__':
  unittest.main()
