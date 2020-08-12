# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
@author: joseph-hellerstein
"""

import teUtils as tu

import numpy as np
import os
import time


BENCHMARK1_TIME = 30 # Actual is 20 sec
DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(DIR, "tst_data.txt")
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
        
    fitter = tu.model_fitter.ModelFitter(MODEL, BENCHMARK_PATH,
          ["k1", "k2"], selected_columns=['S1', 'S3'], is_plot=False)
    fitter.fitModel()
    start_time = time.time()
    fitter.bootstrap(num_iteration=6000)
    elapsed_time = time.time() - start_time
    return elapsed_time
        

if __name__ == '__main__':
    print("Elapsed time: %4.2f" % main(6000))
