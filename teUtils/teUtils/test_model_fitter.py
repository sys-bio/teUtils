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
        self.fitter = ModelFitter(ANTIMONY_MODEL, self.timeseries)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        true = isinstance(self.fitter.roadrunner_model,
             tellurium.roadrunner.extended_roadrunner
             .ExtendedRoadRunner)
        self.assertTrue(true)
        self.assertGreater(len(self.fitter.timeseries), 0)
        #
        parameters = self.fitter.params.valuesdict().keys()
        trues = [p in self.timeseries.colnames for p in parameters]
        self.assertTrue(all(trues))

    def testSimulate(self):
        if IGNORE_TEST:
            return
        timeseries = self.fitter.simulate()
        diff = sum([t1 - t2 for t1, t2 in 
              zip(timeseries[TIME], self.fitter.timeseries["time"])])
        self.assertTrue(np.isclose(diff, 0))

    def testFit(self):
        if IGNORE_TEST:
            return
        parameters = ['k1', 'k2', 'k3', 'k4', 'k5']
        species_list = ['S1', 'S2', 'S3', 'S4',
              'S5', 'S6']
        self.fitter.fit(parameters=parameters,
              species_list=species_list)
        dct = self.fitter.PARAMETER_DCT
        self.assertEqual(len(dct), len(parameters))
        #
        for value in dct.values():
            self.assertTrue(isinstance(value, float))
        #
        PARAMETER = "k2"
        diff = np.abs(PARAMETER_DCT[PARAMETER]
              - dct[PARAMETER])
        self.assertLess(diff, 0.1)

        

if __name__ == '__main__':
  unittest.main()
