from named_timeseries import NamedTimeseries
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
LENGTH = 30
TIME = "time"
        

class TestNamedTimeseries(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)

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
        args = named_timeseries.ConstructorArguments(
              colnames=COLNAMES, array=self.timeseries[COLNAMES])
        new_timeseries = NamedTimeseries(args)
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
            timeseries = NamedTimeseries(TEST_BAD_DATA_PATH)

    def testCopyExisting(self):
        if IGNORE_TEST:
            return
        timeseries = NamedTimeseries(self.timeseries)
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
        df = self.timeseries.to_pandas()
        timeseries = NamedTimeseries(df)
        diff = set(df.columns).symmetric_difference(timeseries.colnames)
        self.assertEqual(len(diff), 0)
        total = sum(timeseries.values.flatten() - self.timeseries.values.flatten())
        self.assertTrue(np.isclose(total, 0))
        

if __name__ == '__main__':
  unittest.main()
