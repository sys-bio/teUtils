"""Helper functions used in teUtils."""


from teUtils import _plotOptions as po

import numpy as np

INDENTATION = "  "
NULL_STR = ""


def updatePlotDocstring(target, keyphrase=None):
    """
    Changes the docstring of plot function to include all
    plot options.

    Parameters
    ----------
    target: class or function
    keyprhase: string searched for in docstring
    """
    # Place import here to avoid circular dependencies
    plot_options = str(po.PlotOptions())
    def updateFunctionDocstring(func):
        docstring = func.__doc__
        if not po.EXPAND_KEYPHRASE in docstring:
            msg = "Keyword not found in method: %s"  \
                  % func.__name__
            raise RuntimeError(msg)
        new_docstring =  \
              docstring.replace(
                    po.EXPAND_KEYPHRASE, plot_options)
        func.__doc__ = new_docstring
    #
    if "__call__" in dir(target):
        # Handle a function
        updateFunctionDocstring(target)
    else:
        # Update a class
        cls = target
        for name in dir(cls):
            if name[0:4] == po.PLOT:
                method = eval("cls.%s" % name)
                updateFunctionDocstring(method)


class Report():
    """Class used to generate reports."""

    def __init__(self):
        self.reportStr= NULL_STR
        self.numIndent = 0

    def indent(self, num: int):
        self.numIndent += num

    def _getIndentStr(self):
        return NULL_STR.join(np.repeat(
              INDENTATION, self.numIndent))
    
    def addHeader(self, title:str):
        indentStr = self._getIndentStr()
        self.reportStr+= "\n%s%s" % (indentStr, title)

    def addTerm(self, name:str, value:object):
        indentStr = self._getIndentStr()
        self.reportStr+= "\n%s%s: %s" %  \
              (indentStr, name, str(value))

    def get(self)->str:
        return self.reportStr
