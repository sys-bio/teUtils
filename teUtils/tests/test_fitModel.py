from teUtils.fitter import Fitter

import numpy as np
import os
import tellurium
import unittest


MODEL_STG = """
# Reactions   
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
    J3: S3 -> S4; k3*S3
    J4: S4 -> S5; k4*S4
    J5: S5 -> S6; k5*S5;
# Species initializations     
    S1 = 10;
# Parameters:      
   k1 = 1; k2 = 2; k3 = 3; k4 = 4; k5 = 5
"""

DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "data.csv")
        

class TestFitter(unittest.TestCase):

    def setUp(self):
        self.fitter = Fitter(MODEL_STG, TEST_DATA_PATH)

    def testConstructor(self):
        return
        true = isinstance(self.fitter.rmodel,
             tellurium.roadrunner.extended_roadrunner
             .ExtendedRoadRunner)
        self.assertTrue(true)
        self.assertGreater(np.shape(
            self.fitter.time_series)[0], 0)

    def testFit(self):
        parameters = ['k1', 'k2', 'k3', 'k4', 'k5']
        species_list = ['S1', 'S2', 'S3', 'S4']
        self.fitter.fit(parameters=parameters,
              species_list=species_list)
        values = self.fitter.parameter_values
        self.assertEqual(len(values), len(parameters))
        for value in values:
            self.assertTrue(isinstance(value, float))
        

if __name__ == '__main__':
  unittest.main()
