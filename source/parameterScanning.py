
import tellurium as _te
import matplotlib.pyplot as _plt
import numpy as _np

def simpleTimeCourseScan(r, parameter, variable, lowRange, highRange, numberOfScans,
      timeEnd=10, numberOfPoints=100, formatStr='{:10.6f}', legendLoc='upper right'):
    
    """ Run a time course simulation at different parameter values, observe a single variable
    
    Args:   
      r (reference): Roadrunner instance
      parameter (string): The name of the parameter to change
      variable (string): The name of the variable to record during the scan
      lowRange (float): The starting value for the parameter
      highRange (float): The final value for the parameter
      numberOfScans (integer): The number of values of the parameter to try
      timeEnd (float): Optional: Simulate a time course up to this time
      numberOfPoints: (integer): Optional: Generate this number of points for each time course
      formatStr (string): Optional: The format string for values listed in the plot legend
         
    Return:
      numpy array:
         first column being time
         remaining columns correspond to each parameter scan.
    
    Example:
   
     .. code-block:: python

        import tellurium as te
        import teUtils as tu

        r = te.loada('''
        J1: $Xo -> S1; k10*Xo - k11*S1; 
        J2: S1 -> S2;  k20*S1 - k21*S2; 
        J3: S2 -> $X1; k30*S2 - k31*X1; 

        k10 = 1.21;  k11 = 0.69
        k20 = 1.03;  k21 = 0.13
        k30 = 1.89;  k31 = 0.10
        Xo = 6.00
        X1 = 0
        S1 = 0; S2 = 0;
        ''')

        tu.parameterScanning.simpleTimeCourseScan(r, 'k20', 'S1', 
                3, 12, 7, timeEnd=6, numberOfPoints=200, formatStr='{:4.1f}')
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
    _plt.legend(loc=legendLoc)
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
