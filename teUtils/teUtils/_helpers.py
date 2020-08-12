"""Helper functions used in teUtils."""


PLOT = "plot"


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
    from teUtils.timeseriesPlotter import PlotOptions, EXPAND_KEYPHRASE
    plot_options = str(PlotOptions())
    def updateFunctionDocstring(func):
        docstring = func.__doc__
        if not EXPAND_KEYPHRASE in docstring:
            msg = "Keyword not found in method: %s"  \
                  % func.__name__
            raise RuntimeError(msg)
        new_docstring =  \
              docstring.replace(EXPAND_KEYPHRASE, plot_options)
        func.__doc__ = new_docstring
    #
    if "__call__" in dir(target):
        # Handle a function
        updateFunctionDocstring(target)
    else:
        # Update a class
        cls = target
        for name in dir(cls):
            if name[0:4] == PLOT:
                method = eval("cls.%s" % name)
                updateFunctionDocstring(method)
