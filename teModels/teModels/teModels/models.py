

import tellurium as _te
import matplotlib.pyplot as _plt
import numpy as _np
import os as _os

__version__ = "0.98"

def _getModelDir():
    import pathlib as _pathlib
    parent = _pathlib.Path(__file__).parent
    return _os.path.join (parent.__str__(), 'models')

def listModelNames():
    import pathlib as _pathlib
    parent = _pathlib.Path(__file__).parent
    flist = _os.listdir (_getModelDir())
    return flist

def listModel(name):
    f = open(_os.path.join (_getModelDir() , name), "r")
    mstring = f.read()
    f.close()
    return mstring 

def runModel (name):
    path = _os.path.join (_getModelDir(), name)
    exec(open(path).read())
