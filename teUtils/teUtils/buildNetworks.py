# -*- coding: utf-8 -*-
""" Build Module for creating random network models """

import tellurium as _te
import random as _random

__all__ = ['getLinearChain']

def _getMMRateLaw (k, s1, s2):
    return 'Vm' + str (k) + '/Km' + str (k) + '0*(' + s1 + '-' + s2 + '/Keq' + str (k) + \
    ')/(' + '1 + ' + s1 + '/' + 'Km' + str (k) + '0' + ' + ' \
    + s2 + '/' + 'Km' + str (k) + '1' + ')'

def _getMARateLaw (k, s1, s2):
    return 'k' + str (k) + '0*' + s1 + ' - k' + str (k) + '1' + '*' + s2


def getLinearChain (lengthOfChain, rateLawType='MassAction', keqRatio=5):
    """ Return an Antimony string for a linear chain
    
    Parameters 
    ----------      
        arg1 (integer): Length of generated chain, number of reactions
         
        arg2 (rateLawType String): Optional, can be 'MassAction' (default) or 'Michaelis'
  
        arg3 (float): Optional, maximum size of equilibrium constant
         
    Return
    ------
    result: Antimony string
    
    Example
    -------     
    >>> s = teUtils.buildNetworks.getLinearChain ('MassAction', 6)
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
#      antStr = _genAntimonyScript (stt[1], stt[2], rl)

# floating and boundary Ids are represented as integers

import numpy as _np
import copy as _copy

class _TReactionType:
      UNIUNI = 0
      BIUNI = 1
      UNIBI = 2
      BIBI = 3
      
class _TReactionProbabilities:
       UniUni = 0.4
       BiUni = 0.3
       UniBi = 0.3
       BiBI  = 0.05
     
      
def _pickReactionType():
       rt = _random.random()
       if rt < _TReactionProbabilities.UniUni:
           return _TReactionType.UNIUNI
       if rt < _TReactionProbabilities.UniUni + _TReactionProbabilities.BiUni:
           return _TReactionType.BIUNI
       if rt < _TReactionProbabilities.UniUni + _TReactionProbabilities.BiUni + _TReactionProbabilities.UniBi:
           return _TReactionType.UNIBI
       return _TReactionType.BIBI
    
    
# Generates a reaction network in the form of a reaction list
# reactionList = [nSpecies, reaction, ....]
# reaction = [reactionType, [list of reactants], [list of product], rateConstant]
def generateReactionList (nSpecies, nReactions):
    
    reactionList = []
    for r in range(nReactions):
        
       rateConstant = _random.random()
       rt = _pickReactionType()
       if rt == _TReactionType.UNIUNI:
           # UniUni
           reactant = _random.randint (0, nSpecies-1)
           product = _random.randint (0, nSpecies-1)
           while product == reactant:
                 product = _random.randint (0, nSpecies-1)
           reactionList.append ([rt, [reactant], [product], rateConstant]) 
               
       if rt == _TReactionType.BIUNI:
           # BiUni
           # Pick two reactants
           reactant1 = _random.randint (0, nSpecies-1)
           reactant2 = _random.randint (0, nSpecies-1)
           # pick a product but only products that don't include the reactants
           species = range (nSpecies)
           # Remove reactant1 and 2 from list
           species = _np.delete (species, [reactant1, reactant2], axis=0)
           product = species[_random.randint (0, len (species)-1)]
               
           reactionList.append ([rt, [reactant1, reactant2], [product], rateConstant]) 

       if rt == _TReactionType.UNIBI:
           # UniBi
           reactant1 = _random.randint (0, nSpecies-1)
           # pick a product but only products that don't include the reactant
           species = range (nSpecies)
           # Remove reactant1 from the list
           species = _np.delete (species, [reactant1], axis=0)
           product1 = species[_random.randint (0, len (species)-1)]
           product2 = species[_random.randint (0, len (species)-1)]
  
           reactionList.append ([rt, [reactant1], [product1, product2], rateConstant]) 

       if rt == _TReactionType.BIBI:
           # BiBi
           reactant1 = _random.randint (0, nSpecies-1)
           reactant2= _random.randint (0, nSpecies-1)
           # pick a product but only products that don't include the reactant
           species = range (nSpecies)
           # Remove reactant1 and 2 from list
           species = _np.delete (species, [reactant1, reactant2], axis=0)
           product1 = species[_random.randint (0, len (species)-1)]
           product2 = species[_random.randint (0, len (species)-1)]
               
           element = [rt, [reactant1, reactant2], [product1, product2], rateConstant]
           reactionList.append (element)            

    reactionList.insert (0, nSpecies)
    return reactionList
    

# Include boundary and floating species
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
    

       
def _genAntimonyScript (floatingIds, boundaryIds, reactionList):
    
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
        if r[0] == _TReactionType.UNIUNI:
           # UniUni
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + '; k' + str (index) + '*S' + str (reactionListCopy[index][1][0])
        if r[0] == _TReactionType.BIUNI:
           # BiUni
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][1][1])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + '; k' + str (index) + '*S' + str (reactionListCopy[index][1][0]) + '*S' + str (reactionListCopy[index][1][1])
        if r[0] == _TReactionType.UNIBI:
           # UniBi
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][1])
           antStr = antStr + '; k' + str (index) + '*S' + str (reactionListCopy[index][1][0])
        if r[0] == _TReactionType.BIBI:
           # BiBi
           antStr = antStr + 'S' + str (reactionListCopy[index][1][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][1][1])
           antStr = antStr + ' -> '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][0])
           antStr = antStr + ' + '
           antStr = antStr + 'S' + str (reactionListCopy[index][2][1])  
           antStr = antStr + '; k' + str (index) + '*S' + str (reactionListCopy[index][1][0]) + '*S' + str (reactionListCopy[index][1][1])
        antStr = antStr + ';\n'

    antStr = antStr + '\n'
    for index, r in enumerate (reactionListCopy):
        antStr = antStr + 'k' + str (index) + ' = ' + str (r[3]) + '\n'
        
    antStr = antStr + '\n'
    for index, b in enumerate (boundaryIds):
        antStr = antStr + 'S' + str (b) + ' = ' + str (_random.randint (1,6)) + '\n'
        
    return antStr       
     

def getRandomNetwork (nSpecies, nReactions):  
    """
    Generate a random network using uniuni, unibi, biuni, and bibi reactions.
    All reactions are governed by mass-action kinetics. User can set the maximum
    number of reactions and species. 
      
    Parameters 
    ----------
         arg1 (nSpecies integer): Maximum number of species
         
         arg2 (nreaction integer): Maximum number of reactions
         
         
    Return
    ------
        result: Antimony network string

    Example
    -------
    >>> model = getRandomNetwork (6, 9)
    >>> r = te.loada(model)
    >>> m = r.simulate (0, 10, 100)      
    """
    rl =  generateReactionList (nSpecies, nReactions)  
    st = _getFullStoichiometryMatrix (rl)
    stt = _removeBoundaryNodes (st)
    if len (stt[1]) > 0:
       return _genAntimonyScript (stt[1], stt[2], rl)
    else:
       return ""

if __name__ == '__main__' :
   # import heat map code 
   import teUtils as _teUtils
   
   mod = getLinearChain ('MassAction', 9, keqRatio=2)
   print (mod)
   r = _te.loada (mod)
   m = r.simulate (0, 100, 200)
   r.plot()
   _teUtils.plotting.plotFluxControlHeatMap (r)

   numBadModels = 0
   for i in range (5):
       rl =  _generateReactionList (8, 8)
       st = _getFullStoichiometryMatrix (rl)
       stt = _removeBoundaryNodes (st)
       if len (stt[1]) > 0:
          antStr = _genAntimonyScript (stt[1], stt[2], rl)
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
    
