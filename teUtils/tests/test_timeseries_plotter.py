# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.named_timeseries import NamedTimeseries, mkNamedTimeseries, TIME
import teUtils.named_timeseries as named_timeseries
from teUtils.timeseries_plotter import PlotOptions, TimeseriesPlotter
from teUtils import timeseries_plotter as tp

import numpy as np
import os
import unittest
import matplotlib


IGNORE_TEST = False
IS_PLOT = False
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
NUM_ROW = tp.NUM_ROW
NUM_COL = tp.NUM_COL
        

class TesTimeseriesPlotter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)
        self.plotter = TimeseriesPlotter(is_plot=IS_PLOT)

    def testConstructor1(self):
        if IGNORE_TEST:
            return
        self.assertTrue(isinstance(self.plotter.is_plot, bool))

    def testInitializeRowColumn(self):
        if IGNORE_TEST:
            return
        def test(max_col, **kwargs):
            options = self.plotter._initializeRowColumn(self.timeseries,
                   max_col=max_col, **kwargs)
            self.assertLessEqual(max_col, options.num_row * options.num_col)
            if NUM_ROW in kwargs:
                self.assertGreaterEqual(options.num_row, kwargs[NUM_ROW])
            if NUM_COL in kwargs:
                self.assertEqual(options.num_col, kwargs[NUM_COL])
        #
        test(3, **{})
        test(3, **{NUM_COL: 3})
        test(4, **{NUM_ROW: 2})
        test(5, **{NUM_ROW: 2})

    def testPlotSingle1(self):
        if IGNORE_TEST:
            return
        self.plotter.plotTimeSingle(self.timeseries, num_col=2)
        self.plotter.plotTimeSingle(self.timeseries, num_col=4)
        self.plotter.plotTimeSingle(self.timeseries, columns=["S1", "S2", "S3"], num_row=2)
        self.plotter.plotTimeSingle(self.timeseries, num_row=2, num_col=3, ylabel="xxx")
        self.plotter.plotTimeSingle(self.timeseries, columns=["S1", "S2"])

    def mkTimeseries(self):
        ts2 = self.timeseries.copy()
        ts2[ts2.colnames] = ts2[ts2.colnames] + np.multiply(ts2[ts2.colnames], ts2[ts2.colnames])
        return ts2

    def testPlotSingle2(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, columns=["S1", "S2"])
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2)
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, num_row=2, num_col=3)

    def testPlotSingle3(self):
        if IGNORE_TEST:
            return
        self.plotter.plotTimeSingle(self.timeseries, ylabel="MISSING")

    def testPlotSingle4(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, num_row=2, num_col=3, marker2="o")

    def testPlotMultiple1(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing", 
              num_row=1, num_col=1,
              marker2="o")
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing")
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing", 
              num_row=2,
              marker2="o")
        self.plotter.plotTimeMultiple(self.timeseries, suptitle="Testing")

    def testValuePairs(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2"), ("S2", "S3"), ("S4", "S5")],
              num_col=2, num_row=2)
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2"), ("S2", "S3")], num_row=2)
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2")])
        
class TestPlotOptions(unittest.TestCase):

    def setUp(self):
        self.options = PlotOptions()

    def testSetDict(self):
        if IGNORE_TEST:
            return
        FIGSIZE = "figsize"
        FIGSIZE_VALUE = (12, 20)
        DUMMY = "dummy"
        DUMMY_VALUE = "value"
        dct = {FIGSIZE: FIGSIZE_VALUE}
        self.options.setDict(dct)
        self.assertEqual(FIGSIZE_VALUE, self.options.figsize)
        #
        dct[DUMMY] = DUMMY_VALUE
        with self.assertRaises(ValueError):
            self.options.setDict(dct)

if __name__ == '__main__':
  unittest.main()
