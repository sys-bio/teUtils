# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

from teUtils.modelFitter import ModelFitter

import numpy as np
import os
import time


BENCHMARK1_TIME = 30 # Actual is 20 sec
DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_PATH = os.path.join(DIR, "groundtruth_2_step_0_1.txt")
MODEL = """
    J1: S1 -> S2; k1*S1
    J2: S2 -> S3; k2*S2
   
    S1 = 1; S2 = 0; S3 = 0;
    k1 = 0; k2 = 0; 
"""
        

def main(num_iteration):
    """
    Calculates the time to run iterations of the benchmark.

    Parameters
    ----------
    num_iteration: int
    
    Returns
    -------
    float: time in seconds
    """
    fitter = ModelFitter(MODEL, BENCHMARK_PATH,
          ["k1", "k2"], selectedColumns=['S1', 'S3'], isPlot=False)
    fitter.fitModel()
    startTime = time.time()
    fitter.bootstrap(numIteration=10000, reportInterval=1000)
    elapsedTime = time.time() - startTime
    return elapsedTime
        

if __name__ == '__main__':
    print("Elapsed time: %4.2f" % main(6000))
