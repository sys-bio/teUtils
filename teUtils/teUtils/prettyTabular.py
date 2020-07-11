# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 09:43:05 2018

@author: hsauro
"""

# Let's only support 3.x series
#from __future__ import absolute_import, division, print_function, unicode_literals

from tabulate import tabulate as _tabulate
import tellurium as _te
import teUtils as _teUtils

def tabulateConcentrations(r, fmt='psql'):
    '''
    Display the concentrations in a neat table
       
    Argument
    --------
        r: roadrunner instance

    >>> print (teUtils.prettyTabular.tabulateConcentrations (r))
    '''

    c = r.getFloatingSpeciesConcentrations()
    ids = r.getIndependentFloatingSpeciesIds()

    alist = []
    for id, value in zip (ids, c):
        alist.append ([id, value])
    print (_tabulate (alist, ['Id', 'Concentration'], tablefmt=fmt))


def tabulateFluxes(r, fmt='psql'):
    '''
    Display the fluxes in a neat table

    Argument
    --------
        r: roadrunner instance

    >>> print (teUtils.prettyTabular.tabulateFluxes (r))
    '''
    c = r.getReactionRates()
    ids = r.getReactionIds();

    alist = []
    for id, value in zip (ids, c):
        alist.append ([id, value])
    print (_tabulate (alist, ['Id', 'Reaction Rates'], tablefmt=fmt))
   
def testme():
    """ Run this to try out the methods"""

    r = _te.loada("""
         J1: $Xo -> S1;  k1*Xo - k11*S1;
         J2:  S1 -> S2;  k2*S1 - k22*S2;
         J3:  S2 -> S3;  k3*S2 - k33*S3;
         J4:  S3 -> S4;  k3*S3 - k44*S4;
         J5:  S4 -> S5;  k4*S4 - k44*S5;
         J6:  S5 -> S6;  k5*S5 - k55*S6;
         J7:  S6 -> S7;  k4*S6 - k44*S7;
         J8:  S7 -> S8;  k3*S7 - k33*S8;
         J9:  S8 -> ;    k4*S8;
          
          k1 = 0.3;  k11 = 0.26;
          k2 = 0.5;  k22 = 0.41;
          k3 = 0.27; k33 = 0.12;
          k4 = 0.9;  k44 = 0.56
          k5 = 0.14; k55 = 0.02
          Xo = 10;
    """)
    r.simulate (0, 10, 10)
    _teUtils.prettyTabular.tabulateConcentrations (r)
    _teUtils.prettyTabular.tabulateFluxes (r)

    
if __name__ == "__main__":

    r = _te.loada("""
         J1: $Xo -> S1;  k1*Xo - k11*S1;
         J2:  S1 -> S2;  k2*S1 - k22*S2;
         J3:  S2 -> S3;  k3*S2 - k33*S3;
         J4:  S3 -> S4;  k3*S3 - k44*S4;
         J5:  S4 -> S5;  k4*S4 - k44*S5;
         J6:  S5 -> S6;  k5*S5 - k55*S6;
         J7:  S6 -> S7;  k4*S6 - k44*S7;
         J8:  S7 -> S8;  k3*S7 - k33*S8;
         J9:  S8 -> ;    k4*S8;
          
          k1 = 0.3;  k11 = 0.26;
          k2 = 0.5;  k22 = 0.41;
          k3 = 0.27; k33 = 0.12;
          k4 = 0.9;  k44 = 0.56
          k5 = 0.14; k55 = 0.02
          Xo = 10;
    """)
    
    m = r.simulate (0, 100, 200)
    _teUtils.prettyTabular.tabulateConcentrations (r)
    _teUtils.prettyTabular.tabulateFluxes (r)