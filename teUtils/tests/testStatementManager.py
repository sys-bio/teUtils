# -*- coding: utf-8 -*-
"""
Created on Aug 8, 2020

@author: joseph-hellerstein
"""

from teUtils._statementManager import StatementManager

import unittest


IGNORE_TEST = False
IS_PLOT = False
POS_VALUES = [2, 3]
KW_DCT = {"c": sum(POS_VALUES)}

def function(a, b, c=None):
    if c is None:
        return a + b
    else:
        return a + b + c


class TestStatementManager(unittest.TestCase):

    def setUp(self):
        self.manager = StatementManager(function)

    def testPositional(self):
        if IGNORE_TEST:
            return
        POS_VALUES = [2, 3]
        def test():
            result = manager.execute()
            self.assertEqual(result, sum(POS_VALUES))
        #
        manager = StatementManager(function)
        manager.addPosarg(POS_VALUES[0])
        manager.addPosarg(POS_VALUES[1])
        test()
        #
        manager = StatementManager(function)
        manager.addPosargs(POS_VALUES)
        test()

    def testPositional(self):
        if IGNORE_TEST:
            return
        def test():
            result = manager.execute()
            self.assertEqual(result, sum(POS_VALUES))
        #
        manager = StatementManager(function)
        manager.addPosarg(POS_VALUES[0])
        manager.addPosarg(POS_VALUES[1])
        test()
        #
        manager = StatementManager(function)
        manager.addPosargs(POS_VALUES)
        test()

    def testKeyword(self):
        if IGNORE_TEST:
            return
        def test(is_with=True):
            if is_with:
                manager.addPosargs(POS_VALUES)
                expected = 2*sum(POS_VALUES)
            else:
                expected = sum(POS_VALUES)
            result = manager.execute()
            self.assertEqual(result, expected)
        #
        manager = StatementManager(function)
        manager.addKwargs(**KW_DCT)
        test()
        #
        manager = StatementManager(function)
        manager.addKwargs(c=sum(POS_VALUES))
        test()
        

if __name__ == '__main__':
  unittest.main()
