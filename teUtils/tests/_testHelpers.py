# -*- coding: utf-8 -*-
"""
Created on Aug 20, 2020

@author: joseph-hellerstein

Codes used in support of test modules.
"""


from teUtils.namedTimeseries import NamedTimeseries, TIME
from teUtils._modelFitterCore import ModelFitterCore

import os


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


def getTimeseries():
    return NamedTimeseries(TEST_DATA_PATH)

def getFitter(cls=ModelFitterCore, isPlot=False):
    return cls(ANTIMONY_MODEL, getTimeseries(),
      list(PARAMETER_DCT.keys()), isPlot=isPlot)

def getObservedFitted():
    fitter = getFitter()
    fitter.fitModel()
    return fitter.observedTS, fitter.residualsTS
