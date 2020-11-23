# -*- coding: utf-8 -*-
""" A module for creating random network models """

import tellurium as _te
import random as _random
import roadrunner
from   dataclasses import dataclass

__all__ = ['getLinearChain']


# General settings for the package
@dataclass
class Settings:
  """ Settings to control some properties of the network generation"""
  rateConstantScale = 1.0
  """ How much the rate cosntants are scaled by. By default rate constants ge values between 0 and 1.0"""
  allowMassViolatingReactions = False
  """ If set to true, reactions such as A + B -> A are allowed"""

  @dataclass
  class ReactionProbabilities:
         """ Defines the probabilities of generating different reaction mechanisms.
         Current probabilities are:
         
         UniUni = 0.4
         BiUni = 0.3
         UniBi = 0.3
         BiBI  = 0.05
         """
         UniUni = 0.4
         BiUni = 0.3
         UniBi = 0.3
         BiBI  = 0.05

  def restoreDefaultProbabilities ():
      """Restore the default settings for the reaction mechanism propabilities"""
      Settings.ReactionProbabilities.UniUni = 0.4
      Settings.ReactionProbabilities.BiUni = 0.3
      Settings.ReactionProbabilities.UniBi = 0.3
      Settings.ReactionProbabilities.BiBI  = 0.05    

# Return strings
def _getMMRateLaw (k, s1, s2):
    return 'Vm' + str (k) + '/Km' + str (k) + '0*(' + s1 + '-' + s2 + '/Keq' + str (k) + \
    ')/(' + '1 + ' + s1 + '/' + 'Km' + str (k) + '0' + ' + ' \
    + s2 + '/' + 'Km' + str (k) + '1' + ')'

def _getMARateLaw (k, s1, s2):
    return 'k' + str (k) + '0*' + s1 + ' - k' + str (k) + '1' + '*' + s2


def getLinearChain (lengthOfChain, rateLawType='MassAction', keqRatio=5):
    """ Return an Antimony string for a linear chain
    
    Args:     
        lengthOfChain (integer): Length of generated chain, number of reactions       
        rateLawType (string): Optional, can be 'MassAction' (default) or 'Michaelis'
        keqRatio (float): Optional, maximum size of equilibrium constant
         
    Returns:
        string :
           Returns an Antimony string representing the network model
    
    Examples:  

    .. code-block:: python 

       >>> s = teUtils.buildNetworks.getLinearChain (6, rateLawType='MassAction')
       >>> r = te.loada (s)
       >>> r.simulate (0, 50, 100)
       >>> r.plot()
    """
    # Set up a default
    getRateLaw = _getMARateLaw
    n = lengthOfChain
    
    if rateLawType == 'Michaelis':
        getRateLaw = _getMMRateLaw
        
    if rateLawType == 'MassAction':
        getRateLaw = _getMARateLaw
        
        
    model = 'J1: $Xo -> S1; ' + getRateLaw (1, 'Xo', 'S1') + '; \n'
    
    for i in range (n-2):
        r = i + 1
        model += 'J' + str (i+2) + ': S' + str (r) + ' -> ' + 'S' + str (r+1) + '; ' + getRateLaw(r+1, 'S' + str(r), 'S' + str (r+1)) + '; \n'     
    model += 'J' + str (r+2) + ': S' + str(n-1) + ' -> $X1; ' + getRateLaw (n, 'S' + str (r+1), 'X1') + '; \n\n'
       
    if rateLawType == 'Michaelis':
        for i in range (n):
            model += 'Vm' + str (i+1) + ' = ' + str ('{:.2f}'.format (_random.random()*10)) + '\n'
            
        for i in range (n):
            model += 'Km' + str (i+1) + '0' + ' = ' + str ('{:.2f}'.format (_random.random()*10)) + '\n'
            model += 'Km' + str (i+1) + '1' + ' = ' + str ('{:.2f}'.format (_random.random()*10)) + '\n'
        
        for i in range (n):
            model += 'Keq' + str (i+1) + ' = ' + str ('{:.2f}'.format (_random.random()*10)) + '\n'  

    # Initialize values
    if rateLawType == 'MassAction':
       for i in range (n):
           model += 'k' + str (i+1) + '0 = ' + str ('{:.2f}'.format (_random.random()*keqRatio)) + ';  ' + \
           'k' + str (i+1) + '1 = ' + str ('{:.2f}'.format (_random.random()*1)) + '\n'
           
    model += 'Xo = ' + str ('{:.2f}'.format (_random.randint(1, 10))) + '\n' 
    model += 'X1 = 0' + '\n' 
    for i in range (n-1):
        model += 'S' + str (i+1) + ' = 0; '
        if (i+1) % 4 == 0:
           model += '\n'
           
    return model

# ----------------------------------------------------------------------------
"""
Created on Tue May 15 17:39:53 2018

@author: hsauro
"""

# Generate random mass-action networks using uniuni, biuni, unibi and bibi
# The following reaction patterns are currently not allowed:
# X -> X

# The following are allowed if the settings variable allowMassViolatingReactions is set to True
# X + Y -> X
# Y + X -> X 
# X + X -> X

# X -> X + Y
# X -> Y + X
# X -> X + X

# X + X -> X + X
# X + Y -> X + Y
# Y + X -> X + Y
# Y + X -> Y + X
# X + Y -> X + Y
# X + Y -> Y + X

# How to use:
# Easy way:
#   print (getRandomNetwork (nSpecies, nReactions))

# To get access to intermediate results:
#   rl =  _generateReactionList (6, 5)
#   st = _getFullStoichiometryMatrix (rl)
#   stt = _removeBoundaryNodes (st)
#   if len (stt[1]) > 0:
#      antStr = _getAntimonyScript (stt[1], stt[2], rl, isReversible)

# floating and boundary Ids are represented as integers

import numpy as _np
import copy as _copy

@dataclass
class _TReactionType:
      UNIUNI = 0
      BIUNI = 1
      UNIBI = 2
      BIBI = 3
      
     
def _pickReactionType():
       rt = _random.random()
       if rt < Settings.ReactionProbabilities.UniUni:
           return _TReactionType.UNIUNI
       if rt < Settings.ReactionProbabilities.UniUni + Settings.ReactionProbabilities.BiUni:
           return _TReactionType.BIUNI
       if rt < Settings.ReactionProbabilities.UniUni + Settings.ReactionProbabilities.BiUni + Settings.ReactionProbabilities.UniBi:
           return _TReactionType.UNIBI
       return _TReactionType.BIBI
    
    
# Generates a reaction network in the form of a reaction list
# reactionList = [nSpecies, reaction, reaction, ....]
# reaction = [reactionType, [list of reactants], [list of products], rateConstant]
# Disallowed reactions:
# S1 -> S1
# S1 + S2 -> S2  # Can't have the same reactant and product
# S1 + S1 -> S1
def _generateReactionList (nSpecies, nReactions):
    
    reactionList = []
    for r in range(nReactions):
        
       rateConstant = _random.random()*Settings.rateConstantScale
       rt = _pickReactionType()
       if rt == _TReactionType.UNIUNI:
           # UniUni
           reactant = _random.randint (0, nSpecies-1)
           product = _random.randint (0, nSpecies-1)
           # Disallow S1 -> S1 type of reaction
           while product == reactant:
                 product = _random.randint (0, nSpecies-1)
           reactionList.append ([rt, [reactant], [product], rateConstant]) 
               
       if rt == _TReactionType.BIUNI:
           # BiUni
           # Pick two reactants
           reactant1 = _random.randint (0, nSpecies-1)
           reactant2 = _random.randint (0, nSpecies-1)
           if Settings.allowMassViolatingReactions:
              product = _random.randint (0, nSpecies-1)
           else:
             # pick a product but only products that don't include the reactants
             species = range (nSpecies)
             # Remove reactant1 and 2 from the species list
             species = _np.delete (species, [reactant1, reactant2], axis=0)
             # Then pick a product from the reactants that are left
             product = species[_random.randint (0, len (species)-1)]
               
           reactionList.append ([rt, [reactant1, reactant2], [product], rateConstant]) 

       if rt == _TReactionType.UNIBI:
          # UniBi
          reactant1 = _random.randint (0, nSpecies-1)
          if Settings.allowMassViolatingReactions:
             product1 = _random.randint (0, nSpecies-1)
             product2 = _random.randint (0, nSpecies-1)
          else:
             # pick a product but only products that don't include the reactant
             species = range (nSpecies)
             # Remove reactant1 from the species list
             species = _np.delete (species, [reactant1], axis=0)
             # Then pick a product from the reactants that are left
             product1 = species[_random.randint (0, len (species)-1)]
             product2 = species[_random.randint (0, len (species)-1)]
    
          reactionList.append ([rt, [reactant1], [product1, product2], rateConstant]) 

       if rt == _TReactionType.BIBI:
          # BiBi
          reactant1 = _random.randint (0, nSpecies-1)
          reactant2= _random.randint (0, nSpecies-1)
          if Settings.allowMassViolatingReactions:
             product1 = _random.randint (0, nSpecies-1)
             product2 = _random.randint (0, nSpecies-1)
          else:
             # pick a product but only products that don't include the reactant
             species = range (nSpecies)
             # Remove reactant1 and 2 from the species list
             species = _np.delete (species, [reactant1, reactant2], axis=0)
             # Then pick a product from the reactants that are left
             product1 = species[_random.randint (0, len (species)-1)]
             product2 = species[_random.randint (0, len (species)-1)]
               
          element = [rt, [reactant1, reactant2], [product1, product2], rateConstant]
          reactionList.append (element)            

    reactionList.insert (0, nSpecies)
    return reactionList
    

# Includes boundary and floating species
# Returns a list:
# [New Stoichiometry matrix, list of floatingIds, list of boundaryIds]
def _getFullStoichiometryMatrix (reactionList):
    
    nSpecies = reactionList[0]
    reactionListCopy = _copy.deepcopy (reactionList)
    reactionListCopy.pop (0)
    st = _np.zeros ((nSpecies, len(reactionListCopy)))
    
    for index, r in enumerate (reactionListCopy):
        if r[0] == _TReactionType.UNIUNI:
           # UniUni
           reactant = reactionListCopy[index][1][0]
           st[reactant, index] = -1
           product = reactionListCopy[index][2][0]
           st[product, index] = 1
     
        if r[0] == _TReactionType.BIUNI:
            # BiUni
            reactant1 = reactionListCopy[index][1][0]
            st[reactant1, index] = -1
            reactant2 = reactionListCopy[index][1][1]
            st[reactant2, index] = -1
            product = reactionListCopy[index][2][0]
            st[product, index] = 1

        if r[0] == _TReactionType.UNIBI:
            # UniBi
            reactant1 = reactionListCopy[index][1][0]
            st[reactant1, index] = -1
            product1 = reactionListCopy[index][2][0]
            st[product1, index] = 1
            product2 = reactionListCopy[index][2][1]
            st[product2, index] = 1

        if r[0] == _TReactionType.BIBI:
            # BiBi
            reactant1 = reactionListCopy[index][1][0]
            st[reactant1, index] = -1
            reactant2 = reactionListCopy[index][1][1]
            st[reactant2, index] = -1
            product1 = reactionListCopy[index][2][0]
            st[product1, index] = 1
            product2 = reactionListCopy[index][2][1]
            st[product2, index] = 1

    return st   
        

# Removes boundary or orphan species from stoichiometry matrix
def _removeBoundaryNodes (st):
    
    dims = st.shape
    
    nSpecies = dims[0]
    nReactions = dims[1]
    
    speciesIds = _np.arange (nSpecies)
    indexes = []
    orphanSpecies = []
    countBoundarySpecies = 0
    for r in range (nSpecies): 
        # Scan across the columns, count + and - coefficients
        plusCoeff = 0; minusCoeff = 0
        for c in range (nReactions):
            if st[r,c] < 0:
                minusCoeff = minusCoeff + 1
            if st[r,c] > 0:
                plusCoeff = plusCoeff + 1
        if plusCoeff == 0 and minusCoeff == 0:
           # No reaction attached to this species
           orphanSpecies.append (r)
        if plusCoeff == 0 and minusCoeff != 0:
           # Species is a source
           indexes.append (r)
           countBoundarySpecies = countBoundarySpecies + 1
        if minusCoeff == 0 and plusCoeff != 0:
           # Species is a sink
           indexes.append (r)
           countBoundarySpecies = countBoundarySpecies + 1

    floatingIds = _np.delete (speciesIds, indexes+orphanSpecies, axis=0)

    boundaryIds = indexes
    return [_np.delete (st, indexes + orphanSpecies, axis=0), floatingIds, boundaryIds]
    

       
def _getAntimonyScript (floatingIds, boundaryIds, reactionList, isReversible):
    
    nSpecies = reactionList[0]
    # Remove the first element which is the nSpecies
    reactionListCopy = _copy.deepcopy (reactionList)
    reactionListCopy.pop (0)

    antStr = ''
    if len (floatingIds) > 0:
       antStr = antStr + 'var ' + 'S' + str (floatingIds[0])
       for index in floatingIds[1:]:
           antStr = antStr + ', ' + 'S' + str (index)
       antStr = antStr + '\n'
    
    if len (boundaryIds) > 0:
       antStr = antStr + 'ext ' + 'S' + str (boundaryIds[0])
       for index in boundaryIds[1:]:
           antStr = antStr + ', ' + 'S' + str (index)
       antStr = antStr + ';\n'
    
    for index, r in enumerate (reactionListCopy):
        antStr = antStr + 'J' + str (index) + ': '
        if r[0] == _TReactionType.UNIUNI:
           # UniUni
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + '; E' + str (index) + '*(k' + str (index) + '*S' + str (reactionListCopy[index][1][0])
           if isReversible:
              antStr = antStr + ' - k' + str (index) + 'r' + '*S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ')'
        if r[0] == _TReactionType.BIUNI:
           # BiUni
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][1][1])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + '; E' + str (index) + '*(k' + str (index) + '*S' + str (reactionListCopy[index][1][0]) + '*S' + str (reactionListCopy[index][1][1])
           if isReversible:
             antStr = antStr + ' - k' + str (index) + 'r' + '*S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ')'
        if r[0] == _TReactionType.UNIBI:
           # UniBi
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][1])
           antStr = antStr + '; E' + str (index) + '*(k' + str (index) + '*S' + str (reactionListCopy[index][1][0])
           if isReversible:
             antStr = antStr + ' - k' + str (index) + 'r' + '*S' + str (reactionListCopy[index][2][0]) + '*S' + str (reactionListCopy[index][2][1])
           antStr = antStr + ')'
        if r[0] == _TReactionType.BIBI:
           # BiBi
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][1][1])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][1])  
           antStr = antStr + '; E' + str (index) + '*(k' + str (index) + '*S' + str (reactionListCopy[index][1][0]) + '*S' + str (reactionListCopy[index][1][1])
           if isReversible:
             antStr = antStr + ' - k' + str (index) + 'r' + '*S' + str (reactionListCopy[index][2][0]) + '*S' + str (reactionListCopy[index][2][1])
           antStr = antStr + ')'
        antStr = antStr + ';\n'

    antStr = antStr + '\n'
    for index, r in enumerate (reactionListCopy):
        antStr = antStr + 'k' + str (index) + ' = ' + str (r[3]) + '\n'
        if isReversible:
           antStr = antStr + 'k' + str (index) + 'r = ' + str (_random.random()*Settings.rateConstantScale) + '\n'       
        
    antStr = antStr + '\n'
    for index, r in enumerate (reactionListCopy):
        antStr = antStr + 'E' + str (index) + ' = 1\n'
 
    antStr = antStr + '\n'
    for index, b in enumerate (boundaryIds):
        antStr = antStr + 'S' + str (b) + ' = ' + str (_random.randint (1,6)) + '\n'
        
    antStr = antStr + '\n'
    for index, b in enumerate (floatingIds):
        antStr = antStr + 'S' + str (b) + ' = ' + str (_random.randint (1,6)) + '\n'

    return antStr       
     

def getRandomNetwork (nSpecies, nReactions, isReversible=False, returnStoichiometryMatrix=False, returnFullStoichiometryMatrix=False):  
    """
    Generate a random network using uniuni, unibi, biuni, and bibi reactions.
    All reactions are governed by mass-action kinetics. User can set the maximum
    number of reactions and species. 
      
    Args:
         nSpecies (integer): Maximum number of species       
         nreaction (integer): Maximum number of reactions
         isReversible (boolean): Set True if the reactions should be reversible  
         returnStoichiometryMatrix (boolean): Set True to make the function return the stoichiometry matrix that
             only inludes the floating species. If you want the full stoichiometriy matrix that includes the boundary
             species as well, set the returnFullStoichiometryMatrix to True
         returnFullStoichiometryMatrix (boolean): Set True if you want the full stoichometry matrix returned. The 
             full matrix will include any boundary species in the network.
               
    Returns:
        string :
           Returns an Antimony string representing the network model
    
    Examples::

       >>> model = getRandomNetwork (6, 9)
       >>> r = te.loada(model)
       >>> m = r.simulate (0, 10, 100)   
       
       >>> model = getRandomNetwork (6, 7, returnStoichiometryMatrix=True)

         array([[ 0.,  0.,  1.,  0., -1.,  0.,  0.],
               [ 1.,  0.,  0.,  1.,  0., -1.,  1.],
               [-1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  1.,  0.,  0.,  0., -1.],
               [ 0., -1.,  0., -1.,  0.,  1.,  0.],
               [ 0.,  0., -1.,  0.,  1.,  0.,  0.]])
    """ 
    roadrunner.Logger_disableConsoleLogging()
    roadrunner.Config_setValue (roadrunner.Config.ROADRUNNER_DISABLE_WARNINGS, True)

    rl = _generateReactionList (nSpecies, nReactions)  
    st = _getFullStoichiometryMatrix (rl)
    
    if returnFullStoichiometryMatrix:
       return st
    
    stt = _removeBoundaryNodes (st)
    if returnStoichiometryMatrix:
       return stt[0]
   
    if len (stt[1]) > 0:
       return _getAntimonyScript (stt[1], stt[2], rl, isReversible)
    else:
       return ""

if __name__ == '__main__' :
   # import heat map code 
   import teUtils as _teUtils
   
   roadrunner.Logger_disableConsoleLogging()
   roadrunner.Config_setValue (roadrunner.Config.ROADRUNNER_DISABLE_WARNINGS, True)
    
   mod = getLinearChain (9, rateLawType='MassAction', keqRatio=2)
   print (mod)
   r = _te.loada (mod)
   m = r.simulate (0, 100, 200)
   r.plot()
   _teUtils.plotting.plotFluxControlHeatMap (r)

   numBadModels = 0
   for i in range (5):
       rl = _generateReactionList (8, 8)
       st = _getFullStoichiometryMatrix (rl)
       stt = _removeBoundaryNodes (st)
       if len (stt[1]) > 0:
          antStr = _getAntimonyScript (stt[1], stt[2], rl, isReversible=True)
          r = _te.loada(antStr)
          m = r.simulate (0, 10, 100)
          try:
            r.steadyState()
            print (antStr)
            r.plot()
          except:
              print ("Bad Model")
              numBadModels = numBadModels + 1
          print ("Network = ", i)
       else:
          print ('No floating species in the network')
   print ("Number of bad models = ", numBadModels)
    
