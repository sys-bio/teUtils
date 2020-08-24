# -*- coding: utf-8 -*-
"""
 Created on August 18, 2020

@author: joseph-hellerstein

Reports for model fitter
"""

from teUtils.namedTimeseries import NamedTimeseries, TIME, mkNamedTimeseries
from teUtils._modelFitterBootstrap import ModelFitterBootstrap

import lmfit
import numpy as np
import pandas as pd
import typing


##############################
class ModelFitterReport(ModelFitterBootstrap):

    def reportFit(self)->str:
        """
        Provides details of the parameter fit.
        
        Example
        -------
        f.reportFit()
        """
        self._checkFit()
        if self.minimizerResult is None:
            raise ValueError("Must do fitModel before reportFit.")
        return str(lmfit.fit_report(self.minimizerResult))

    def reportBootstrap(self):
        """
        Prints a report of the bootstrap results.
        ----------
        
        Example
        -------
        f.reportBootstrap()
        """
        self._checkBootstrap()
        print(self.bootstrapResult)
