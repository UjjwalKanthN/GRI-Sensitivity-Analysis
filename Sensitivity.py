'''
Constant Pressure, Adiabatic kinetics simulation with sensitivity analysis

CH4 + 2(O2 + 3.76N2) = CO2 + 2H20 + 7.52N2

Temperature: 1500 K
Pressure: 101325 Pa (1 Bar)
    
@author: Ujjwal
'''

import numpy as np
import matplotlib.pyplot as plt 
import cantera as ct

gas = ct.Solution('gri30.yaml')
temp = 1500
press = 101325

n_reactions = 325 # Number of Reactions

time = np.arange(0, 2e-3, 5e-6) # Simulation Time
interval = 5e-6
n_time = len(time)

gas.TPX = temp, press, {'CH4':1, 'O2':2, 'N2':7.52}
r = ct.IdealGasConstPressureReactor(gas, name='R1')
sim = ct.ReactorNet([r])

# Enable sensitivity with respect to te rates of all the 325 reactions
# reactions (0 through 324)

for i in range(n_reactions):
	r.add_sensitivity_reaction(i)
	

# set the tolerances for the solution and the sensitivity co-efficients
sim.rtol = 1.0e-6 # Realtive change in the solution < sim.rtol
sim.atol = 1.0e-15 # Absolute change in the solution < sim.atol

sim.rtol_sensitivity = 1.0e-6 #relative change in sensitivity < sim.rtol_sense
sim.atol_sensitivity = 1.0e-6 #absolute change in sensitivity <sim.atol_sense

s = np.zeros((n_time, n_reactions))
t = 0

for n in range(n_time): # Iterates for every time step

	t = t + interval
	sim.advance(t) # Increments the reactor by the actual time (not time step)

	for j in range(n_reactions):
	
		s[n,j] = (sim.sensitivity(1, j)) # Sensitivity of Temperature to 100 reactions

		print('%10.3e %10.3f %10.3f %14.6e %s' %
			(sim.time, r.T, r.thermo.P, r.thermo.u, s[n,j]))


def max_abs(array):

	b_ar = np.abs(array) # Finds the Absolute values
	b_arr_f = np.max(b_ar) # Finds the maximum value

	return b_arr_f


b_array = []
fin_sens = [] # Final Sensitivities Array

for i in range(0,n_reactions):
	
	# Stores reaction names and the absolute maximum sensitivities for the respective reaction
	
	b_array = s[:,i]
	
	fin_sens.append((sim.sensitivity_parameter_name(i), max_abs(b_array)))

dtype = [('reaction name', 'S40'), ('max sensitivity', float)]

fin_sens_temp = np.array(fin_sens, dtype=dtype)

final_sort = np.sort(fin_sens_temp, order='max sensitivity')[::-1] # Sorts the reactions in descending order
print(final_sort)


num = 10 # Number of top reactions
top_reac = [] # Stores the top Reactions

for n in range(0,num):
	top_reac.append(final_sort[n])
	print(final_sort[n])


# Plotting the Sensitivities with the respective reactions

def sens_plot(top_reac, temp, press):
	flat_arr = [y for x in top_reac for y in x] # Flattens the 2D array to 1D 

	reac_name = []
	for i in range(0,len(flat_arr),2):
		reac_name.append(flat_arr[i])


	reac_sens = []
	for i in range(1,len(flat_arr)+1,2):
		reac_sens.append(flat_arr[i])


	y_pos = np.arange(len(reac_name))
	y_pos = y_pos[::-1]

	plt.barh(y_pos, reac_sens)
	plt.yticks(y_pos, reac_name)
	plt.xlabel('Modulus of Sensitivity Co-efficient')
	plt.title('GRI Mech Sensitivity Analysis on Temperature')
	plt.text(8, .70, r' $T = %d  [K]$' %(temp), {'color': 'b', 'fontsize': 20})
	plt.text(8, .10, r' $P = %d  [Pa]$' %(press), {'color': 'b', 'fontsize': 20})
	plt.subplots_adjust(left=0.19, bottom=0.20, right=0.90, top=0.88, wspace=0.20, hspace=0.20)
	plt.show()

sens_plot(top_reac, temp, press)
