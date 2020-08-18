# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.modelFitter import ModelFitter
from teUtils import modelFitter
from teUtils.namedTimeseries import NamedTimeseries, TIME

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
        self.fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertIsNone(self.fitter.roadrunnerModel)
        self.assertGreater(len(self.fitter.observedTS), 0)
        #
        for variable in self.fitter.selectedColumns:
            self.assertTrue(variable in VARIABLE_NAMES)

    def testSimulate(self):
        if IGNORE_TEST:
            return
        self.fitter._initializeRoadrunnerModel()
        self.fitter._simulate()
        self.assertTrue(self.fitter.observedTS.isEqualShape(
              self.fitter.fittedTS))

    def testResiduals(self):
        if IGNORE_TEST:
            return
        self.fitter._initializeRoadrunnerModel()
        arr = self.fitter._residuals(None)
        self.assertTrue(self.fitter.observedTS.isEqualShape(
              self.fitter.residualsTS))
        self.assertEqual(len(arr),
              len(self.fitter.observedTS)*len(self.fitter.observedTS.colnames))

    def checkParameterValues(self):
        dct = self.fitter.params.valuesdict()
        self.assertEqual(len(dct), len(self.fitter.parametersToFit))
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
        for method in [modelFitter.METHOD_LEASTSQR,
              modelFitter.METHOD_BOTH,
              modelFitter.METHOD_DIFFERENTIAL_EVOLUTION]:
            test(method)

    def testFit2(self):
        if IGNORE_TEST:
            return
        def calcResidualStd(selectedColumns):
            columns = self.timeseries.colnames[:3]
            fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
                  list(PARAMETER_DCT.keys()), selectedColumns=selectedColumns)
            fitter.fitModel()
            return np.std(fitter.residualsTS.flatten())
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
        self.fitter.bootstrap(numIteration=3)
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()

    def testGetFittedModel(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        fittedModel = fitter1.getFittedModel()
        fitter2 = ModelFitter(fittedModel, self.timeseries, None)
        fitter2.fitModel()
        # Should get same fit without changing the parameters
        self.assertTrue(np.isclose(np.var(fitter1.residualsTS.flatten()),
              np.var(fitter2.residualsTS.flatten())))

    def testReportFit(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        result = fitter1.reportFit()

    def testPlotResiduals(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotResiduals(numCol=3, numRow=2)

    def testPlotFit(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotFitAll(numCol=3, numRow=2)

    def testPlotFitAll(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        fitter1.plotFitAll()
        fitter1.plotFitAll(isMultiple=True)

    def testCalcNewObserved(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        ts = ModelFitter.calcObservedTS(self.fitter)
        self.assertEqual(len(ts),
              len(self.fitter.observedTS))
        self.assertGreater(ts["S1"][0], ts["S6"][0])
        self.assertGreater(ts["S6"][-1], ts["S1"][-1])

    def testBoostrap(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(numIteration=100,
              reportInterval=25)
        NUM_STD = 10
        result = self.fitter.bootstrapResult
        for p in self.fitter.parametersToFit:
            isLowerOk = result.meanDct[p]  \
                  - NUM_STD*result.stdDct[p]  \
                  < PARAMETER_DCT[p]
            isUpperOk = result.meanDct[p]  \
                  + NUM_STD*result.stdDct[p]  \
                  > PARAMETER_DCT[p]
            self.assertTrue(isLowerOk)
            self.assertTrue(isUpperOk)

    def testBoostrapReport(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(numIteration=5000,
              reportInterval=1000)
        bootstrapReport = str(self.fitter.bootstrapResult)
        for param in self.fitter.bootstrapResult.parameters:
            self.assertTrue(param in bootstrapReport)
        self.fitter.getBootstrapReport()

    def testBoostrapBenchmark1(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        startTime = time.time()
        self.fitter.bootstrap(numIteration=1000)
        elapsedTime = time.time() - startTime
        self.assertLess(elapsedTime, BENCHMARK1_TIME)

    def testGetFittedParameterStds(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        with self.assertRaises(ValueError):
            _ = self.fitter.getFittedParameterStds()
        #
        self.fitter.bootstrap(numIteration=3)
        stds = self.fitter.getFittedParameterStds()
        for std in stds:
            self.assertTrue(isinstance(std, float))

    def testPlotParameterEstimates(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(numIteration=100)
        self.fitter.plotParameterEstimatePairs(ylim=[0, 5], xlim=[0, 5])

    def testPlotParameterHistograms(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        self.fitter.bootstrap(numIteration=100)
        self.fitter.plotParameterHistograms(ylim=[0, 5], xlim=[0, 6],
              bins=10, parameters=["k1", "k2"])

    def testBootstrapAccuracy(self):
        if IGNORE_TEST:
            return
        import tellurium as te
        import teUtils as tu
        
        r = te.loada("""
            J1: S1 -> S2; k1*S1
            J2: S2 -> S3; k2*S2
           
            S1 = 1; S2 = 0; S3 = 0;
            k1 = 0; k2 = 0; 
        """)
        
        fitter = tu.modelFitter.ModelFitter(r, BENCHMARK_PATH,
              ["k1", "k2"], selectedColumns=['S1', 'S3'], isPlot=IS_PLOT)
        fitter.fitModel()
        print(fitter.reportFit ())
        
        #fitter.plotResiduals (numCol=3, numRow=1, figsize=(17,5))
        #fitter.plotFit (numCol=3, numRow=1, figsize=(18, 6))
        
        print (fitter.getFittedParameters())  
        
        fitter.bootstrap(numIteration=2000,
              reportInterval=500)
              #calcObservedFunc=ModelFitter.calcObservedTSNormal, std=0.01)
        fitter.plotParameterEstimatePairs(['k1', 'k2'],
              markersize1=2)
        print("Mean: %s" % str(fitter.getFittedParameters()))
        print("Std: %s" % str(fitter.getFittedParameterStds()))
        fitter.getBootstrapReport()

        
        

if __name__ == '__main__':
    matplotlib.use('TkAgg')
    unittest.main()
