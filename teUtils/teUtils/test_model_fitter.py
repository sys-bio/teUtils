from model_fitter import ModelFitter
from named_timeseries import NamedTimeseries, TIME

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
parameters_strs = ["%s=%d" % (k, v) for k,v 
      in PARAMETER_DCT.items()]
parameters_str = "; ".join(parameters_strs)
ANTIMONY_MODEL = """
# Reactions   
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
    J3: S3 -> S4; k3*S3
    J4: S4 -> S5; k4*S4
    J5: S5 -> S6; k5*S5;
# Species initializations     
    S1 = 10;
# Parameters:      
   %s
""" % parameters_str
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
        

class TestModelFitter(unittest.TestCase):

    def setUp(self):
        self.timeseries = NamedTimeseries(TEST_DATA_PATH)
        self.fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()))

    def testConstructor(self):
        if IGNORE_TEST:
            return
        true = isinstance(self.fitter.roadrunner_model,
             tellurium.roadrunner.extended_roadrunner
             .ExtendedRoadRunner)
        self.assertTrue(true)
        self.assertGreater(len(self.fitter.timeseries), 0)
        #
        for variable in self.fitter.selected_variable_names:
            self.assertTrue(variable in VARIABLE_NAMES)
        #
        self.assertTrue(isinstance(
              self.fitter.unoptimized_residual_variance, float))

    def testSimulate(self):
        if IGNORE_TEST:
            return
        timeseries = self.fitter.simulate()
        diff = sum([t1 - t2 for t1, t2 in 
              zip(timeseries[TIME], self.fitter.timeseries["time"])])
        self.assertTrue(np.isclose(diff, 0))

    def testResiduals(self):
        if IGNORE_TEST:
            return
        arr = self.fitter._residuals(None)
        self.assertEqual(len(arr),
              len(self.fitter.timeseries.colnames)*
              len(self.fitter.timeseries))

    def checkParameterValues(self):
        dct = self.fitter.minimizer.params.valuesdict()
        self.assertEqual(len(dct), len(self.fitter.parameters_to_fit))
        #
        for value in dct.values():
            self.assertTrue(isinstance(value, float))
        return dct

    def testFit(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        dct = self.checkParameterValues()
        #
        PARAMETER = "k2"
        diff = np.abs(PARAMETER_DCT[PARAMETER]
              - dct[PARAMETER])
        self.assertLess(diff, 1)

    def testGetFittedParameters(self):
        if IGNORE_TEST:
            return
        self.fitter.fitModel()
        values = self.fitter.getFittedParameters()
        _ = self.checkParameterValues()

    def testGetFittedModel(self):
        if IGNORE_TEST:
            return
        fitter1 = ModelFitter(ANTIMONY_MODEL, self.timeseries,
              list(PARAMETER_DCT.keys()))
        fitter1.fitModel()
        fitted_model = fitter1.getFittedModel()
        fitter2 = ModelFitter(fitted_model, self.timeseries, None)
        # Should get same fit without changing the parameters
        self.assertTrue(np.isclose(fitter1.optimized_residual_variance,
              fitter2.unoptimized_residual_variance))
        

if __name__ == '__main__':
  unittest.main()
