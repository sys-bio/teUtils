
import tellurium as _te
import matplotlib.pyplot as _plt
import numpy as _np

def simpleTimeCourseScan (r, parameter, variable, low_range, high_range,
      number_of_scans, time_end=10, number_of_points=100, format_str='{:10.6f}'):
    
    """ Run a time course simulation at different parameter values, observe a single variable
    
    Parameters 
    ----------      
    r (reference): Roadrunner instance
    parameter (string): The name of the parameter to change
    variable (string): The name of the variable to record during the scan
    low_range (float): The starting value for the parameter
    high_range (float): The final value for the parameter
    number_of_scans (integer): The number of values of the parameter to try
    time_end (float): Optional: Simulate a time course up to this time
    number_of_points: (integer): Optional: Generate this number of points for each time course
    format_str (string): Optional: The format string for values listed in the plot legend
         
    Return
    ------
    numpy array:
        first column being time
        remaining columns correspond to each parameter scan.
    
    Example
    -------     
    data = teUtils.scanning.simpleTimeCourseScan (r, 'k2', 'S1', 3, 12, 7)
    """   
    r[parameter] = low_range
    step_size = (high_range - low_range)/(number_of_scans-1)
    for h in range (number_of_scans):
        r.reset()
        m = r.simulate (0, time_end, number_of_points, ["Time", variable])
        _te.plotArray (m, resetColorCycle=False,
              label=parameter + ' = ' + format_str.format (r[parameter]), show=False)
        r[parameter] = r[parameter] + step_size

    _plt.ylabel('Concentration (' + variable + ')')
    _plt.xlabel ('Time')
    _plt.legend()
    # A bit of a hack to extract the data out of the plot and construct a
    # numpy array of time in first column and scans in remaining columns
    data = _np.empty([number_of_points, 0]) # Create an empty array
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
