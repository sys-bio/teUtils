# -*- coding: utf-8 -*-
"""
Created on Aug 8, 2020

@author: joseph-hellerstein
"""

from teUtils import _helpers
from teUtils.timeseriesPlotter import PlotOptions

import unittest


IGNORE_TEST = False
IS_PLOT = False

  
def plotItFunction(a, b, **kwargs):
    """
    Dummy method
    
    Parameters
    ----------
    a: float
    b: float
    kwargs: dict
        Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
    Returns
    -------
    None
    """
    pass

class GoodClass():

  def plotIt(self, a, b, **kwargs):
        """
        Dummy method
        
        Parameters
        ----------
        a: float
        b: float
        kwargs: dict
            Expansion keyphrase. Expands to help(PlotOptions()). Do not remove. (See timeseriesPlotter.EXPAND_KEYPRHASE.)
        Returns
        -------
        None
        """
        pass


class BadClass():

  def plotIt(self, a, b, **kwargs):
        """
        Plot method without the keyword string.
        """
        pass


class TestHelpers(unittest.TestCase):

    def setUp(self):
        pass

    def testUpdatePlotDocstring(self):
        if IGNORE_TEST:
            return
        def test(target):
            _helpers.updatePlotDocstring(target)
            isTrue = str(PlotOptions()) in GoodClass.plotIt.__doc__
            self.assertTrue(isTrue)
        #
        test(GoodClass)
        test(plotItFunction)
        #
        with self.assertRaises(RuntimeError):
            _helpers.updatePlotDocstring(BadClass)
            

if __name__ == '__main__':
  unittest.main()