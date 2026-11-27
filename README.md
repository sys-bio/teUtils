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


# teUtils: Additional Utilities for Tellurium

teUtils is a collection of utilities for [Tellurium](https://tellurium.analogmachine.org/) users that we
have found useful in our own modeling work. It adds functions for:

- Generating test models: linear pathways and random mass-action networks, returned as Antimony
- Printing a model as its rate equations and ODEs
- Extra plots: control coefficient heat maps and 3D plots, phase portrait grids, ASCII bar charts and more
- Showing concentrations and fluxes as neat text tables
- Simple time course parameter scans
- Reading CSV files into arrays ready for plotting

# Installation

Install teUtils from PyPI with pip:

```
pip install teUtils
```

To upgrade an existing installation:

```
pip install --upgrade teUtils
```

teUtils requires Python 3.7 or later. pip installs its dependencies automatically: tellurium, libroadrunner,
python-libsbml, numpy, pandas, matplotlib, seaborn and tabulate.

# Quick start

```python
import tellurium as te
import teUtils as tu

# Build a three-step linear pathway with mass-action kinetics
model = tu.buildNetworks.getLinearChain(3, rateLawType='MassAction')
r = te.loada(model)

r.simulate(0, 50, 100)
r.steadyState()

# Show the steady-state fluxes as a table
print(tu.prettyTabular.tabulateFluxes(r))

# Plot the flux control coefficients as a heat map
tu.plotting.plotFluxControlHeatMap(r)
```

Output from the table:

```
+------+------------------+
| Id   |   Reaction Rates |
|------+------------------|
| J1   |          4.04079 |
| J2   |          4.04079 |
| J3   |          4.04079 |
+------+------------------+
```

# Documentation

Full API documentation is at: http://teUtils.readthedocs.io/en/latest/

The sections below give an overview of each module. All functions that take `r` expect a roadrunner
instance, for example one created by `te.loada(...)`.

## buildNetworks

Generates models as Antimony strings that can be loaded with `te.loada`.

| Function | Description |
|----------|-------------|
| `getLinearChain(lengthOfChain, rateLawType='MassAction', keqRatio=5)` | A linear pathway `Xo -> S1 -> ... -> X1` with boundary species at each end and random parameter values. |
| `getRandomNetwork(nSpecies, nReactions, isReversible=False, randomSeed=-1, ...)` | A random network built from uni-uni, bi-uni, uni-bi and bi-bi mass-action reactions. Returns an empty string if the network has no floating species. |
| `getRandomNetworkDataStructure(nSpecies, nReactions, ...)` | The same random network as a Python data structure (floating ids, boundary ids, reaction list) instead of Antimony. |

`getLinearChain` supports three rate laws through `rateLawType`:

| rateLawType | Rate law for each step |
|-------------|------------------------|
| `'MassAction'` (default) | `e1*(k10*S1 - k11*S2)` |
| `'ModifiedMassAction'` | `k1*S1*(1 - (S2/S1)/Keq1)` |
| `'Michaelis'` | `Vm1/Km10*(S1 - S2/Keq1)/(1 + S1/Km10 + S2/Km11)` |

The `e` terms in the mass-action rate laws make it easy to compute control coefficients with respect to
enzyme level. The modified mass-action form makes it easy to control each reaction's equilibrium constant.

```python
model = tu.buildNetworks.getLinearChain(10, rateLawType='ModifiedMassAction')

# Random network with 6 species and 9 reactions, repeatable with a seed
model = tu.buildNetworks.getRandomNetwork(6, 9, randomSeed=42)
r = te.loada(model)
r.simulate(0, 10, 100)
```

Random network generation can be configured through `tu.buildNetworks.Settings`:

| Setting | Default | Meaning |
|---------|---------|---------|
| `rateConstantScale` | `1.0` | Rate constants are drawn between 0 and this value |
| `allowMassViolatingReactions` | `False` | Allow reactions such as `A + B -> A` |
| `addDegradationSteps` | `False` | Add a degradation step to every floating species |
| `removeBoundarySpecies` | `True` | Turn pure sources and sinks into boundary species |
| `ReactionProbabilities.UniUni` / `BiUni` / `UniBi` / `BiBi` | `0.3` / `0.3` / `0.3` / `0.1` | Probability of picking each reaction type |

Call `tu.buildNetworks.Settings.restoreDefaultProbabilities()` to reset the reaction probabilities.

## odePrint

Converts a model into readable rate equations and ODEs.

| Function | Description |
|----------|-------------|
| `getODEsFromModel(r)` | ODEs for a roadrunner instance |
| `getODEsFromSBMLString(sbmlStr)` | ODEs for an SBML string |
| `getODEsFromSBMLFile(fileName)` | ODEs for an SBML file |

```python
r = te.loada('S1 -> S2; k1*S1; k1 = 1; S1 = 10')
print(tu.odePrint.getODEsFromModel(r))
```

```
v_J0 = k1*S1

dS1/dt = -v_J0
dS2/dt = v_J0
```

## plotting

Additional plotting functions built on matplotlib and seaborn. Most heat map and grid functions accept
`pdfExport='file.pdf'` to save the figure, and `figsize=(width, height)` to set its size.

| Function | Description |
|----------|-------------|
| `plotFluxControlHeatMap(r)` | Flux control coefficients as a heat map |
| `plotConcentrationControlHeatMap(r)` | Concentration control coefficients as a heat map |
| `plotArrayHeatMap(data)` | Any 2D array as a heat map |
| `plotFluxControlIn3D(r)` | Flux control coefficients as a 3D bar plot |
| `plotConcentrationControlIn3D(r)` | Concentration control coefficients as a 3D bar plot |
| `plotFluxControlBar(r, reactionId)` | Bar chart of the control coefficients for one flux |
| `plotConcentrationControlBar(r, speciesId)` | Bar chart of the control coefficients for one species |
| `plotReactionRates(r)` | Bar chart of the current reaction rates |
| `plotFloatingSpecies(r)` | Bar chart of the current floating species concentrations |
| `plotPhasePortraitGrid(r)` | Grid of phase portraits for every pair of floating species |
| `plotRandSimGrid(r)` | Grid of time courses, each using randomly drawn parameter values |
| `plotAsciiConcentrationsBar(r, scale=5)` | Text-only bar chart of the concentrations |
| `plotAsciiReactionRatesBar(r, scale=5)` | Text-only bar chart of the reaction rates |
| `plotArray(result, ...)` | Plot an array whose first column is the x-axis |
| `plotWithLegend(r, result)` | Plot a simulation result with a legend |

## prettyTabular

Displays model values as text tables, using the [tabulate](https://pypi.org/project/tabulate/) package.

| Function | Description |
|----------|-------------|
| `tabulateConcentrations(r, fmt='psql')` | Table of the floating species concentrations |
| `tabulateFluxes(r, fmt='psql')` | Table of the reaction rates |

`fmt` can be any tabulate table format, such as `'psql'`, `'grid'`, `'github'` or `'plain'`.

## parameterScanning

| Function | Description |
|----------|-------------|
| `simpleTimeCourseScan(r, parameter, variable, lowRange, highRange, numberOfScans, timeEnd=10, numberOfPoints=100)` | Runs a time course at evenly spaced values of one parameter and plots one variable from each run on a single graph |

```python
r = te.loada('S1 -> S2; k1*S1; k1 = 0.1; S1 = 10')
tu.parameterScanning.simpleTimeCourseScan(r, 'k1', 'S1', 0.1, 1.0, 5)
```

## fileUtils

| Function | Description |
|----------|-------------|
| `readCsvFile(fileName, includeFirstColumnLabel=False)` | Reads a CSV file with a header row and returns the data as a numpy array plus the list of column names |

```python
data, header = tu.fileUtils.readCsvFile('mydata.csv')
tu.plotting.plotArray(data, labels=header)
```

# Release history

**3.2.1** Package dependencies now include matplotlib, seaborn and libroadrunner. Removes the deprecated
license classifier.

**3.2** Fixes invalid Antimony from `getRandomNetwork` (boundary species are now declared with `const`) and
other buildNetworks bugs. Adds `pyproject.toml` so pip no longer warns about the legacy `setup.py` build.

**3.0** Updates matplotlib support and fixes some typos in the docs.

**2.9** Adds `e` terms to mass-action rate laws, for example `S1 -> S2; e1*(k1*S1 - k2*S2)`, which makes it
easier to compute control coefficients with respect to `e`. Also adds the modified mass-action rate law
`v = k1*A*(1 - (B/A)/Keq1)`, generated with `getLinearChain(10, rateLawType='ModifiedMassAction')`.

# License

MIT
