# -*- coding: utf-8 -*-
"""
Created on Aug 19, 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils import _modelFitterBootstrap as mfb
from teUtils.namedTimeseries import NamedTimeseries, TIME

import numpy as np
import os
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
# Globals
TIMESERIES = NamedTimeseries(TEST_DATA_PATH)
FITTER = mfb.ModelFitterBootstrap(ANTIMONY_MODEL, TIMESERIES,
      list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
FITTER.fitModel()
        

class TestModelFitterBootstrap(unittest.TestCase):

    def setUp(self):
        self.timeseries = TIMESERIES
        self.fitter = FITTER
        self.fitter.bootstrapResult = None

    def testRunBootstrap(self):
        if IGNORE_TEST:
            return
        NUM_ITERATION = 10
        MAX_DIFF = 2
        arguments = mfb._Arguments(self.fitter)
        arguments.numIteration = NUM_ITERATION
        parameterDct, numSuccessIteration = mfb._runBootstrap(arguments)
        self.assertEqual(numSuccessIteration, NUM_ITERATION)
        trues = [len(v)==NUM_ITERATION for _, v in parameterDct.items()]
        self.assertTrue(all(trues))
        # Test not too far from true values
        trues = [np.abs(np.mean(v) - PARAMETER_DCT[p]) <= MAX_DIFF
              for p, v in parameterDct.items()]
        self.assertTrue(all(trues))

    def checkParameterValues(self):
        dct = self.fitter.params.valuesdict()
        self.assertEqual(len(dct), len(self.fitter.parametersToFit))
        #
        for value in dct.values():
            self.assertTrue(isinstance(value, float))
        return dct
        
    def testGetFittedParameters(self):
        if IGNORE_TEST:
            return
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()
        #
        self.fitter.bootstrap(numIteration=5)
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()

    def testCalcNewObserved(self):
        if IGNORE_TEST:
            return
        ts = mfb.calcObservedTS(self.fitter)
        self.assertEqual(len(ts),
              len(self.fitter.observedTS))
        self.assertGreater(ts["S1"][0], ts["S6"][0])
        self.assertGreater(ts["S6"][-1], ts["S1"][-1])

    def testBoostrapTimeMultiprocessing(self):
        return
        if IGNORE_TEST:
            return
        print("\n")
        def timeIt(maxProcess):
            startTime = time.time()
            self.fitter.bootstrap(numIteration=10000,
                  reportInterval=1000, maxProcess=maxProcess)
            elapsed_time = time.time() - startTime
            print("%s processes: %3.2f" % (str(maxProcess), elapsed_time))
        #
        timeIt(None)
        timeIt(1)
        timeIt(2)
        timeIt(4)

    def testBoostrap(self):
        if IGNORE_TEST:
            return
        self.fitter.bootstrap(numIteration=500,
              reportInterval=100, maxProcess=2)
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

    def testGetFittedParameterStds(self):
        if IGNORE_TEST:
            return
        with self.assertRaises(ValueError):
            _ = self.fitter.getFittedParameterStds()
        #
        self.fitter.bootstrap(numIteration=3)
        stds = self.fitter.getFittedParameterStds()
        for std in stds:
            self.assertTrue(isinstance(std, float))

    # TODO: move or delete
    def testBootstrapAccuracy(self):
        return
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
        
        fitter = mfb.ModelFitterBootstrap(r, BENCHMARK_PATH,
              ["k1", "k2"], selectedColumns=['S1', 'S3'], isPlot=IS_PLOT)
        fitter.fitModel()
        print(fitter.reportFit ())
        
        #fitter.plotResiduals (numCol=3, numRow=1, figsize=(17,5))
        #fitter.plotFit (numCol=3, numRow=1, figsize=(18, 6))
        
        print (fitter.getFittedParameters())  
        
        fitter.bootstrap(numIteration=200,
              reportInterval=500)
              #calcObservedFunc=ModelFitter.calcObservedTSNormal, std=0.01)
        fitter.plotParameterEstimatePairs(['k1', 'k2'],
              markersize1=2)
        print("Mean: %s" % str(fitter.getFittedParameters()))
        print("Std: %s" % str(fitter.getFittedParameterStds()))
        fitter.getBootstrapReport()

        
        

if __name__ == '__main__':
    unittest.main()
