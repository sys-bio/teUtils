.. SimpleSBML documentation master file, created by
   sphinx-quickstart 
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: teUtils

=======================================================
Welcome to the teUtils documentation for Version 0.99
=======================================================

This page describes the SimpleSBML package and its contents.  To install
SimpleSBML, go to
https://github.com/sys-bio/teUtils
.

To read more about Tellurium, go to
http://tellurium.analogmachine.org/
.

--------
Overview
--------

teUtils is a package that can be used to construct biological models in
SBML format using Python without interacting directly with the libSBML package.  Using
libSBML to build models can be difficult and complicated, even when the model
is relatively simple, and it can take time for a user to learn how to use the
package properly.  This package is intended as an intuitive interface for
users who are not already familiar with libSBML.  It can be used to construct
models with only a few lines of code, print out the resulting models in SBML
format, and simplify existing models in SBML format by finding the SimpleSBML
methods that can be used to build a libSBML version of the model.

--------
Examples
--------

The output saved to 'example_code.py' will look like this::

    import simplesbml
    model = simplesbml.SbmlModel(sub_units='')
    model.addCompartment(vol=1e-14, comp_id='comp')
    model.addSpecies(species_id='E', amt=5e-21, comp='comp')
    model.addSpecies(species_id='S', amt=1e-20, comp='comp')
    model.addSpecies(species_id='P', amt=0.0, comp='comp')
    model.addSpecies(species_id='ES', amt=0.0, comp='comp')
    model.addReaction(reactants=['E', 'S'], products=['ES'], expression='comp * (kon * E * S - koff * ES)', local_params={'koff': 0.2, 'kon': 1000000.0}, rxn_id='veq')
    model.addReaction(reactants=['ES'], products=['E', 'P'], expression='comp * kcat * ES', local_params={'kcat': 0.1}, rxn_id='vcat')

Examples of Interrogating an Existing Model
============================================

Verison 2.0.0 has a set of new 'get' methods that allows a user to easily interrogate a model for its contents.::

    import simplesbml
    mymodel = loadFromFile ('mymodel.xml')  # Load the model into a string variable
    model = simplesbml.loadSBMLStr(mymodel)

    # Or:

    model = simplesbml.loadSBMLFile('mymodel.xml')

    # Or of you're using the Tellurium package:

    model = simplesbml.loadSBMLStr(r.getSBML())    
  
    print ('Num compartmetns = ', s.getNumCompartmentIds())
    print ('Num parameters =', s.getNumParameters())
    print ('Num species =', s.getNumSpecies())
    print ('Num floating species = ', s.getNumFloatingSpecies())
    print ('Num floating species = ', s.getNumBoundarySpecies())
    print ('Num reactions = ', s.getNumReactions())
    print (s.getListOfCompartments())
    print (s.getListOfAllSpecies())
    print ('list of floating species = ', s.getListOfFloatingSpecies())
    print ('list of boundary species = ', s.getListOfBoundarySpecies())
    print ('List of reactions = ', s.getListOfReactionIds())
    print ('List of rules = ', s.getListOfRuleIds())

Here is an example script that uses simplesbml to create a stoichiometry matrix for a model::

    import tellurium as te, simplesbml, numpy as np

    r = te.loada("""
    S0 + S3 -> S2; k0*S0*S3;
    S3 + S2 -> S0; k1*S3*S2;
    S5 -> S2 + S4; k2*S5;
    S0 + S1 -> S3; k3*S0*S1;
    S5 -> S0 + S4; k4*S5;
    S0 -> S5; k5*S0;
    S1 + S1 -> S5; k6*S1*S1;
    S3 + S5 -> S1; k7*S3*S5;
    S1 -> $S4 + S4; k8*S1;

    S0 = 0; S1 = 0; S2 = 0; S3 = 0; S4 = 0; S5 = 0;
    k0 = 0; k1 = 0; k2 = 0; k3 = 0; k4 = 0
    k5 = 0; k6 = 0; k7 = 0; k8 = 0
    """)


-------------------
Tests and Examples
-------------------

Two test files can be found in the tests folder. The runTest.py is the more formal testing file. It was decided not to use the Python unittest due to its limitations and pyTest simply made the code unmanagable. A simple test system was therefore created. To run the tests just execute runTests.py. Make sure you have libsbml installed or are running the code under Tellurium.

-------------------
Classes and Methods
-------------------

.. automodule:: teUtils
   :members:
   :member-order: bysource

