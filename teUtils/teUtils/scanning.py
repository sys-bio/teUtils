
import tellurium as _te
import matplotlib.pyplot as _plt
import numpy as _np

def simpleTimeCourseScan (r, parameter, variable, lowRange, highRange, numberOfScans, timeEnd=10, numberOfPoints=100, formatStr='{:10.6f}'):
    
    """ Run a time course simulation at different parameter values, observe a single variable
    
    Parameters 
    ----------      
        arg1 (reference): Roadrunner instance
         
        arg2 (string): The name of the parameter to change
  
        arg3 (string): The name of the variable to record during the scan
        
        arg4 (float): The starting value for the parameter
        
        arg5 (float): The final value for the parameter
        
        arg6 (integer): The number of values of the parameter to try
        
        arg6 (float): Optional: Simulate a time course up to this time
        
        arg7 (integer): Optional: Generate this number of points for each time course
        
        arg8 (string): Optional: The format string for values listed in the plot legend
         
    Return
    ------
    Returns a numpy array with the first column being time and the remaining columns 
    correspond to each parameter scan.
    
    Example
    -------     
    >>> data = teUtils.scanning.simpleTimeCourseScan (r, 'k2', 'S1', 3, 12, 7)
    """   
    r[parameter] = lowRange
    stepSize = (highRange - lowRange)/(numberOfScans-1)
    for h in range (numberOfScans):
        r.reset()
        m = r.simulate (0, timeEnd, numberOfPoints, ["Time", variable])
        _te.plotArray (m, resetColorCycle=False, label=parameter + ' = ' + formatStr.format (r[parameter]), show=False)
        r[parameter] = r[parameter] + stepSize

    _plt.ylabel('Concentration (' + variable + ')')
    _plt.xlabel ('Time')
    _plt.legend()
    # A bit of a hack to extract the data out of the plot and construct a
    # numpy array of time in first column and scans in remaining columns
    data = _np.empty([numberOfPoints, 0]) # Create an empty array
    g = _plt.gca()
    # Collect the time column first
    xdata = g.lines[0].get_xdata()
    xdata = xdata.reshape (len (xdata), 1)  # Reshape to make arrays compatible when we use hstack 
    data = _np.hstack ((data, xdata))
    # Now collect the y columns
    for i in range (len (g.lines)):
        ydata = g.lines[i].get_ydata()
        ydata = ydata.reshape (len (ydata), 1)  
        data = _np.hstack (((data, ydata)))
    return data


def testme():
    
    r = _te.loada('''
      $Xo -> S1; vo;
      S1 -> S2; k1*S1 - k2*S2;
      S2 -> $X1; k3*S2;

      vo = 1
      k1 = 2; k2 = 0.6; k3 = 3;
    ''')
   
    return simpleTimeCourseScan (r, 'k2', 'S1', 3, 12, 3)    
