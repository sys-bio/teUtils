# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19, 2020

@author: hsauro
@author: joseph-hellerstein
"""

import teUtils._modelFitterCore as mf
from teUtils._modelFitterCore import ModelFitterCore
from teUtils.namedTimeseries import NamedTimeseries, TIME

import numpy as np
import os
import tellurium
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
        

class TestModelFitterCore(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)
        self.fitter = ModelFitterCore(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertIsNone(self.fitter.roadrunnerModel)
        self.assertGreater(len(self.fitter.observedTS), 0)
        #
        for variable in self.fitter.selectedColumns:
            self.assertTrue(variable in VARIABLE_NAMES)

    def testCopy(self):
        if IGNORE_TEST:
            return
        newFitter = self.fitter.copy()
        self.assertTrue(isinstance(newFitter.modelSpecification, str))
        self.assertTrue(isinstance(newFitter, ModelFitterCore))

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
            fitter = ModelFitterCore(ANTIMONY_MODEL, self.timeseries,
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
        for method in [mf.METHOD_LEASTSQR, mf.METHOD_BOTH,
              mf.METHOD_DIFFERENTIAL_EVOLUTION]:
            test(method)

    def testFit2(self):
        if IGNORE_TEST:
            return
        def calcResidualStd(selectedColumns):
            columns = self.timeseries.colnames[:3]
            fitter = ModelFitterCore(ANTIMONY_MODEL, self.timeseries,
                  list(PARAMETER_DCT.keys()), selectedColumns=selectedColumns)
            fitter.fitModel()
            return np.std(fitter.residualsTS.flatten())
        #
        CASES = [COLUMNS[0], COLUMNS[:3], COLUMNS]
        stds = [calcResidualStd(c) for c in CASES]
        # Variance should decrease with more columns
        self.assertGreater(stds[0], stds[1])
        self.assertGreater(stds[1], stds[2])

    def testGetFittedModel(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitterCore(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()), isPlot=IS_PLOT)
        fitter1.fitModel()
        fittedModel = fitter1.getFittedModel()
        fitter2 = ModelFitterCore(fittedModel, self.timeseries, None)
        fitter2.fitModel()
        # Should get same fit without changing the parameters
        self.assertTrue(np.isclose(np.var(fitter1.residualsTS.flatten()),
              np.var(fitter2.residualsTS.flatten())))
        

if __name__ == '__main__':
    unittest.main()
