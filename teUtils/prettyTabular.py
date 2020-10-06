# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 09:43:05 2018
@author: hsauro
"""

from tabulate import tabulate as _tabulate
import tellurium as _te

def tabulateConcentrations(r, fmt='psql'):
    '''
    Display the current concentrations in a neat table
       
    Args:
        r (roadrunner instance): Roadruner variable

    Example:

    .. code-block:: text

       >>> print (teUtils.prettyTabular.tabulateConcentrations (r))
       +------+-----------------+
       | Id   |   Concentration |
       |------+-----------------|
       | S1   |        8.51577  |
       | S3   |        8.46827  |
       | S5   |       12.5046   |
       | S7   |        4.6257   |
       | S8   |        6.03088  |
       | S2   |        2.92542  |
       | S6   |        3.29835  |
       | S4   |        0.873088 |
       +------+-----------------+
    '''

    c = r.getFloatingSpeciesConcentrations()
    ids = r.getIndependentFloatingSpeciesIds()

    alist = []
    for id, value in zip (ids, c):
        alist.append ([id, value])
    print (_tabulate (alist, ['Id', 'Concentration'], tablefmt=fmt))


def tabulateFluxes(r, fmt='psql'):
    '''
    Display the current reaction in a neat table

   Args:
        r (roadrunner instance): Roadruner variable

   Example:

    .. code-block:: text

       >>> print (teUtils.prettyTabular.tabulateFluxes (r))
       +------+------------------+
       | Id   |   Reaction Rates |
       |------+------------------|
       | J1   |         0.7859   |
       | J2   |         0.785893 |
       | J3   |         0.785882 |
       | J4   |         0.78585  |
       | J5   |         0.785835 |
       | J6   |         0.785815 |
       | J7   |         0.785801 |
       | J8   |         0.785784 |
       | J9   |         0.785779 |
       +------+------------------+
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

    import teUtils
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
    teUtils.prettyTabular.tabulateConcentrations (r)
    teUtils.prettyTabular.tabulateFluxes (r)