# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.named_timeseries import NamedTimeseries, mkNamedTimeseries, TIME
import teUtils.named_timeseries as named_timeseries
from teUtils.timeseries_plotter import PlotOptions, TimeseriesPlotter

import numpy as np
import os
import unittest
import matplotlib


IGNORE_TEST = False
IS_PLOT = False
matplotlib.use( 'tkagg' )
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
        

class TesTimeseriesPlotter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csv_path=TEST_DATA_PATH)
        self.plotter = TimeseriesPlotter(is_plot=IS_PLOT)

    def testConstructor1(self):
        if IGNORE_TEST:
            return
        self.assertTrue(isinstance(self.plotter.options, PlotOptions))

    def testPlotSingle1(self):
        if IGNORE_TEST:
            return
        self.plotter.plotTimeSingle(self.timeseries, num_row=2, num_col=3)
        self.plotter.plotTimeSingle(self.timeseries, columns=["S1", "S2"])
        self.plotter.plotTimeSingle(self.timeseries)

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
        options = PlotOptions()
        options.ylabel = "MISSING"
        self.plotter.plotTimeSingle(self.timeseries, options=options)

    def testPlotSingle4(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        options = PlotOptions()
        options.marker1 = 'o'
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, num_row=2, num_col=3, options=options)

    def testPlotMultiple1(self):
        if IGNORE_TEST:
            return
        options = PlotOptions()
        options.suptitle = "Testing"
        #
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, options=options)
        #
        self.plotter.plotTimeMultiple(self.timeseries, options=options)

    def testValuePairs(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2")])
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2"), ("S2", "S3")], num_row=2)
        

if __name__ == '__main__':
  unittest.main()
