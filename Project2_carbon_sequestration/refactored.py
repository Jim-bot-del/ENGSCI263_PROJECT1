## data handling
from glob import glob

## numpy and math
import numpy as np
from numpy.core.numeric import NaN
from numpy.lib.function_base import interp

import statistics
import itertools

from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

## plotting
from matplotlib import pyplot as plt

## type handling
from typing import List

class Helper:
	"""Class containing helper functions 

	Methods:
		COMPLETE
			improved_euler_step(...)
				DESCRIPTION HERE

		TODO: INCOMPLETE
			benchmark - compares analytical solution vs data

			grid_search

			construct_samples

			model_ensemble

			!!!assosciated error functions^
		
	
	"""
	@staticmethod
	def improved_euler_step(self, f, tk: float, yk: float, h: float, x0: float, pars)->float:
		""" Compute a single Improved Euler step.
		
			Parameters
			----------
			f : callable
				Derivative function.
			tk : float
				Independent variable at beginning of step.
			yk : float
				Solution at beginning of step.
			h : float
				Step size.
			pars : iterable
				Optional parameters to pass to derivative function.
				
			Returns
			-------
			yk1 : float
				Solution at end of the Improved Euler step.
		"""
		f0 = f(tk, yk, *pars, x0)
		f1 = f(tk + h, yk + h*f0, *pars,x0)
		yk1 = yk + h*0.5*(f0 + f1)

		return yk1

class PressureModel:
	"""Class containing pressure model methods, instantiated using: newVar = PressureModel()

		Data :
			...

		Methods :
			IMPLEMENTED/COMPLETE
			run :
				runs everything ...

			getPresureData : 
				None -> None
				reads in the data from output.csv adding it to the class data

			model : 
				float -> float
				returns the first derivative of pressure with respect to time

			solve :
				...

			optimise :
				...

			plot :
				...
			
			TODO/INCOMPLETE 
			!!! add docstrings

			interpolate :
				interpolates the data for the new timestep

			extrapolate : 
				extrapolates the data


	TODO:

		add other functions

	"""
	def __init__(self, pars = [1,1,1,1]):
		self.time = []
		self.pressure = []
		self.analytical = []
		self.net = []
		self.pars = pars
		self.dt = 0.5

	def getPressureData(self)->None:
		'''
			Reads all relevant data from output.csv file
			
			Parameters : 
			------------
			None

			Returns : 
			---------
			None (instantiates class data)

			t : np.array
				Time data that matches with other relevant quantities 

			P : np.array
				Relevant Pressure data in MPa

			net : np.array
				Overall net flow for the system in kg/s
		'''
		# reads the files' values
		vals = np.genfromtxt('output.csv', delimiter = ',', skip_header= 1, missing_values= 0)

		# extracts the relevant data
		self.time = vals[:,1]
		self.pressure = vals[:,3]
		self.pressure[0] = self.pressure[1] # there is only one missing value
		self.pars[0] = self.pressure[0]
		self.net = []

		prod = vals[:, 2]
		injec = vals[:,4]

		# cleans data
		# for CO2 injection if no data is present then a rate of 0 is given for Pressure 
		# it is given the most recent value
		injec[np.isnan(injec)] = 0
		
		for i in range(len(prod)):
			self.net.append(prod[i] - injec[i]) # getting net amount 

		return 

	def model(self, t: float, P: float, q: float, dqdt: float, a: float, b: float, c: float, P0: float)->float:
		"""Returns the first derivative of pressure with respect to time
		"""
		dPdt = -a*q - b*(P-P0) - c*dqdt
		return dPdt

	def solve(self, t: List[float], a: float, b: float, c: float, y0: float = 6.17)->List[float]:
		""" Solves ode ...
		
		"""
		## checking that the lengths for data match
		nt = len(t)
		if nt != len(self.net):
			raise ValueError("If the original time data is not used then the net sink must be interpolated to fit")

		result = 0.*t	# creating output array 
		result[0] = y0	# setting the initial value

		params = [0, a, b, c, 0]

		for k in range(1, nt):
			# setting the value for q sink and dqdt
			params[0] = self.net[k]
			params[-1] = (self.net[k] - self.net[k-1]) / self.dt
			
			result[k] = Helper.improved_euler_step(self, self.model, t[k], result[k-1], self.dt, y0, params)

		return result

	def optimise(self, ignorePressure: bool = False)->None:
		"""Function which uses curve_fit() to optimise the paramaters for the ode
		"""
		self.pars = curve_fit(self.solve, self.time, self.pressure, self.pars[:4-ignorePressure])[0]
		
		return  

	def interpolate(self):
		pass
	
	def plot(self, c1: str = 'r', c2: str = 'b')->None:
		f, ax = plt.subplots(1,1)

		ax.plot(self.time,self.pressure, c1, label = "Measurements")
		ax.plot(self.time,self.analytical, c2, label = "Analyitical Solution")

		ax.legend()

		ax.set_title("Pressure in the Ohaaki geothermal field.")

		plt.show()
		
		return

	def run(self, optimiseArgs: List[bool] = [False], plotArgs: List[str] = ['r','b'])->None:
		"""This function runs everything and produces a plot of the analytical solution

		TODO: 
			-	include optional paramaters for extrapolation, uncertainty
			- 	include the graph we used to validate our ode
		
		"""
		self.getPressureData()
		self.optimise(*optimiseArgs)
		self.analytical = self.solve(self.time, *self.pars)
		self.plot(*plotArgs)

		return

class SoluteModel:
	"""Class containing solute model methods, instantiated using: newVar = SoluteModel()

		Data : 
			- ...

		Methods :
			- ...

	TODO:
	
		- ...
	"""
	def __init__(self):
		self.time = []
		self.pressure = []
		self.qC02 = []
		self.CO2_conc = []

	def getConcentrationData(self)->None:
		'''	Reads all relevant data from output.csv file

			Parameters : 
			------------
				None

			Returns : 
			---------
				None, modifies class data

				t : np.array
					Time data that matches with other relevant quantities 

				P : np.array
					Relevant Pressure data in MPa

				injec : np.array
					Relevant CO2 injection data in kg/s

				CO2_conc : np.array
					Relevant concentrations of CO2 in wt %

			Notes :
			------
				CO2 concentration before injection is assumed to be natural state
				of 3 wt %. 
		'''

		# reads all the data from excel file
		vals = np.genfromtxt('output.csv', delimiter = ',', skip_header= 1, missing_values= 0)
		
		## extracting the relevant data
		self.time = vals[:,1] 		# time values
		self.pressure = vals[:,3] 	# Pressure values
		self.qCO2 = vals[:,4] 		# CO2 injection values 
		self.CO2_conc = vals[:,5]	# CO2 concentration values
		
		## Cleaning the data
		self.qCO2[np.isnan(qCO2)] = 0 				# absence of injection values is 0
		self.CO2_conc[np.isnan(CO2_conc)] = 0.03 	# inputting natural state 

		self.pressure[0] = self.pressure[1]			# missing initial pressure data point
		
		return 

	def model(self, t: float, C: float, qC02: float, P: float, a: float, b: float, d: float, M0: float, P0: float = 6.17, C0: float = 0.03)->float:
		''' Return the Solute derivative dC/dt at time, t, for given parameters.
			Parameters:
			-----------
			t : float
				Independent variable.
			C : float
				Dependent variable.
			qCO2 : float
				Source/sink rate.
			a : float
				Source/sink strength parameter.
			b : float
				Recharge strength parameter.
			d  : float
				Recharge strength parameter
			P : float
				Pressure at time point t
			P0 : float
				Ambient value of Pressure within the system.
			M0 : float
				Ambient value of Mass of the system
			C0 : float
				Ambient value of the dependent variable.
			Returns:
			--------
			dCdt : float
				Derivative of Pressure variable with respect to independent variable.
		'''
		if (P > P0):
			C_1 = C
			# see what happens
			C_2 = C
		else:
			C_1 = C0
			C_2 = 0

		qLoss = (b/a)*(P-P0)*C_2*t # calculating CO2 loss to groundwater

		qC02 = qC02 - qLoss # qCO2 after the loss

		dCdt = (1 - C) * (qC02 / M0) - (b / (a*M0)) * (P - P0) * (C_1 - C) - d * (C - C0) # calculates the derivative

		return dCdt

	def solve(self, t: List[float])->List[float]:
		pass

	def optimise(self)->None:
		pass

	def interpolate(self):
		pass

	def plot(self)->None:
		pass

	def run(self)->None:
		pass
## ---------------------------------------------------------
## ---------------------------------------------------------
## ---------------------------------------------------------

def main():

	## 	TEST 1
	model1 = PressureModel()

	# model1.getPressureData()
	# solution1 = model1.solve(model1.time, *model1.pars)
	# # print(model1.pars)
	# model1.optimise()
	# # print(model1.pars)
	# solution2 = model1.solve(model1.time, *model1.pars)

	# model1.plot()
	# # print(model1.pressure[:10]) 
	# # print(solution1[:10])
	# # print(solution2[:10])

	model1.run()

	pass

if __name__ == "__main__":
	main()