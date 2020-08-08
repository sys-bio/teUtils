# -*- coding: utf-8 -*-
"""
Created on Aug 8, 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils import scanning

import numpy as np
import tellurium as te
import unittest


IGNORE_TEST = False
IS_PLOT = False
ANTIMONY_MODEL = """
    $Xo -> S1; vo;
    S1 -> S2; k1*S1 - k2*S2;
    S2 -> $X1; k3*S2;
    
    vo = 1
    k1 = 2; k2 = 0.6; k3 = 3;
    """


class TestScanning(unittest.TestCase):

    def setUp(self):
        self.rr_model = te.loada(ANTIMONY_MODEL)

    def testSimpleTImeCourseScan(self):
        if IGNORE_TEST:
            return
        NUM_SCAN = 3
        result = scanning.simpleTimeCourseScan (
              self.rr_model, 'k2', 'S1', 3, 12, 3)
        self.assertTrue(isinstance(result, np.ndarray))
        self.assertEqual(np.shape(result)[1], NUM_SCAN+1)
        

if __name__ == '__main__':
  unittest.main()
