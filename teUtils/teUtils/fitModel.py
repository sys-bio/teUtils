# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 14:24:09 2020

@author: hsauro
"""

import numpy as np
import lmfit; 
import roadrunner
import tellurium as te 

class fitModel:
    
     rmodel = 0
     parametersToFit = []
     timeToSimulate = 4
     nDataPoints = 30
     SIndexList = []
     
     def __init__(self, fileName):      
        self.timeSeriesData = np.loadtxt(fileName, delimiter=",")
    
     def setModel (self, model):
         self.rmodel = model
         
     def setParametersToFit (self, parametersToFit):
         self.parametersToFit = parametersToFit
         
     def setTimeSeriesData (self, columnIndices):
         self.SIndexList = []
         for i in range (len (columnIndices)):
             if columnIndices[i] in self.rmodel.getFloatingSpeciesIds():
                 self.SIndexList.append (i+1) # index start from 1 not zero, hence add 1
             
         self.x_data = self.timeSeriesData[:,0]
         self.y_data = self.timeSeriesData[:,1:len(self.SIndexList)].T

         
     def computeSimulationData(self, p, SIndex):

         self.rmodel.reset()  
         pp = p.valuesdict()
         for i in range(0, self.nParameters):
            self.rmodel.model[self.parametersToFit[i]] = pp[self.parametersToFit[i]]
         m = self.rmodel.simulate (0, self.timeToSimulate, self.nDataPoints)
         return m[:,SIndex]

     # Compute the residuals between objective and experimental data
     def residuals(self, p):
         #self.SIndexList = [1,2,3,4,5,6]
         #global y_data, SIndexList
         y1 = (self.y_data[0] - self.computeSimulationData (p, self.SIndexList[0])); 
         y1 = np.concatenate ((y1, ))
         for k in range (0, len (self.SIndexList)-1):
             y1 = np.concatenate ((y1, (self.y_data[k] - self.computeSimulationData (p, self.SIndexList[k]))))
         return y1
     
     def fit(self):
         print ('Starting fit...')
         
         self.params = lmfit.Parameters()
         self.nParameters = len (self.parametersToFit)
         for k in self.parametersToFit:
            self.params.add(k, value=1, min=0, max=10)
            
         # Fit the model to the data
         # Use two algorotums:
         # global differential evolution to get us close to minimum
         # A local Levenberg-Marquardt to getsus to the minimum
         minimizer = lmfit.Minimizer(self.residuals, self.params)
         self.result = minimizer.minimize(method='differential_evolution')
         self.result = minimizer.minimize(method='leastsqr')

     def getFittedParameters (self):
         fittedParameters = []
         for i in range(0, self.nParameters):
             fittedParameters.append (self.result.params[self.parametersToFit[i]].value)
         return fittedParameters
     
        
      
def testme():
    
    import tellurium as te
    import numpy as np
    
    r = te.loada("""
    # Reactions   
        J1: S1 -> S2; k1*S1
        J2: S2 -> S3; k2*S2
        J3: S3 -> S4; k3*S3
        J4: S4 -> S5; k4*S4
        J5: S5 -> S6; k5*S5;
    # Species initializations     
        S1 = 10;
    # Parameters:      
       k1 = 1; k2 = 2; k3 = 3; k4 = 4; k5 = 5
    """)

    f = fitModel('testdata.txt')

    f.setModel (r)
    f.setParametersToFit (['k1', 'k2', 'k3', 'k4', 'k5'])
    f.setTimeSeriesData (['S1', 'S2', 'S3', 'S4'])

    f.fit()
    print ("Fitted Parameters are:")
    print (f.getFittedParameters())
  
        
