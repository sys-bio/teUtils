from teUtils.fitter import Fitter

import numpy as np
import os
import tellurium
import unittest

parameter_dct = {
      "k1": 1,
      "k2": 2,
      "k3": 3,
      "k4": 4,
      "k5": 5,
      }
parameters_strs = ["%s=%d" % (k, v) for k,v 
      in parameter_dct.items()]
parameters_str = "; ".join(parameters_strs)
MODEL_STR = """
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
TEST_DATA_PATH = os.path.join(DIR, "data.csv")
        

class TestFitter(unittest.TestCase):

    def setUp(self):
        self.fitter = Fitter(TEST_DATA_PATH,
            model_str=MODEL_STR,
            time_to_simulate=4)

    def testConstructor(self):
        true = isinstance(self.fitter.rmodel,
             tellurium.roadrunner.extended_roadrunner
             .ExtendedRoadRunner)
        self.assertTrue(true)
        self.assertEqual(np.shape(
            self.fitter.y_data)[0], 0)

    def testFit(self):
        parameters = ['k1', 'k2', 'k3', 'k4', 'k5']
        species_list = ['S1', 'S2', 'S3', 'S4']
        self.fitter.fit(parameters=parameters,
              species_list=species_list)
        dct = self.fitter.parameter_dct
        self.assertEqual(len(dct), len(parameters))
        #
        for value in dct.values():
            self.assertTrue(isinstance(value, float))
        #
        PARAMETER = "k2"
        diff = np.abs(parameter_dct[PARAMETER]
              - dct[PARAMETER])
        self.assertLess(diff, 0.1)
        

if __name__ == '__main__':
  unittest.main()
