from named_timeseries import NamedTimeseries

import numpy as np
import os
import unittest


IGNORE_TEST = True
IS_PLOT = True
VARIABLE_NAMES = ["S%d" % d for d in range(1, 7)]
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
TEST_BAD_DATA_PATH = os.path.join(DIR, "missing.txt")
LENGTH = 30
TIME = "time"
        

class TestNamedTimeseries(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)

    def testConstructor(self):
        # TESTING
        self.assertGreater(len(self.timeseries._value_arr), 0)
        # colnames doesn't include TIME
        self.assertEqual(len(self.timeseries.colnames),
               np.shape(self.timeseries._value_arr)[1] - 1)
        #
        cols = [TIME, "S1", "S2"]
        new_values = self.timeseries[cols]
        new_timeseries = NamedTimeseries((cols, new_values))
        for name in cols:
            self.assertTrue(np.isclose(sum(new_timeseries[name]
                  - self.timeseries[name]), 0))

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
              zip(values, self.timeseries._value_arr)])
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
        for variable in ["_value_arr"]:
            checkMatrix(variable)

    def testFlattenValues(self):
        if IGNORE_TEST:
            return
        values = self.timeseries.flattenValues()
        self.assertTrue(np.isclose(sum(values - 
              self.timeseries._value_arr[:, 1:].flatten()), 0))
        

if __name__ == '__main__':
  unittest.main()
