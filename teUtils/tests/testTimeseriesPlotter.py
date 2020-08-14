# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.namedTimeseries import NamedTimeseries, mkNamedTimeseries, TIME
import teUtils.namedTimeseries as namedTimeseries
from teUtils.timeseriesPlotter import PlotOptions, TimeseriesPlotter,  \
      LayoutManagerLowerTriangular
from teUtils import timeseriesPlotter as tp

import numpy as np
import os
import unittest
import matplotlib
import matplotlib.pyplot as plt


IGNORE_TEST = False
IS_PLOT = False
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
NUM_ROW = tp.NUM_ROW
NUM_COL = tp.NUM_COL
DEFAULT_NUM_ROW = 2
DEFAULT_NUM_COL = 3
DEFAULT_NUM_PLOT = 5
        

class TestTimeseriesPlotter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(csvPath=TEST_DATA_PATH)
        self.plotter = TimeseriesPlotter(isPlot=IS_PLOT)

    def testConstructor1(self):
        if IGNORE_TEST:
            return
        self.assertTrue(isinstance(self.plotter.isPlot, bool))

    def testInitializeRowColumn(self):
        if IGNORE_TEST:
            return
        def test(maxCol, **kwargs):
            options = self.plotter._mkPlotOptionsMatrix(self.timeseries,
                   maxCol=maxCol, **kwargs)
            if NUM_ROW in kwargs:
                self.assertGreaterEqual(options.numRow, kwargs[NUM_ROW])
            if NUM_COL in kwargs:
                self.assertEqual(options.numCol, kwargs[NUM_COL])
        #
        test(3, **{})
        test(3, **{NUM_COL: 3})
        test(4, **{NUM_ROW: 2})
        test(5, **{NUM_ROW: 2})

    def testPlotSingle1(self):
        if IGNORE_TEST:
            return
        self.plotter.plotTimeSingle(self.timeseries, numCol=4)
        self.plotter.plotTimeSingle(self.timeseries, numCol=4,
              subplotWidthSpace=0.2, yticklabels=[])
        self.plotter.plotTimeSingle(self.timeseries, columns=["S1", "S2", "S3"], numRow=2)
        self.plotter.plotTimeSingle(self.timeseries, numCol=4)
        self.plotter.plotTimeSingle(self.timeseries, numCol=2)
        self.plotter.plotTimeSingle(self.timeseries, numRow=2, numCol=3, ylabel="xxx")
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
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, numRow=2, numCol=3)

    def testPlotSingle3(self):
        if IGNORE_TEST:
            return
        self.plotter.plotTimeSingle(self.timeseries, ylabel="MISSING")

    def testPlotSingle4(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeSingle(self.timeseries, timeseries2=ts2, numRow=2, numCol=3, marker2="o")

    def testPlotMultiple1(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing")
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing", 
              numRow=1, numCol=1,
              marker2="o")
        self.plotter.plotTimeMultiple(self.timeseries, timeseries2=ts2, suptitle="Testing", 
              numRow=2,
              marker2="o")
        self.plotter.plotTimeMultiple(self.timeseries, suptitle="Testing")

    def testValuePairs(self):
        if IGNORE_TEST:
            return
        ts2 = self.mkTimeseries()
        self.plotter.plotValuePairs(self.timeseries, 
              [("S1", "S2"), ("S2", "S3"), ("S4", "S5")],
              numCol=2, numRow=2)
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2"), ("S2", "S3")], numRow=2)
        self.plotter.plotValuePairs(self.timeseries, [("S1", "S2")])

    def testPlotHistograms(self):
        if IGNORE_TEST:
            return
        self.plotter.plotHistograms(self.timeseries, numCol=2)

    def testPlotValuePairsBug(self):
        if IGNORE_TEST:
            return
        self.plotter.plotValuePairs(self.timeseries,
              pairs=[("S1", "S2"), ("S1", "S6"), ("S2", "S3")], numCol=3)
        
        
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
        
class TestLayoutManagerLowerTriangular(unittest.TestCase):

    def setUp(self):
        options = PlotOptions()
        options.numRow = 2*DEFAULT_NUM_ROW
        options.numCol = 3*DEFAULT_NUM_COL

    def testSetAxes(self):
        if IGNORE_TEST:
            return
        options = PlotOptions()
        options.numCol = 4
        options.numRow = 4
        layout = LayoutManagerLowerTriangular(options, DEFAULT_NUM_PLOT)
        _, axes, _ = layout._setAxes()
        corners = [a.get_position().corners() for a in axes]
        self.assertEqual(corners[0][0][0], corners[1][0][0])
        if IS_PLOT:
            plt.show()


if __name__ == '__main__':
    matplotlib.use('TkAgg')
    unittest.main()