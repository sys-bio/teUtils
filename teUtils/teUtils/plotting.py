# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 09:32:22 2018

@author: hsauro
"""

# Let's only support 3.x series
#from __future__ import absolute_import, division, print_function, unicode_literals

import tellurium as _te

from mpl_toolkits.mplot3d import Axes3D as _Axes3D
import numpy as _np
import matplotlib.pyplot as _plt
import teUtils as _teUtils

def plotAsciiConcentrationsBar (r, scale=5):
    '''
    Display the floating species concentrations as an ASCII bar chart.
    
    Argument
    --------
        r : reference 
            roadrunner instance
        scale : integer
            optional parameter to scale the ascii bar graph

    >>> teUtils.prettyTabular.plotAsciiConcentrationsBar (r, scale=20)
    '''
    
    import math
    c = r.getFloatingSpeciesConcentrations()
    ids = r.getFloatingSpeciesIds()

    maxString = len (max(ids, key=len))

    for value in range (len (c)):
        print ('{:{X}.{Y}}'.format (ids[value], X=maxString, Y=maxString), ':', math.trunc (scale*c[value])*'*')


def plotAsciiReactionRatesBar (r, scale=5):
    '''
    Display the reaction rates as an ASCII bar chart.

    Argument
    --------
        r : reference
              roadrunner instance
        scale : integer
              optional parameter to scale the ascii bar graph

    >>> teUtils.prettyTabular.plotAsciiReactionRatesBar (r, scale=20)
    '''

    import math
    c = r.getReactionRates()
    ids = r.getReactionIds()

    maxString = len (max(ids, key=len))

    for value in range (len (c)):
        print ('{:{X}.{Y}}'.format (ids[value], X=maxString, Y=maxString), ':', math.trunc (scale*c[value])*'*')



def plotConcentrationControlHeatMap (r, pdfExport=None):
    '''
    Display the concentation control coefficients as a heat map
    
    Arguments
    ---------
        r : reference
            roadrunner instance
        pdfExport : string
            optional parameter, if present it should indicate the filename to export the heat map image to in the form of pdf

    >>> teUtils.prettyTabular.plotConcentrationControlHeatMap (r, pdfExport='heapmap.pdf')
    '''

    import seaborn as sns
    import pandas as pd
    hist = r.getScaledConcentrationControlCoefficientMatrix()

    ss = r.getFloatingSpeciesIds()
    rr = r.getReactionIds()

    df = pd.DataFrame (hist, columns=rr, index=ss)

    f, ax = _plt.subplots(figsize=(9, 6))
    hp = sns.heatmap(df, annot=True, fmt="5.2f", linewidths=.5, ax=ax,cmap='bwr')
    if pdfExport != None:
        f.savefig(pdfExport)

    
def plotFluxControlHeatMap (r, pdfExport=None):
    '''
    Display the flux control coefficients as a heat map
    
    Arguments
    ---------
        r : reference
           roadrunner instance
        pdfExport : string
           optional parameter, if present it should indicate the filename to export the heat map image to in the form of pdf

    >>> teUtils.prettyTabular.plotFluxControlHeatMap (r, pdfExport='heapmap.pdf')
    '''

    import seaborn as sns
    import pandas as pd
    
    hist = r.getScaledFluxControlCoefficientMatrix()

    ss = r.getReactionIds()
    rr = r.getReactionIds()

    df = pd.DataFrame (hist,columns=rr, index=ss)

    f, ax = _plt.subplots(figsize=(9, 6))
    hp = sns.heatmap(df, annot=True, fmt="5.2f", linewidths=.5, vmin=-1, vmax=1, ax=ax,cmap='bwr')

    if pdfExport != None:
        f.savefig(pdfExport)

    
def plotConcentrationControlIn3D (r, upperLimit=1, lowerLimit=-1):
    '''
    Display the concentation control coefficients as a 3D plot
    
    Arguments
    ---------
        r : reference
           roadrunner instance
        upperlimit : float 
           optional parameter, sets the lower z axis limit
        upperlimit : float
           optional parameter, sets the upper z axis limit

    >>> teUtils.prettyTabular.plotConcentrationControlIn3D (r)
    '''

    import matplotlib.colors as colors
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    fig = _plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    hist = r.getScaledConcentrationControlCoefficientMatrix()
    
    xedges = _np.arange (float (hist.shape[0]) + 1)
    yedges = _np.arange (float (hist.shape[1]) + 1)
    
    # Construct arrays for the anchor positions
    # Note: _np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
    # ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
    # with indexing='ij'.
    xpos, ypos = _np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
    xpos = xpos.flatten('F')
    ypos = ypos.flatten('F')
    zpos = _np.zeros_like(xpos)
    
    # Construct arrays with the dimensions for the 16 bars.
    dx = 0.5 * _np.ones_like(zpos)
    dy = dx.copy()
    dz = hist.flatten()
    
    offset = dz + _np.abs(dz.min())
    fracs = offset.astype(float)/offset.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
    colors = cm.YlOrRd (norm(fracs))
    
    ax.set_zlim3d(lowerLimit, upperLimit)
    ax.set_zlabel('Control Coefficient')
    ax.set_xlabel('Species')
    ax.set_ylabel('Enzymes')
    ax.w_xaxis.set_ticks(_np.arange (float (hist.shape[0]) + 1))
    ax.w_xaxis.set_ticklabels(r.getFloatingSpeciesIds())
    ax.w_yaxis.set_ticks(_np.arange (float (hist.shape[1]) + 1))
    ax.w_yaxis.set_ticks(ypos + dy/2.)
    ax.w_yaxis.set_ticklabels(r.getReactionIds())

    ax.bar3d (xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average') 
    
    
def plotFluxControlIn3D (r, upperLimit=1, lowerLimit=-1):
    '''
    Display the flux control coefficients as a 3D plot

    Arguments
    ---------
        r : reference
           roadrunner instance
        upperlimit : float 
           optional parameter, sets the lower z axis limit
        upperlimit : float
           optional parameter, sets the upper z axis limit

    >>> teUtils.prettyTabular.plotFluxControlIn3D (r)
    '''

    import matplotlib.cm as cm
    import matplotlib.colors as colors
        
    fig = _plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    hist = r.getScaledFluxControlCoefficientMatrix()
    
    xedges = _np.arange (float (hist.shape[0]) + 1)
    yedges = _np.arange (float (hist.shape[1]) + 1)
    
    # Construct arrays for the anchor positions
    # Note: _np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
    # ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
    # with indexing='ij'.
    xpos, ypos = _np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
    xpos = xpos.flatten('F')
    ypos = ypos.flatten('F')
    zpos = _np.zeros_like(xpos)
    
    # Construct arrays with the dimensions for the 16 bars.
    dx = 0.5 * _np.ones_like(zpos)
    dy = dx.copy()
    dz = hist.flatten()
    
    offset = dz + _np.abs(dz.min())
    fracs = offset.astype(float)/offset.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
    colors = cm.YlOrRd (norm(fracs))
    
    ax.set_zlim3d(lowerLimit, upperLimit)
    ax.set_zlabel('Control Coefficient')
    ax.set_xlabel('Fluxes')
    ax.set_ylabel('Enzymes')
    ax.w_xaxis.set_ticks(_np.arange (float (hist.shape[0]) + 1))
    ax.w_xaxis.set_ticklabels(r.getReactionIds())
    ax.w_yaxis.set_ticks(_np.arange (float (hist.shape[1]) + 1))
    ax.w_yaxis.set_ticks(ypos + dy/2.)
    ax.w_yaxis.set_ticklabels(r.getReactionIds())

    ax.bar3d (xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average') 
    
    
def plotFloatingSpecies (r, width=12, height=6):
    '''
    Plots a graph bar graph of the floating species concentrations.
    
    Arguments
    ---------
        r : reference
           roadrunner instance
        width : float
           optional width in inches of the plot
        height : float
           optional height in inches of the plot

    >>> teUtils.prettyTabular.plotFloatingSpecies (r)
    '''
    import matplotlib.pyplot as plt
    
    xlabels = r.getFloatingSpeciesIds()
    concs = r.getFloatingSpeciesConcentrations()
    _plt.figure(figsize=(width,height))    
    _plt.bar(xlabels, concs, label=xlabels)
    _plt.xticks(range (len (xlabels)), xlabels,  ha='right', rotation=45)    

# ---------------------------------------------------------------------
# Plotting Utilities
# ---------------------------------------------------------------------
def plotArray(result, loc='upper right', show=True, resetColorCycle=True,
             xlabel=None, ylabel=None, title=None, xlim=None, ylim=None,
             xscale='linear', yscale="linear", grid=False, labels=None, **kwargs):
    """ Plot an array.
    The first column of the array must be the x-axis and remaining columns the y-axis. Returns
    a handle to the plotting object. Note that you can add plotting options as named key values after
    the array. To add a legend, include the label legend values:
    te.plotArray (m, labels=['Label 1, 'Label 2', etc])
    Make sure you include as many labels as there are curves to plot!
    Use show=False to add multiple curves. Use color='red' to use the same color for every curve.
    ::
        import numpy as np
        result = _np.array([[1,2,3], [7.2,6.5,8.8], [9.8, 6.5, 4.3]])
        te.plotArray(result, title="My graph', xlim=((0, 5)))
    """

    # FIXME: unify r.plot & _te.plot (lots of code duplication)
    # reset color cycle (columns in repeated simulations have same color)
    if resetColorCycle:
        _plt.gca().set_prop_cycle(None)

    if 'linewidth' not in kwargs:
            kwargs['linewidth'] = 2.0

    # get the labeles
    Ncol = result.shape[1]
    if labels is None:
        labels = result.dtype.names

    for k in range(1, Ncol):
        if loc is None or labels is None:
            # no legend or labels
            p = _plt.plot(result[:, 0], result[:, k], **kwargs)
        else:
            p = _plt.plot(result[:, 0], result[:, k], label=labels[k-1], **kwargs)

    # labels
    if xlabel is not None:
        _plt.xlabel(xlabel)
    if ylabel is not None:
        _plt.ylabel(ylabel)
    if title is not None:
        _plt.title(title)
    if xlim is not None:
        _plt.xlim(xlim)
    if ylim is not None:
        _plt.ylim(ylim)
    # axis and grids
    _plt.xscale(xscale)
    _plt.yscale(yscale)
    _plt.grid(grid)

    # show legend
    if loc is not None and labels is not None:
        _plt.legend(loc=loc)
    # show plot
    if show:
        _plt.show()
    return p


def plotWithLegend(r, result=None, loc='upper left', show=True, **kwargs):
    return r.plot(result=result, loc=loc, show=show, **kwargs)

def testme():
    """ Call this method to try out the methods in this module"""

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

    r.steadyState()
    _teUtils.plotting.plotFloatingSpecies (r, width=6,height=3)
    
    _teUtils.plotting.plotConcentrationControlIn3D (r)
    _teUtils.plotting.plotFluxControlIn3D (r, lowerLimit=0)
    
    _teUtils.plotting.plotConcentrationControlHeatMap (r)
    _teUtils.plotting.plotFluxControlHeatMap (r)


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
    
    m = r.simulate(0, 100,200)
    _teUtils.plotting.plotArray (m)
    _teUtils.plotting.plotWithLegend (r, m)
    
    r.steadyState()
    _teUtils.plotting.plotFloatingSpecies (r, width=6,height=3)
    
    _teUtils.plotting.plotConcentrationControlIn3D (r)
    _teUtils.plotting.plotFluxControlIn3D (r, lowerLimit=0)
    
    _teUtils.plotting.plotConcentrationControlHeatMap (r)
    _teUtils.plotting.plotFluxControlHeatMap (r)
    



