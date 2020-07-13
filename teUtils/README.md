# Utilities for Tellurium

This repo includes a number of useful utilities for Tellurium users.
Modules are described below.

## odePrint

This provides a number of methods convert SBML into the equations representing the model. 
   
## plotting

This modules contains a variety of additional plotting methods, include 3D, heatmaps for control coefficients, 
and ascii plots.

## prettyTabular

This modules provides two methods to display fluxes and concentrations in a neat tabular format.

## buildNetworks

This modules provides two methods to build a linear chain of reactions using either mass-action or Michaelis-Menten
kinetics or a random network using uniuni, unibi, biuni or bibi mass-action governed reactions. 

## fitter
This module fits model parameters to observational data.


# Developer Notes

1. run tests as follows:
   1. change to this directory
   1. set the environment variable PYTHONPATH to
      the absolute path of this directory. In Linux,
      this can be done with `PYTHONPATH=``pwd``` and
      `export PYTHONPATH`.
   1. "python tests/<test file>

