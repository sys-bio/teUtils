from named_timeseries import NamedTimeseries, mkNamedTimeseries
import named_timeseries
from timeseries_plotter import PlotOptions, TimeseriesPlotter

import numpy as np
import os
import unittest


IGNORE_TEST = False
IS_PLOT = False
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
        

class TesTimeseriesPlotter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)

    def testConstructor1(self):
        if IGNORE_TEST:
            return
        pass
        

if __name__ == '__main__':
  unittest.main()
