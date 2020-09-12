'''
    ===================
    Tellurium Utilities
    ===================

    teUtils provides a number of useful modules.

    This repo includes a number of useful utilities for Tellurium users. These are included in three modules:

    odePrint
    --------

    This provides a number of methods convert SBML into the equations representing the model. 
   
    plotting
    --------

    This modules contains a variety of additional plotting methods, include 3D, heatmaps for control coefficients, and ascii plots.

    prettyTabular
    -------------

    This modules provides two methods to display fluxes and concentrations in a neat tabular format.

    buildNetworks
    -------------

    This module provides a single method that can be used to build linear chaing network with random parmaetr values. The 
    user has a choice of either building a network based on mass-action or Michaelis-Menten kinetics

    parameterScanning
    --------

    At the moment a single method to do a simple time course parameter scan
    
    fitModel
    --------
    
    A helper class to make it much easier to fit models using lmfit
    
'''

try:
  from . import _version
except:
    from teUtils import _version

__version__ = _version.__version__

try:
    from . import odePrint
    from . import plotting
    from . import prettyTabular
    from . import buildNetworks
    from . import parameterScanning
    from . import fileUtils
except:
    from teUtils import odePrint
    from teUtils import plotting
    from teUtils import prettyTabular
    from teUtils import buildNetworks
    from teUtils import parameterScanning
    from teUtils import fileUtils
    #from teUtils import model_fitter
