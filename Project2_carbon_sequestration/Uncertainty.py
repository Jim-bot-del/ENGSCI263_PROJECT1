
import numpy as np
from typing import List

def grid_search(pars: List[float], N: int):
	''' This function implements a grid search to compute the posterior over a and b.

		Parameters:
		pars : The best fitting coefficient for each variable

		N    : The number of parameter spaces for each variable
			   Total number of runs = N^len(pars)

		Returns:
		--------
		a : array-like
			Vector of 'a' parameter values.
		b : array-like
			Vector of 'b' parameter values.
		P : array-like
			Posterior probability distribution.
	'''
	# **to do**
	# 1. DEFINE parameter ranges for the grid search
	# 2. COMPUTE the sum-of-squares objective function for each parameter combination
	# 3. COMPUTE the posterior probability distribution
	# 4. ANSWER the questions in the lab document

	# 1. define parameter ranges for the grid search
	# a_best = 0.0047
	# b_best = 0.26

	# number of values considered for each parameter within a given interval
	# N = 51	
	
	grid = [np.linspace(estimate/2,estimate*1.5, N) for estimate in pars]

	# vectors of parameter values
	# a = np.linspace(a_best/2,a_best*1.5, N)
	# b = np.linspace(b_best/2,b_best*1.5, N)

	# grid of parameter values: returns every possible combination of parameters in a and b
	axis = np.meshgrid(*grid, indexing='ij')

	
	# empty ND matrix for objective function 
	S = np.zeros(axis[0].shape)

	
	
	# TODO: data for calibration?
	# tp,po = np.genfromtxt('wk_pressure_history.csv', delimiter = ',')[:28,:].T

	# error variance - 2 bar
	v = 2.

	# grid search algorithm

	# TODO: this needs be changed to recursive for n dimensions
	# def inner_func(idx: int):
	# 	pass

	for i in range(len(a)):
		for j in range(len(b)):
			# 3. compute the sum of squares objective function at each value 
			#pm =
			#S[i,j] =
			# TODO: add solve LPM
			pm = solve_lpm(tp,a[i],b[j])
			S[i,j] = np.sum((po-pm)**2)/v
	
	# 4. compute the posterior
	P = np.exp(-S/2.)

	# normalize to a probability density function
	# TODO: change this for generalised
	Pint = np.sum(P)*(a[1]-a[0])*(b[1]-b[0])
	P = P/Pint

	# plot posterior parameter distribution
	# plot_posterior(a, b, P=P)

	return axis,P
	

def construct_samples():
	pass

def model_ensemble():
	pass

if __name__ == "__main__":
	# grid_search([1,1,1,1],4)
	pass