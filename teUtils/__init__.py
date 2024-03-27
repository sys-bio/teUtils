'''
    ===================
    Tellurium Utilities
    ===================

    teUtils provides a number of useful modules to the tellurium modeling package.

    This repo includes a number of useful utilities for Tellurium users. These are included in five modules:

    odePrint
    --------

    This provides a number of methods convert SBML into the equations representing the model. 
   
    plotting
    --------

    This module contains a variety of additional plotting methods, including 3D plots, heatmaps for control coefficients, and ascii plots.

    prettyTabular
    -------------

    This modules provides two methods to display fluxes and concentrations in a neat tabular format.

    buildNetworks
    -------------

    This module provides a number of methods that can be used to build random kinetic networks linear. The 
    user choose networks based on mass-action or Michaelis-Menten kinetics, linear chaings or random networks.
    A number of methods under Settings allow the generation of random models to be configured.

    parameterScanning
    -----------------

    At the moment this is a single method to do a simple time course parameter scan
    
    fileUtils
    --------
    
    Currently a single method to make it trival to import a csv file 

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
