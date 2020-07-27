
import numpy as np
# Variety of useful file utilties, easier to use than the python supplied functionality

def readCsvFile (fileName, delimiter=','):
	""" Will read data from a csv file that has column labels
	eg
	time,S1,S2
	0.0, 0.4, 0.5
	0.1, 0.2, 0.8
	etc
    
    The method returns to pieces of data, the csv data itself as a
    numpy array and a list of header names. By defauls the the first column
    is not included to make it compatible with plotArray.
    the argument, includeFirstColumnLabel=True if the first column label is needed
    >>> data, header = te.fileUtils.readCsvFile ('mydata.txt')

    The data variable can be plotted using te.plotArray(data, header)
    """

def readCsvFile (fileName, includeFirstColumnLabel=False):
    import csv, numpy as np
    # Open the data file and look for the header line         
    with open(fileName, 'r') as f:
         reader = csv.reader(f, delimiter=',')
         if csv.Sniffer().has_header(f.readline()):
            f.seek(0)
            header = next(reader)
            if not includeFirstColumnLabel:
               del header[0]
         else:
            raise Exception ('Error: This data file has no column headers')
         return np.array(list(reader)).astype(float), header