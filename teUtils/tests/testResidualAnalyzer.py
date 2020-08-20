# -*- coding: utf-8 -*-
"""
Created on Aug 20, 2020

@author: joseph-hellerstein
"""

from teUtils.modelFitter import ModelFitter
from teUtils.residualsAnalyzer import ResidualsAnalyzer
import tests._testHelpers as th

import matplotlib
import os
import unittest


IGNORE_TEST = False
IS_PLOT = False
OBSERVED_TS, FITTED_TS = th.getObservedFitted()
        

class TestReidualAnalyzer(unittest.TestCase):

    def setUp(self):
        self.observedTS = OBSERVED_TS
        self.fittedTS = FITTED_TS
        self.analyzer = ResidualsAnalyzer(self.observedTS, self.fittedTS)

    def testPlotResidualsOverTime(self):
        if IGNORE_TEST:
            return
        self.analyzer.plotResidualsOverTime(numCol=3, numRow=2,
              ylim=[-1.5, 1.5])

    def testPlotFittedObservedOverTime(self):
        if IGNORE_TEST:
            return
        self.analyzer.plotFittedObservedOverTime(numCol=3, numRow=2)

    def testPlotResidualsHistograms(self):
        if IGNORE_TEST:
            return
        self.analyzer.plotResidualsHistograms(ylim=[0, 5],
              xlim=[0, 6], titlePosition=[.3, .9],
              bins=10, parameters=["k1", "k2"])


if __name__ == '__main__':
    matplotlib.use('TkAgg')
    unittest.main()
