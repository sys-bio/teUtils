from model_data import ModelData

import numpy as np
import os
import unittest


IGNORE_TEST = False
IS_PLOT = False
VARIABLE_NAMES = ["S%d" % d for d in range(1, 7)]
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "testdata.txt")
TEST_BAD_DATA_PATH = os.path.join(DIR, "missing.txt")
        

class TestModelData(unittest.TestCase):

    def setUp(self):
        self.data = ModelData(TEST_DATA_PATH)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertGreater(len(self.data.time_values), 0)
        self.assertEqual(len(self.data.variable_values), len(self.data.time_values))
        self.assertEqual(len(self.data.variable_names),
            np.shape(self.data.variable_values)[1])

    def testMissingData(self):
        if IGNORE_TEST:
            return
        with self.assertRaises(ValueError):
            data = ModelData(TEST_BAD_DATA_PATH)

    def testCopyExisting(self):
        if IGNORE_TEST:
            return
        model_data = ModelData(self.data)
        #
        def checkVector(attribute):
            length = len(self.data.__getattribute__(attribute))
            trues = [model_data.__getattribute__(attribute)[k]==
                  self.data.__getattribute__(attribute)[k]
                  for k in range(length)]
            self.assertTrue(all(trues))
        def checkMatrix(attribute):
            trues = []
            for row_idx, row in enumerate(
                  model_data.__getattribute__(attribute)):
                for col_idx, val in enumerate(row):
                    trues.append(val == 
                          self.data.__getattribute__(attribute)[
                          row_idx, col_idx])
            self.assertTrue(all(trues))
        #
        for variable in ["last_time", "number_of_data_values"]:
            self.assertEqual(model_data.__getattribute__(variable),
                  self.data.__getattribute__(variable))
        for variable in ["variable_names", "time_values"]:
            checkVector(variable)
        for variable in ["variable_values"]:
            checkMatrix(variable)

    def testGet(self):
        if IGNORE_TEST:
            return
        for name in VARIABLE_NAMES:
            values = self.data.get([name])
            self.assertEqual(np.shape(values), (1, self.data.number_of_data_values))
        #
        SIZE = 2
        values = self.data.get(VARIABLE_NAMES[0:SIZE])
        self.assertEqual(np.shape(values), (SIZE, self.data.number_of_data_values))
        

if __name__ == '__main__':
  unittest.main()
