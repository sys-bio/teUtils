# -*- coding: utf-8 -*-
"""
Created on Aug 19, 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils._modelFitterReport import ModelFitterReport
from teUtils.namedTimeseries import NamedTimeseries
from tests import _testHelpers as th

import numpy as np
import os
import unittest


IGNORE_TEST = True
IS_PLOT = True
TIMESERIES = th.getTimeseries()
FITTER = th.getFitter(cls=ModelFitterReport, isPlot=IS_PLOT)
FITTER.fitModel()
FITTER.bootstrap(numIteration=100)

class TestModelFitter(unittest.TestCase):

    def setUp(self):
        self.timeseries = TIMESERIES
        self.fitter = FITTER

    def testReportFit(self):
        if IGNORE_TEST:
            return
        result = fitter1.reportFit()

    def testBoostrapReport(self):
        if IGNORE_TEST:
            return
        self.fitter.reportBootstrap()


if __name__ == '__main__':
    unittest.main()
