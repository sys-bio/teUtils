# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.model_fitter import ModelFitter
from teUtils import model_fitter
from teUtils.named_timeseries import NamedTimeseries, TIME

import matplotlib
import numpy as np
import os
import tellurium
import time
import unittest


IGNORE_TEST = False
IS_PLOT = False
PARAMETER_DCT = {
      "k1": 1,
      "k2": 2,
      "k3": 3,
      "k4": 4,
      "k5": 5,
     }
VARIABLE_NAMES = ["S%d" % d for d in range(1, 7)]
parameters_strs = ["%s=%d" % (k, v) for k,v 
      in PARAMETER_DCT.items()]
parameters_str = "; ".join(parameters_strs)
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
""" % parameters_str
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
        

class TestModelFitter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)
        self.fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertIsNone(self.fitter.roadrunner_model)
        self.assertGreater(len(self.fitter.observed_ts), 0)
        #
        for variable in self.fitter.selected_columns:
            self.assertTrue(variable in VARIABLE_NAMES)

    def testSimulate(self):
        if IGNORE_TEST:
            return
        self.fitter._initializeRoadrunnerModel()
        self.fitter._simulate()
        self.assertTrue(self.fitter.observed_ts.isEqualShape(
              self.fitter.fitted_ts))

    def testResiduals(self):
        if IGNORE_TEST:
            return
        self.fitter._initializeRoadrunnerModel()
        arr = self.fitter._residuals(None)
        self.assertTrue(self.fitter.observed_ts.isEqualShape(
              self.fitter.residuals_ts))
        self.assertEqual(len(arr),
              len(self.fitter.observed_ts)*len(self.fitter.observed_ts.colnames))

    def checkParameterValues(self):
        dct = self.fitter.params.valuesdict()
        self.assertEqual(len(dct), len(self.fitter.parameters_to_fit))
        #
        for value in dct.values():
            self.assertTrue(isinstance(value, float))
        return dct

    def testFit1(self):
        if IGNORE_TEST:
            return
        def test(method):
            fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
                  list(PARAMETER_DCT.keys()), method=method)
            fitter.fitModel()
            PARAMETER = "k2"
            diff = np.abs(PARAMETER_DCT[PARAMETER]
                  - dct[PARAMETER])
            self.assertLess(diff, 1)
        #
        self.fitter.fitModel()
        dct = self.checkParameterValues()
        #
        for method in [model_fitter.METHOD_LEASTSQR,
              model_fitter.METHOD_BOTH,
              model_fitter.METHOD_DIFFERENTIAL_EVOLUTION]:
            test(method)

    def testFit2(self):
        if IGNORE_TEST:
            return
        def calcResidualStd(selected_columns):
            columns = self.timeseries.colnames[:3]
            fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
                  list(PARAMETER_DCT.keys()), selected_columns=selected_columns)
            fitter.fitModel()
            return np.std(fitter.residuals_ts.flatten())
        #
        CASES = [COLUMNS[0], COLUMNS[:3], COLUMNS]
        stds = [calcResidualStd(c) for c in CASES]
        # Variance should decrease with more columns
        self.assertGreater(stds[0], stds[1])
        self.assertGreater(stds[1], stds[2])

    def testGetFittedParameters(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()
        #
        self.fitter.bootstrap(num_iteration=3)
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()

    def testGetFittedModel(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)
        fitter1.fitModel()
        fitted_model = fitter1.getFittedModel()
        fitter2 = ModelFitter(fitted_model, self.timeseries, None)
        fitter2.fitModel()
        # Should get same fit without changing the parameters
        self.assertTrue(np.isclose(np.var(fitter1.residuals_ts.flatten()),
              np.var(fitter2.residuals_ts.flatten())))

    def testReportFit(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)
        fitter1.fitModel()
        result = fitter1.reportFit()

    def testPlotResiduals(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotResiduals(num_col=3, num_row=2)

    def testPlotFit(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotFitAll(num_col=3, num_row=2)

    def testPlotFitAll(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), is_plot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotFitAll()
        fitter1.plotFitAll(is_multiple=True)

    def testCalcNewObserved(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.calcNewObserved()
        ts = self.fitter.calcNewObserved()
        self.assertEqual(len(ts), len(self.fitter.observed_ts))
        self.assertGreater(ts["S1"][0], ts["S6"][0])
        self.assertGreater(ts["S6"][-1], ts["S1"][-1])

    def testBoostrap(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(num_iteration=100,
              report_interval=25)
        NUM_STD = 10
        result = self.fitter.bootstrap_result
        for p in self.fitter.parameters_to_fit:
            is_lower_ok = result.mean_dct[p]  \
                  - NUM_STD*result.std_dct[p]  \
                  < PARAMETER_DCT[p]
            is_upper_ok = result.mean_dct[p]  \
                  + NUM_STD*result.std_dct[p]  \
                  > PARAMETER_DCT[p]
            self.assertTrue(is_lower_ok)
            self.assertTrue(is_upper_ok)

    def testBoostrapBenchmark1(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        start_time = time.time()
        self.fitter.bootstrap(num_iteration=1000)
        elapsed_time = time.time() - start_time
        msg = "\n***6 stage network with 6000 iterations ran in %4.1f sec\n"  \
              % elapsed_time
        print(msg)

    def testGetFittedParameterStds(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        with self.assertRaises(ValueError):
            _ = self.fitter.getFittedParameterStds()
        #
        self.fitter.bootstrap(num_iteration=3)
        stds = self.fitter.getFittedParameterStds()
        for std in stds:
            self.assertTrue(isinstance(std, float))

    def testPlotParameterEstimates(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(num_iteration=100)
        self.fitter.plotParameterEstimates(num_col=2, ylim=[0, 10])
        
        

if __name__ == '__main__':
    matplotlib.use('TkAgg')
    unittest.main()
