# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 10:36:22 2017
@author: hsauro
"""

# Add option to allow vJi and dX/dt to be merged.

# Let's only support 3.x series
#from __future__ import absolute_import, division, print_function, unicode_literals

import tellurium as _te
import tesbml as _libsbml

def getODEsFromSBMLFile (fileName):
    """ Given a SBML file name, this function returns the model
    as a string of rules and ODEs
    
    >>> print (te.getODEsFromSBMLFile ('mymodel.xml'))
    """

    sbmlStr = _te.readFromFile (fileName)
    extractor = _ODEExtractor (sbmlStr)
    return extractor._toString()

def getODEsFromSBMLString (sbmlStr):
    """ Given a SBML string this fucntion returns the model
    as a string of rules and ODEs
    
    >>> print (te.getODEsFromSBMLString (sbmlStr))
    """

    extractor = _ODEExtractor (sbmlStr)
    return extractor._toString()

def getODEsFromModel (sbmlModel):
    """Given a roadrunner instance this function returns
    a string of rules and ODEs
    
    >>> r = te.loada ('S1 -> S2; k1*S1; k1=1')
    >>> print (te.getODEsFromModel (r))
    """

    from roadrunner import RoadRunner
    if type (sbmlModel) == RoadRunner:
       extractor = _ODEExtractor (sbmlModel.getSBML())
    else:
       raise RuntimeError('The argument to getODEsFromModelAsString should be a roadrunner variable')

    return extractor._toString()

# This is the code that the users doesn't ened to know about

class _Accumulator:
    def __init__(self, species_id):
        self.reaction_map = {}
        self.reactions = []
        self.species_id = species_id

    def _addReaction(self, reaction, stoich):
        rid = reaction.getId()
        if rid in self.reaction_map:
            self.reaction_map[rid]['stoich'] += stoich
        else:
            self.reaction_map[rid] = {
                'reaction': reaction,
                'id': rid,
                'formula': self._getFormula(reaction),
                'stoich': stoich,
            }
            self.reactions.append(rid)

    def _getFormula(self, reaction):
        return reaction.getKineticLaw().getFormula()

    def _toString(self, use_ids=False):
        lhs = 'd{}/dt'.format(self.species_id)
        terms = []
        for rid in self.reactions:
            if abs(self.reaction_map[rid]['stoich']) == 1:
                stoich = ''
            else:
                stoich = str(abs(self.reaction_map[rid]['stoich'])) + '*'

            if len(terms) > 0:
                if self.reaction_map[rid]['stoich'] < 0:
                    op = ' - '
                else:
                    op = ' + '
            else:
                if self.reaction_map[rid]['stoich'] < 0:
                    op = '-'
                else:
                    op = ''

            if use_ids:
                expr = 'v' + self.reaction_map[rid]['id']
            else:
                expr = self.reaction_map[rid]['formula']

            terms.append(op + stoich + expr)

        rhs = ''.join(terms)
        return lhs + ' = ' + rhs

class _ODEExtractor:

    def __init__(self, sbmlStr):

        self.doc = _libsbml.readSBMLFromString (sbmlStr)
        self.model = self.doc.getModel()

        self.species_map = {}
        self.species_symbol_map = {}
        self.use_species_names = False
        self.use_ids = True

        from collections import defaultdict
        self.accumulators = {}
        self.accumulator_list = []

        def reactionParticipant(participant, stoich):
            stoich_sign = 1
            if stoich < 0:
                stoich_sign = -1
            if participant.isSetStoichiometry():
                stoich = participant.getStoichiometry()
            elif participant.isSetStoichiometryMath():
                raise RuntimeError('Stoichiometry math not supported')
            self.accumulators[participant.getSpecies()]._addReaction(r, stoich_sign*stoich)

        newReactant = lambda p: reactionParticipant(p, -1)
        newProduct  = lambda p: reactionParticipant(p, 1)


        for s in (self.model.getSpecies(i) for i in range(self.model.getNumSpecies())):
            self.species_map[s.getId()] = s
            if s.isSetName() and self.use_species_names:
                self.species_symbol_map[s.getId()] = s.getName()
            else:
                self.species_symbol_map[s.getId()] = s.getId()
            a = _Accumulator(s.getId())
            self.accumulators[s.getId()] = a
            self.accumulator_list.append(a)

        for r in (self.model.getReaction(i) for i in range(self.model.getNumReactions())):
            for reactant in (r.getReactant(i) for i in range(r.getNumReactants())):
                newReactant(reactant)
            for product in (r.getProduct(i) for i in range(r.getNumProducts())):
                newProduct(product)

    def _getRules (self):
        r = ''
        for i in range (self.model.getNumRules()):
            if self.model.getRule(i).getType() == 0:
                r += 'd' + self.model.getRule(i).id + '/dt = ' + self.model.getRule(i).formula + '\n'
            if self.model.getRule(i).getType() == 1:
                r += self.model.getRule(i).id + ' = ' + self.model.getRule(i).formula + '\n'
        return r

    def _getKineticLaws (self):
        r = ''
        if self.use_ids:
            r += '\n'
            for rx in (self.model.getReaction(i) for i in range(self.model.getNumReactions())):
                r += 'v' + rx.getId() + ' = ' + rx.getKineticLaw().getFormula().replace(" ", "")  + '\n'
        return r

    def _getRateOfChange (self, index):
        return self.accumulator_list[index]._toString(use_ids=self.use_ids) + '\n'

    def _getRatesOfChange (self):
        r = '\n'
        for a in self.accumulator_list:
            r += a._toString(use_ids=self.use_ids) + '\n'
        return r

    def _toString(self):
        r = self._getRules()
        r = r + self._getKineticLaws() + '\n'
        for index in range (self.model.getNumSpecies()):
            if not self.model.getSpecies (index).boundary_condition:
               r = r + self._getRateOfChange (index)
        return r

def testme():
    """ Run this method to try out the odePrint function"""

    import teUtils as _teUtils

    r = _te.loada('''
        S9' = 999
        x1 := 1+2
        x2 := sin (x1)
        // Reactions:
        J0: $Xo -> 2 E; v;
        J1: ES -> E  + S1; k1*ES*E;
        J2: S1 -> S2 ; k2*S1;
        J3: S2 + 3 E -> 6 ES; k3*S2*E;
        k1 = 0.1; k2 = 0.4; k3 = 0.6;
        v = 0;
        // Species initializations:
        S1 = 100; E = 20; S9 = 1;
    ''')
    odes = getODEsFromModel(r)
    print (odes)


if __name__ == "__main__":
    import teUtils as _teUtils

    r = _te.loada('''
        S9' = 999
        x1 := 1+2
        x2 := sin (x1)
        // Reactions:
        J0: $Xo -> 2 E; v;
        J1: ES -> E  + S1; k1*ES*E;
        J2: S1 -> S2 ; k2*S1;
        J3: S2 + 3 E -> 6 ES; k3*S2*E;
        k1 = 0.1; k2 = 0.4; k3 = 0.6;
        v = 0;
        // Species initializations:
        S1 = 100; E = 20; S9 = 1;
    ''')
    odes = _teUtils.getODEsFromModel(r)
    print (odes)