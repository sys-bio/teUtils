# -*- coding: utf-8 -*-
"""
Created on Aug 14, 2020

@author: joseph-hellerstein
"""

import teUtils._plotOptions as po
from teUtils import _layoutManager as lm

import os
import unittest
import matplotlib
import matplotlib.pyplot as plt


IGNORE_TEST = False
IS_PLOT = False
DEFAULT_NUM_ROW = 2
DEFAULT_NUM_COL = 3
DEFAULT_NUM_PLOT = 5


class TestLayoutManagerLower(unittest.TestCase):

    def testConstructor(self):
        options = po.PlotOptions()
        options.numRow = 2*DEFAULT_NUM_ROW
        options.numCol = 3*DEFAULT_NUM_COL
        with self.assertRaises(RuntimeError):
            _ = lm.LayoutManager(
                  options, DEFAULT_NUM_PLOT)


class TestLayoutManagerSingle(unittest.TestCase):

    def setUp(self):
        options = po.PlotOptions()
        options.numRow = 2*DEFAULT_NUM_ROW
        options.numCol = 3*DEFAULT_NUM_COL
        self.layout = lm.LayoutManagerMatrix(
              options, DEFAULT_NUM_PLOT)

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertTrue(isinstance(
              self.layout.options, po.PlotOptions))

    def testInitializeAxes(self):
        if IGNORE_TEST:
            return
        figure, axes = self.layout._initializeAxes()
        self.assertTrue(isinstance(figure,
              matplotlib.figure.Figure))
        self.assertTrue(isinstance(axes, list))

    def testSetAxes(self):
        if IGNORE_TEST:
            return
        options = po.PlotOptions()
        options.numCol = 4
        options.numRow = 4
        _, axes, _ = self.layout._setAxes()
        if IS_PLOT:
            plt.show()


class TestLayoutManagerMatrix(unittest.TestCase):

    def setUp(self):
        options = po.PlotOptions()
        options.numRow = 2*DEFAULT_NUM_ROW
        options.numCol = 3*DEFAULT_NUM_COL
        self.layout = lm.LayoutManagerMatrix(
              options, DEFAULT_NUM_PLOT)

    def testSetAxes(self):
        if IGNORE_TEST:
            return
        options = po.PlotOptions()
        options.numCol = 4
        options.numRow = 4
        _, axes, _ = self.layout._setAxes()
        corners = [a.get_position().corners()
              for a in axes]
        self.assertEqual(corners[0][0][0],
               corners[1][0][0])
        if IS_PLOT:
            plt.show()


class TestLayoutManagerMatrix(unittest.TestCase):

    def setUp(self):
        options = po.PlotOptions()
        options.numRow = 2*DEFAULT_NUM_ROW
        options.numCol = 3*DEFAULT_NUM_COL
        self.layout = lm.LayoutManagerMatrix(
              options, DEFAULT_NUM_PLOT)

    def testSetAxes(self):
        if IGNORE_TEST:
            return
        options = po.PlotOptions()
        options.numCol = 4
        options.numRow = 4
        _, axes, _ = self.layout._setAxes()
        self.assertEqual(len(self.layout.axisPositions),                DEFAULT_NUM_PLOT)
        if IS_PLOT:
            plt.show()


if __name__ == '__main__':
    matplotlib.use('TkAgg')
    unittest.main()
