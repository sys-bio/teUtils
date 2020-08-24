"""Provides for incremental construction of python statements."""


class StatementManager(object):

    def __init__(self, func):
        """
        Parameters
        ----------
        func: Function
        """
        self.func = func
        self.pargs = []
        self.kwargs = {}

    def addKwargs(self, **kwargs):
        self.kwargs.update(kwargs)

    def addPosarg(self, arg):
        self.pargs.append(arg)

    def addPosargs(self, args):
        self.pargs.extend(args)

    def execute(self):
        return self.func(*self.pargs, **self.kwargs)
