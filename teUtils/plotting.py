# -*- coding: utf-8 -*-
#
# Created on Tue Jan 16 09:32:22 2018
#
# @author: hsauro

# ---------------------------------------------------------------------
# Plotting Utilities
# ---------------------------------------------------------------------

import tellurium as _te

from mpl_toolkits.mplot3d import Axes3D as _Axes3D
import numpy as _np
import matplotlib.pyplot as _plt 
import random

def plotAsciiConcentrationsBar (r, scale=5):
    '''
    Display the floating species concentrations as an ASCII bar chart.
    
    Args:
    -----
        r : reference 
            roadrunner instance
        scale : integer
            optional parameter to scale the ascii bar graph

    Example:
       >>> teUtils.plotting.plotAsciiConcentrationsBar (r, scale=20)
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

    Args:
    -----
        r : reference
              roadrunner instance
        scale : integer
              optional parameter to scale the ascii bar graph

    Example:
       >>> teUtils.plotting.plotAsciiReactionRatesBar (r, scale=20)
    '''

    import math
    c = r.getReactionRates()
    ids = r.getReactionIds()

    maxString = len (max(ids, key=len))

    for value in range (len (c)):
        print ('{:{X}.{Y}}'.format (ids[value], X=maxString, Y=maxString), ':', math.trunc (scale*c[value])*'*')


def plotRandSimGrid  (r, species=[], pdfExport=None, figsize=(11,8), maxRange=10, endTime=200, numPoints=500, ngrid=20):
    '''
    Plots a grid of simulations, each simulation is based on the same model
    but randomly drawn parameter values. 
    
    Args:
        r : reference
           roadrunner instance
        figsize : tuple of float
           optional: width and heigh of plot in inches
        endtime : double
           optional: time to simulate to
        numPoints: double
           optional: numberof points to generate for the plot
        ngrid : integer
           optional: the size of the grid, default is 20 x 20 plots
        maxRange: double
           optional: upper range for randomly drawn parameter values
        pdfExport : string
            optional parameter, indicates the filename to export the plot as a pdf file

    Example:
      >>> teUtils.plotting.plotPhasePortraitGrid (r)
    '''
    print ("Starting....")
    slist = sorted (r.getFloatingSpeciesIds())
    if species == []:
       n = r.getNumFloatingSpecies()
    else:
       slist = species
       n = len (species) + 1
    slist = ['time'] + slist
    print ('Creating subplots (will take a while for a large grid)...')
    fig, axarr = _plt.subplots(ngrid, ngrid, figsize=figsize)
    print ("Adjust subplots...")
    fig.subplots_adjust (wspace=0.15, hspace=0.15)

    print ("Run simulations and populate grid....")
    count = 0
    for i in range(ngrid):
        for j in range(ngrid):
            r.reset()
            for k in r.getGlobalParameterIds():
                r[k] = random.random()*maxRange
             
            m = r.simulate (0, endTime, numPoints, slist)
            count += 1
            ax = _plt.subplot2grid ((ngrid,ngrid), (i,j))
            if i==n-1:
               ax.set_xlabel ('Time') 
               ax.set_xticklabels([])
            else:
               ax.set_xticklabels([])
               ax.set_xticks([])
            if j == 0:
            
               ax.set_yticklabels([])
            else:
               ax.set_yticks([])

            for k in range (n-1):
                ax.plot (m[:,0],m[:,k+1])
                
    if pdfExport != None:
        fig.savefig(pdfExport)                

def plotPhasePortraitGrid  (r, pdfExport=None, figsize=(11,8), endTime=200, numPoints=500):
    '''
    Plots a grid of phase portraits of the floating species concentrations.
    
    Args:
        r : reference
           roadrunner instance
        figsize : tuple of float
           optional: width and heigh of plot in inches
        endtime : double
           optional: time to simulate to
        numPoints: double
           optional: numberof points to generate for the plot
        pdfExport : string
            optional parameter, indicates the filename to export the plot as a pdf file

    Example:
      >>> teUtils.plotting.plotPhasePortraitGrid (r)
    '''
    print ("Starting....")
    slist = sorted (r.getFloatingSpeciesIds())
    r.reset()
    print ('Run simulation...')
    m = r.simulate (0, endTime, numPoints, slist)
    n = r.getNumFloatingSpecies()
    print ('Creating subplots (will take a while for a large grid)...')
    fig, axarr = _plt.subplots(n, n, figsize=figsize)
    print ("Adjust subplots...")
    fig.subplots_adjust (wspace=0.15, hspace=0.15)

    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
            ax = _plt.subplot2grid ((n,n), (i,j))
            if i==n-1:
               ax.set_xlabel (slist[j]) 
               ax.set_xticklabels([])
            else:
               ax.set_xticklabels([])
               ax.set_xticks([])
            if j == 0:
               ax.set_ylabel (slist[i])              
               ax.set_yticklabels([])
            else:
               ax.set_yticklabels([])
               ax.set_yticks([])

            ax.plot (m[:,i], m[:,j])

    if pdfExport != None:
        fig.savefig(pdfExport)
        
def plotConcentrationControlHeatMap (r, pdfExport=None, annotations=True, figsize=(13,7), vmin=-1, vmax=1):
    '''
    Display the concentation control coefficients as a heat map
    
    Args:
        r : reference
            roadrunner instance
        pdfExport : string
            optional: indicates the filename to export the heat map image to in the form of pdf
        annotations (boolean), 
            optional : used to draw values on teh heatmap cells
        figsize : tutle of double
            optional: sets the size of the plot, eg figsize=(10,5)
        vmin and vmax : double
            optional: set the lower and upper limits for the range

    Example:
      >>> teUtils.plotting.plotConcentrationControlHeatMap (r, pdfExport='heapmap.pdf')
    '''

    import seaborn as sns
    import pandas as pd
    hist = r.getScaledConcentrationControlCoefficientMatrix()

    ss = r.getFloatingSpeciesIds()
    rr = ["E" + str(x) for x in range (r.getNumReactions())]

    df = pd.DataFrame (hist, columns=rr, index=ss)

    f, ax = _plt.subplots(figsize=figsize)
    hp = sns.heatmap(df, annot=annotations, fmt="5.2f", linewidths=.5, ax=ax,cmap='bwr', vmin=vmin, vmax=vmax)
    if pdfExport != None:
        f.savefig(pdfExport)

    
def plotFluxControlHeatMap (r, pdfExport=None, annotations=True, figsize=(13,7), vmin=-1, vmax=1):
    '''
    Display the flux control coefficients as a heat map
    
    Args:
        r : reference
           roadrunner instance
        pdfExport : string
           optional parameter, if present it should indicate the filename to export the heat map image to in the form of pdf
        annotations : boolean
           used to draw values on teh heatmap cells
        figsize : tuple
           sets the size of the plot, eg figsize=(10,5)
        vmin and vmax : double
           set the lower and upper limits for the range

    Example:
       >>> teUtils.plotting.plotFluxControlHeatMap (r, pdfExport='heapmap.pdf')
    '''

    import seaborn as sns
    import pandas as pd
    
    hist = r.getScaledFluxControlCoefficientMatrix()
    ss = r.getReactionIds()
    rr = ["E" + str(x) for x in range (r.getNumReactions())]

    df = pd.DataFrame (hist, columns=rr, index=ss)

    f, ax = _plt.subplots(figsize=figsize)
    hp = sns.heatmap(df, annot=annotations, fmt="5.2f", linewidths=.5, vmin=vmin, vmax=vmax, ax=ax, cmap='bwr')

    if pdfExport != None:
        f.savefig(pdfExport)
        
       
def plotFluxControlBar (r, reactionId, figsize=(13,7)):
    '''
    Plots a graph bar graph of the flux control coefficients
    
    Args:
        r : reference
           roadrunner instance
        reactionid : string
           reactinoId for the flux control 
        figsize : tuple of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotFluxControlBar (r, 'J1', figsize=(12,6))
    '''
    import matplotlib.pyplot as plt
    
    cc = r.getScaledFluxControlCoefficientMatrix()
    rIds = r.getReactionIds()
    index = rIds.index (reactionId)
    row = cc[index,:]
    
    _plt.figure(figsize=figsize)    
    _plt.bar(rIds, row, label=reactionId)
    _plt.xticks(range (len (rIds)), rIds,  ha='right', rotation=45)  
    _plt.legend()

def plotConcentrationControlBar (r, speciesId, figsize=(13,7)):
    '''
    Plots a graph bar graph of the concentration control coefficients
    
    Args:
        r : reference
           roadrunner instance
        speciesid : string
           speciesId for the concentration control 
        figsize : tuple of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotConcentrationControlBar (r, 'Glucose', figsize=(12,6))
    '''
    import matplotlib.pyplot as plt
    

    cc = r.getScaledConcentrationControlCoefficientMatrix()
    spIds = r.getFloatingSpeciesIds()
    rIds = r.getReactionIds()
    index = spIds.index (speciesId)
    row = cc[index,:]
    print (row)
    print (rIds)
    
    _plt.figure(figsize=figsize)    
    _plt.bar(rIds, row, label=speciesId)
    _plt.xticks(range (len (rIds)), rIds,  ha='right', rotation=45)  
    _plt.legend()


def plotArrayHeatMap (data, pdfExport=None, annotations=True, figsize=(13,7), vmin=-1, vmax=1):
    '''
    Display the flux control coefficients as a heat map
    
    Args:
        r : reference
           roadrunner instance
        pdfExport : string
           optional parameter, if present it should indicate the filename to export the heat map image to in the form of pdf
        annotations : boolean
           used to draw values on teh heatmap cells
        figsize : tuple
           sets the size of the plot, eg figsize=(10,5)
        vmin and vmax : double
           set the lower and upper limits for the range

    Example:
       >>> teUtils.plotting.plotFluxControlHeatMap (r, pdfExport='heapmap.pdf')
    '''

    import seaborn as sns
    import pandas as pd
    
    #ss = r.getReactionIds()
    #rr = ["E" + str(x) for x in range (r.getNumReactions())]

    df = pd.DataFrame (data)

    f, ax = _plt.subplots(figsize=figsize)
    hp = sns.heatmap(df, annot=annotations, fmt="5.2f", linewidths=.5, vmin=vmin, vmax=vmax, ax=ax, cmap='bwr')

    if pdfExport != None:
       f.savefig(pdfExport)

    
def plotConcentrationControlIn3D (r, upperLimit=1, lowerLimit=-1, figsize=(10, 8)):
    '''
    Display the concentation control coefficients as a 3D plot
    
    Args:
        r : reference
           roadrunner instance
        upperlimit : float 
           optional parameter, sets the lower z axis limit
        upperlimit : float
           optional parameter, sets the upper z axis limit
        figsize : tuble of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotConcentrationControlIn3D (r)
    '''

    import matplotlib.colors as colors
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    fig = _plt.figure(figsize=figsize)
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
    ax.w_xaxis.set_ticks(_np.arange (float (hist.shape[0])))
    ax.w_xaxis.set_ticklabels(r.getFloatingSpeciesIds())
    ax.w_yaxis.set_ticks(_np.arange (float (hist.shape[1])))
    #ax.w_yaxis.set_ticks(ypos + dy/2.)
    ax.w_yaxis.set_ticklabels(r.getReactionIds())

    ax.bar3d (xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average') 
    
    
def plotFluxControlIn3D (r, upperLimit=1, lowerLimit=-1, figsize=(9, 7)):
    '''
    Display the flux control coefficients as a 3D plot

    Args:
        r : reference
           roadrunner instance
        upperlimit : float 
           optional parameter, sets the lower z axis limit
        upperlimit : float
           optional parameter, sets the upper z axis limit
        figsize : tuble of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotFluxControlIn3D (r)
    '''

    import matplotlib.cm as cm
    import matplotlib.colors as colors
        
    fig = _plt.figure(figsize=figsize)
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
    ax.w_xaxis.set_ticks(_np.arange (float (hist.shape[0])))
    ax.w_xaxis.set_ticklabels(r.getReactionIds())
    ax.w_yaxis.set_ticks(_np.arange (float (hist.shape[1])))
    print (hist.shape)
    ax.w_yaxis.set_ticklabels(r.getReactionIds())

    ax.bar3d (xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average') 
    

    
def plotReactionRates (r, figsize=(12,6)):
    '''
    Plots a graph bar graph of the reaction rates
    
    Args:
        r : reference
           roadrunner instance
        figsize : tuple of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotReactionRates (r, figsize=(12,6))
    '''
    import matplotlib.pyplot as plt
    
    xlabels = r.getReactionIds()
    rates = r.getReactionRates()
    _plt.figure(figsize=figsize)    
    _plt.bar(xlabels, rates, label=xlabels)
    _plt.xticks(range (len (xlabels)), xlabels,  ha='right', rotation=45)  


def plotFloatingSpecies (r, figsize=(12,6)):
    '''
    Plots a graph bar graph of the floating species concentrations.
    
    Args:
        r : reference
           roadrunner instance
        figsize : tuple of float
           optional: width and heigh of plot in inches

    Example:
       >>> teUtils.plotting.plotFloatingSpecies (r, figsize=(12,6))
    '''
    import matplotlib.pyplot as plt
    
    xlabels = r.getFloatingSpeciesIds()
    concs = r.getFloatingSpeciesConcentrations()
    _plt.figure(figsize=figsize)    
    _plt.bar(xlabels, concs, label=xlabels)
    _plt.xticks(range (len (xlabels)), xlabels,  ha='right', rotation=45)    


def plotArray(result, loc='upper right', show=True, resetColorCycle=True,
             xlabel=None, ylabel=None, title=None, xlim=None, ylim=None,
             xscale='linear', yscale="linear", grid=False, labels=None, **kwargs):
    """ Plot a 2D graph based on an array where the first column is the x-axis

    The first column of the array must be the x-axis and remaining columns the y-axis.  
    Note that you can add plotting options as named key values after
    the array. To add a legend, include the label legend values:
    te.plotArray (m, labels=['Label 1, 'Label 2', etc])
    Make sure you include as many labels as there are curves to plot!
    Use show=False to add multiple curves. Use color='red' to use the same color for every curve.

    Args:
        r : reference
           roadrunner instance

    Returns:
       Returns a handle to the plotting object.

    Example:
        >>> import numpy as np
        >>> result = _np.array([[1,2,3], [7.2,6.5,8.8], [9.8, 6.5, 4.3]])
        >>> te.plotArray(result, title="My graph', xlim=((0, 5)))
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

    import teUtils
    
    r.steadyState()
    teUtils.plotting.plotFloatingSpecies (r)
    
    teUtils.plotting.plotConcentrationControlIn3D (r)
    teUtils.plotting.plotFluxControlIn3D (r, lowerLimit=0)
    
    teUtils.plotting.plotConcentrationControlHeatMap (r)
    teUtils.plotting.plotFluxControlHeatMap (r)


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
    
    m = r.simulate(0, 100,200)
    teUtils.plotting.plotArray (m)
    teUtils.plotting.plotWithLegend (r, m)
    
    r.steadyState()
    teUtils.plotting.plotFloatingSpecies (r, figsize=(6,3))
    
    teUtils.plotting.plotConcentrationControlIn3D (r)
    teUtils.plotting.plotFluxControlIn3D (r, lowerLimit=0)
    
    teUtils.plotting.plotConcentrationControlHeatMap (r)
    teUtils.plotting.plotFluxControlHeatMap (r)
    



