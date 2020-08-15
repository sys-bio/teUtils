# -*- coding: utf-8 -*-
"""
Created on August 14, 2020

@author: joseph-hellerstein
"""

from teUtils._plotOptions import CommandManager, PlotOptions

import unittest
import matplotlib
import matplotlib.pyplot as plt


IGNORE_TEST = False
IS_PLOT = False
TITLE = "A Title"
FONTSIZE = "30"
       
 
class TestCommandManager(unittest.TestCase):

    def setUp(self):
        self.fig, self.ax = plt.subplots()
        self.manager= CommandManager("ax.set_title")

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertEqual(self.manager.string,
              "ax.set_title(")

    def testAdd1(self):
        if IGNORE_TEST:
            return
        self.manager.add(TITLE)
        self.assertTrue(TITLE in self.manager.string)
        #
        self.manager.add("fontsize", FONTSIZE)
        self.assertTrue(FONTSIZE in self.manager.string)
 
    def testGet(self):
        if IGNORE_TEST:
            return
        self.manager.add(TITLE)
        command = self.manager.get()
        self.assertEqual(")", command[-1])
        if IS_PLOT:
            ax = self.ax
            exec(command)
            plt.show()
       
 
class TestPlotOptions(unittest.TestCase):

    def setUp(self):
        self.options = PlotOptions()

    def testSetDict(self):
        if IGNORE_TEST:
            return
        FIGSIZE = "figsize"
        FIGSIZE_VALUE = (12, 20)
        DUMMY = "dummy"
        DUMMY_VALUE = "value"
        dct = {FIGSIZE: FIGSIZE_VALUE}
        self.options.setDict(dct)
        self.assertEqual(FIGSIZE_VALUE, self.options.figsize)
        #
        dct[DUMMY] = DUMMY_VALUE
        with self.assertRaises(ValueError):
            self.options.setDict(dct)


if __name__ == '__main__':
    #matplotlib.use('TkAgg')
    unittest.main()
