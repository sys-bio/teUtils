 <table style="width:100%">
  <tr>
    <td><img src="https://codecov.io/gh/sys-bio/teUtils/branch/master/graph/badge.svg" /></td>
    <td><img src="https://img.shields.io/badge/License-MIT-yellow.svg" /></td>
    <td><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/w/sys-bio/teUtils"></td>
    <td><img alt="Read the Docs" src="https://img.shields.io/readthedocs/teutils"></td>
    <td><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/teutils"></td>
    <td><img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/sys-bio/teutils"></td>
    <td><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/teUtils"></td>
  </tr>
</table> 

<a href="https://codecov.io/gh/sys-bio/teUtils">
</a>


# Additional Utilities for Tellurium that we have found useful in our work

This repo includes a number of useful utilities for Tellurium users. These include:

# Installation
You can install teUtils using pip:

``pip install teUtils``

# Documenation

The documentation can be found at: http://teUtils.readthedocs.io/en/latest/

## buildNetworks
This modules provides two methods to build a linear chain of reactions using either mass-action or Michaelis-Menten
kinetics or a random network using uniuni, unibi, biuni or bibi mass-action governed reactions. 

## odePrint
This provides a number of methods to convert SBML into the equations representing the model. 
   
## plotting
This modules contains a variety of additional plotting methods, include 3D, heatmaps for control coefficients, ascii plots, phase plots and more.

## prettyTabular
This modules provides two methods to display fluxes and concentrations in a neat tabular format using jsut ascii characters.

## fileUtils
File utilties that simply some operation whch for some reason are not available in Python

## parameterScanning
This package only has one method currently which is a single method to make time course parameter scanning easier

