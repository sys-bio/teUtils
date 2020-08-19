# -*- coding: utf-8 -*-
"""
Created on Aug 19, 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils._modelFitterReport import ModelFitterReport
from teUtils.namedTimeseries import NamedTimeseries

import numpy as np
import os
import unittest


IGNORE_TEST = True
IS_PLOT = True
PARAMETER_DCT = {
      "k1": 1,
      "k2": 2,
      "k3": 3,
      "k4": 4,
      "k5": 5,
     }
VARIABLE_NAMES = ["S%d" % d for d in range(1, 7)]
parametersStrs = ["%s=%d" % (k, v) for k,v 
      in PARAMETER_DCT.items()]
parametersStr = "; ".join(parametersStrs)
COLUMNS = ["S%d" % d for d in range(1, 7)]
ANTIMONY_MODEL_BENCHMARK = """
# Reactions   
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
# Species initializations     
    S1 = 10; S2 = 0;
    k1 = 1; k2 = 2
"""
ANTIMONY_MODEL = """
# Reactions   
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
    J3: S3 -> S4; k3*S3
    J4: S4 -> S5; k4*S4
    J5: S5 -> S6; k5*S5;
# Species initializations     
    S1 = 10; S2 = 0; S3 = 0; S4 = 0; S5 = 0; S6 = 0;
# Parameters:      
   %s
""" % parametersStr
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
BENCHMARK_PATH = os.path.join(DIR, "groundtruth_2_step_0_1.txt")
BENCHMARK1_TIME = 30 # Actual is 20 sec
        

class TestModelFitter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)
        self.fitter = ModelFitterReport(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        self.fitter.fitModel()
        self.fitter.bootstrap()

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
