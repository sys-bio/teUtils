from fitter import Fitter

import numpy as np
import os
import tellurium
import unittest

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
TEST_DATA_PATH = os.path.join(DIR, "testdata.txt")
        

class TestFitter(unittest.TestCase):

    def setUp(self):
        self.fitter = Fitter(TEST_DATA_PATH,
            model_str=ANTIMONY_MODEL,
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

    def testFitModel(self):
from teUtils.fitter import Fitter

import numpy as np
import os
import tellurium
import unittest

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
TEST_DATA_PATH = ospath.join(DIR, "data.csv")
        

class TestFitter(unittest.TestCase):

    def setUp(self):
        self.fitter = Fitter(
            time_series_file_path=TEST_DATA_PATH,
            antimony_model=ANTIMONY_MODEL,
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

    def testFit(self):
    """
      Runs a simple example
               
      Example:
            fitModel.tryMe()
     """    
    import tellurium as te
    import numpy as np
    
    r = te.loada("""
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
    """)

    # Alternative way to start fitter
    # f = fitter (roadrunner_model=r, time_series_file_name='testdata.txt',
    #         selected_time_series_ids=['S1', 'S2', 'S3', 'S4']),
    #         parameters_to_fit=['k1', 'k2', 'k3', 'k4', 'k5']) 
    # f.fitModel()
    
    f = fitter(r)

    f.setParametersToFit (['k1', 'k2', 'k3', 'k4', 'k5'])
    f.setTimeSeriesData ('testdata.txt', ['S1', 'S2', 'S3', 'S4'])

    f.fitModel()
    print ("Fitted Parameters are:")
    print (f.getFittedParameters())
    f.plotTimeSeries()
        

if __name__ == '__main__':
  unittest.main()
