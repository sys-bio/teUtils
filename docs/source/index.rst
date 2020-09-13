.. teUilts documentation master file, created by sphinx-quickstart 
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: fileUtils

======================================
Documentation for teUtils Version 0.99
======================================

This page describes the teUtils package.

Contents:

.. toctree::
   :maxdepth: 2

   buildNetworks
   plotting
   parameterScanning
   odePrint
   prettyTabular
   fileUtils

Installation
------------

To install teUtils use

.. code-block:: python
   
   pip install teUtils

For additional information go to https://github.com/sys-bio/teUtils

To read more about Tellurium, go to http://tellurium.analogmachine.org/

--------
Overview
--------

teUtils is a utilties package for Telluirum that provides a number of useful function. These are grouped into:

- Plotting 
- Random Network Construction
- Parameter Scanning
- Pretty Tabular Output
- Converting SBML in to Readable Differential Equations
- File Utilties 

--------
Examples
--------

    .. code-block:: python

      import teUtils as tu
      # Build a random network using mass-action kintics with upto 10 species and 20 reactions
      antimonyModel = tu.buildNetworks.getRandomNetwork(10, 20)
    
      # Plot the species cocnentrations as a histogram for the roadrunne rmodel r
      tu.plotting.plotFloatingSpecies(r)

      # Plot a heatmap of the flux control coefficients
      tu.plotting.plotFluxControlHeatMap (r)

      # Plot a grid of phase portraits of all species in the model r
      tu.plotting.plotFluxControlHeatMap (r)

      # Generate the ODES for a SBML model stored in a file
      tu.odePrint.getODEsFromSBMLFile ('mymodel.xml')