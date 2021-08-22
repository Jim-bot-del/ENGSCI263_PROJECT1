# The start of the Modelling stuff I guess
#from main import solve_Pressure_ode
from re import A
import numpy as np
from numpy.core.numeric import NaN
from matplotlib import pyplot as plt
from numpy.lib.function_base import interp
from scipy.interpolate import interp1d
import itertools
from scipy.optimize import curve_fit

net = []
qCO2 = []
pressure = []
a = 0
b = 0
c = 0
d = 0 
M0 = 0

def main():
	CurveFit()
	# we have all of our constants need to use constants to see how model predicts data 
	# up to 2020
	# Then we can extrapolate
	time, Pressure = getPressureData()
	prediction = time
	pars = [1, 1, a,b,c]
	sol, t = solve_pressure_ode(pressure_model, prediction[0], prediction[-1], 0.465, pressure[0], pars)

	f, ax = plt.subplots(1, 1)
	ax.plot(t,sol, 'r', label = 'ODE predict')
	ax.plot(time,pressure, 'b', label = 'ODE')
	ax.plot(time, Pressure, 'k', label = 'DATA')
	plt.axvline(time[90], color = 'black', linestyle = '--', label = 'Calibration point')
	ax.legend()
	ax.set_title("Pressure flow in the Ohaaki geothermal field.")
	plt.show()
	return 

def solve_pressure_ode(f, t0, t1, dt , P0, pars):
	nt = int(np.ceil((t1-t0)/dt))
	ts = t0+np.arange(nt+1)*dt
	ys = 0.*ts
	ys[0] = P0
	for k in range(nt):
		pars[0] = net[k]
		pars[1] = (net[k+1] - net[k])/dt
		ys[k + 1] = improved_euler_step(f, ts[k], ys[k], dt, P0, pars)
	return ys, ts


def improved_euler_step(f, tk, yk, h, x0, pars):
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
	yk1 = yk + h*(f0*0.5 + f1*0.5)
	return yk1

def pressure_model(t, P, q, dqdt, a, b, c, P0):
	dPdt = -a*q - b*(P-P0) - c*dqdt
	return dPdt

def CurveFit():
	time, Pressure  = getPressureData()
	# initial guesses come from MSPE A function which brute forces the terms
	pars = [0.0012653061224489797,0.09836734693877551,0.0032244897959183673]

	autofit_pars1 = curve_fit(solve_Pressure_ode, time, Pressure)
	sol_pressure = solve_Pressure_ode(time, *autofit_pars1[0])

	global pressure
	pressure = sol_pressure

	f, ax = plt.subplots(1, 1)
	ax.plot(time,sol_pressure, 'b', label = 'ODE')
	ax.plot(time,Pressure, 'r', label = 'DATA')
	plt.axvline(time[90], color = 'black', linestyle = '--', label = 'Calibration point')
	ax.legend()
	ax.set_title("Pressure flow in the Ohaaki geothermal field.")
	plt.show()

	time, Pressure, conc = getConcentrationData()
	# in order for pars
	global C
	C = conc
	global a
	a = autofit_pars1[0][0]
	global b
	b = autofit_pars1[0][1]
	global c
	c = autofit_pars1[0][2]


	pars = [0.0001,10000000] # initial guesses

	autofit_pars = curve_fit(solve_Solute_ode, time, conc, pars)
	sol_conc = solve_Solute_ode(time, *autofit_pars[0])
	global d 
	d = autofit_pars[0][0]
	global M0
	M0 = autofit_pars[0][1]

	f, ax = plt.subplots(1, 1)	
	ax.plot(time,sol_conc, 'b', label = 'ODE')
	ax.plot(time,conc, 'r', label = 'DATA')
	plt.axvline(time[90], color = 'black', linestyle = '--', label = 'Calibration point')
	ax.legend()
	ax.set_title("Concentration of CO2 in the Ohaaki geothermal field.")
	plt.show()	
	return

def getConcentrationData():
	'''
	Reads all relevant data from output.csv file
	Parameters : 
	------------
	None
	Returns : 
	---------
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
	# extracts the relevant data
	t = vals[:,1] # time values
	P = vals[:,3] # Pressure values
	global qCO2 
	qCO2 = vals[:,4] # CO2 injection values 
	CO2_conc = vals[:,5] # CO2 concentration values
	CO2_conc[np.isnan(CO2_conc)] = 0.03 # inputting natural state 
	qCO2[np.isnan(qCO2)] = 0 # absence of injection values is 0
	P[0] = P[1]

	return t, P, CO2_conc

def MSPE_A():
	'''
	Using MSPE as metric for brute-force calculating coefficients of the pressure ODE.
	Parameters : 
	------------
	None
	Returns : 
	---------
	A : float
		Best parameter one for ODE model
	B : float
		Best parameter two for ODE model
	C : float
		Best parameter three for ODE model
	Generates plots of various ODE models, best ODE model, and MSPE wrt. A    
	
	'''

	# Experimental Data, defining testing range for coefficient, constants
	time, Pressure ,netFlow = getPressureData()
	A = np.linspace(0.001,0.0015,50)
	# A = 9.81/(0.15*A)
	B = np.linspace(0.08,0.11,50)
	C = np.linspace(0.002,0.006,50)
	dt = 0.5
	MSPE_best = float('inf')
	best_A = 1000
	best_B = 1000
	best_C = 1000


	# Modelling ODE for each combination of A,B,C
	for A_i,B_i,C_i in itertools.product(A,B,C):
		pars = [netFlow,A_i,B_i,C_i,1]
		sol_time, sol_pressure = solve_Pressure_ode(pressure_model, time[0], time[-1], dt , Pressure[0], pars)

		# Interpolating for comparison of MSE
		f = interp1d(sol_time,sol_pressure)
		analytic_pressure = f(time)
		diff_array = np.subtract(analytic_pressure,Pressure)
		squared_array = np.square(diff_array)
		MSPE = squared_array.mean()

		print(A_i)

		if (MSPE < MSPE_best):
			MSPE_best = MSPE
			best_A = A_i
			best_B = B_i
			best_C = C_i


	
	# Plotting best fit ODE
	pars = [netFlow,best_A,best_B,best_C,1]
	sol_time, sol_pressure = solve_Pressure_ode(pressure_model, time[0], time[-1], dt , Pressure[0], pars)

	# Printout of results
	txt = "Best coefficient {} is {}"
	print(txt.format("A",best_A))
	print(txt.format("B",best_B))
	print(txt.format("C",best_C))
	print("Mean Squared Error is {}".format(MSPE_best))

	
	f, ax2 = plt.subplots(1, 1)
	ax2.plot(sol_time,sol_pressure, 'b', label = 'ODE')
	ax2.plot(time,Pressure, 'r', label = 'DATA')
	ax2.set_title("Best fit A coefficient")
	ax2.legend()
	plt.show()
		

	return best_A,best_B,best_C

def curve_pressure_model(t, P, q, a, b, c, dqdt):
	''' Return the Pressure derivative dP/dt at time, t, for given parameters.
		Parameters:
		-----------
		t : float
			Independent variable.
		P : float
			Dependent variable.
		q : float
			Source/sink rate.
		a : float
			Source/sink strength parameter.
		b : float
			Recharge strength parameter.
		c  : float
			Recharge strength parameter
		dqdt : float
			Rate of change of flow rate
		P0 : float
			Ambient value of dependent variable.
		Returns:
		--------
		dPdt : float
			Derivative of Pressure variable with respect to independent variable.
	'''
	P0 = 6.17
	dPdt =  -a*q - b*(P-P0) - c*dqdt
	return dPdt

def SoluteModel(t, C, qC02, P, d, M0):
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
	# performing calculating C' for ODE
	P0 = 6.17
	C0 = 0.03
	if (P > P0):
		Cdash1 = C
	else:
		Cdash1 = C0
		Cdash2 = 0

	qloss = (b/a)*(P-P0)*Cdash2*t # calculating CO2 loss to groundwater

	qC02 = qC02 - qloss # qCO2 after the loss

	dCdt = (1 - C)*(qC02/M0) - (b/(a*M0))*(P-P0)*(Cdash1-C) - d*(C-C0) # calculates the derivative
	return dCdt

def solve_Solute_ode(t, d, M0):
	''' Solve an ODE numerically.
		Parameters:
		-----------
		f : callable
			Function that returns dxdt given variable and parameter inputs.
		t0 : float
			Initial time of solution.
		t1 : float
			Final time of solution.
		dt : float
			Time step length.
		x0 : float
			Initial value of solution.
		pars : array-like
			List of parameters passed to ODE function f.
		Returns:
		--------
		t : array-like
			Independent variable solution vector.
		ys : array-like
			Dependent variable solution vector.
		Notes:
		------
		ODE is solved using improved Euler
	'''
	x0 = 0.03
	dt = 0.5
	nt = len(t) # gets size of the array needing to solve
	ys = 0.*t # creates array to put solutions in
	ys[0] = x0 # inputs initial values
	pars = [d,M0]
	for k in range(nt-1):
		# improved euler needs different values of pressure and sink rate
		# for different time values
		q = qCO2[k]
		P = pressure[k]
		ys[k + 1] = improved_eulerC_step(SoluteModel, t[k], ys[k], dt, q, P,pars)
	return ys


def solve_Pressure_ode(t, a, b, c):
	''' Solve an ODE numerically.
		Parameters:
		-----------
		f : callable
			Function that returns dxdt given variable and parameter inputs.
		t0 : array-like
			Time values used
		
		x0 : float
			Initial value of solution.
		pars : array-like
			List of parameters passed to ODE function f.
		Returns:
		--------
		t : array-like
			Independent variable solution vector.
		ys : array-like
			Dependent variable solution vector.
		Notes:
		------
		ODE is solved using improved Euler
	'''
	dt = 0.5
	nt = len(t)
	
	x0 = 6.17
	# ts = t0+np.arange(nt+1)*dt      # creates time array
	ys = 0.*t                      # creates array to put solutions in
	ys[0] = x0                    # inputs initial value
	# netFlow =                       # extracts the sink values 
	# pars.insert(0,net[0])
	pars = [a,b,c]
	for k in range(nt-1):
		# pars[0] = netFlow[k]
		# # ODE needs sink at different time points calculates dqdt using forward differentiation
		q = net[k]
		dqdt = (net[k+1] - net[k])/(t[k+1]-t[k])
		ys[k + 1] = improved_eulerP_step(curve_pressure_model, t[k], ys[k], dt,q, dqdt,pars)
	
	return ys

def improved_eulerC_step(f, tk, yk, h, q, P, pars):
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
	# print(pars)
	f0 = f(tk, yk, q, P, *pars) # calculates f0 using function
	f1 = f(tk + h, yk + h*f0, q, P, *pars) # calculates f1 using fuctions
	yk1 = yk + h*(f0*0.5 + f1*0.5) # calculates the new y value
	return yk1


def improved_eulerP_step(f, tk, yk, h, q, dqdt, pars):
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
	# print(pars)
	f0 = f(tk, yk, q ,*pars, dqdt) # calculates f0 using function
	f1 = f(tk + h, yk + h*f0, q, *pars, dqdt) # calculates f1 using fuctions
	yk1 = yk + h*(f0*0.5 + f1*0.5) # calculates the new y value
	return yk1

def getPressureData():
	'''
	Reads all relevant data from output.csv file
	
	Parameters : 
	------------
	None

	Returns : 
	---------
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
	t = vals[:,1]
	prod = vals[:, 2]
	P = vals[:,3]
	injec = vals[:,4]

	# cleans data
	# for CO2 injection if no data is present then a rate of 0 is given for Pressure 
	# it is given the most recent value
	injec[np.isnan(injec)] = 0
	P[0] = P[1] # there is only one missing value
	global net

	for i in range(len(prod)):
		net.append(prod[i] - injec[i]) # getting net amount 

	return t, P

if __name__ == "__main__":
	 main()
	# MSPE_A()