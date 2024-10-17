import numpy as np
import matplotlib.pyplot as plt
from dipep_potential import V_potential, V_deriv
from plots import hills_time, fes, rads_time, animate_md, energy_time
from src import config
import time
import logging
import argparse

# When run as a module, this script has the name 'walker'

# Parse arguments and python logger options
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='set log level')
parser.add_argument('--log', default='INFO', help='log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
args = parser.parse_args()

# Helper function for logger
def setup_logger(level):
    logging.basicConfig(level=level,
    format='%(levelname)s:%(message)s',
    filename='MD_sim.log')

log_level = getattr(logging, args.log.upper(), None)
setup_logger(log_level)

#####---User Inputs---#####

# Define parameters
mratio = 10 #what to do here? Maybe this is something I enforce a min/max for as a function of steps?
steps = config.steps
x0 = config.x0
T = config.temp  # Initial temperature
dt = config.timestep  # Time step
t = 0  # Time
m = 1  # Mass

# Parameters for metadynamics
w = config.w
delta = config.delta
hfreq = config.hfreq

# Parameters for integrator
gamma = 5.0 #
beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol
c1 = np.exp(-gamma * dt / 2)
c2 = np.sqrt((1 - c1**2) * m / beta)

# Subfunction to calculate PE and force
def force(r, s, w, delta):
    r = pbc(r)
    V = V_potential(r)
    F = V_deriv(r) #function notation is at odds with the potential one-liner 
    Fpot = -F

    if config.metad: 
        Fbias = np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2))) # Metadynamics eq
    else:
        Fbias = 0
    return V, Fpot + Fbias

# Lean PBC function for improving performance
def pbc(r, bc=np.pi):
    return (((r + bc) % (2 * bc)) - bc) #one liner


def integrator_performance(t_start, t_end):
    delta_t = t_end - t_start
    ns_day = (steps / delta_t) * dt * 86400 # nanoseconds per day
    time_step = delta_t / steps
    print(f"""SIMULATION SUMMARY:
    nanoseconds per day: {ns_day:.3f}
    time per step: {time_step:.7f}
    """)

# Empty arrays to store information
q = np.zeros(steps + 1) # Making room for final radian
E = np.zeros(steps + 1) # Making room for final energy
V = np.zeros(steps + 1) # Making room for final potential
# COLVAR = [] # empty array to resemble COLVAR file (time, CV, CV.bias)

# Initial configurations 
q[0] = x0
v0 = np.random.rand() - 0.5 #random initial potential
p = v0 * m
s = [0]
v, f = force(q[0], 0, w, delta)
E[0] = 0.5 * p**2 + v



# Plot 1D FES
xlong = np.arange(-np.pi, np.pi, 0.01) #len of bias array is directly related to this. 
vcalc, first = force(xlong, 0, w, delta)
bias = np.zeros((len(xlong), ), dtype=float) # this array size needs to be changed to fit periodic gaussians?

print(f" Number of steps: {steps}")
print(f" Initial x coord: {x0:.2f} radians")
print(f" Initial Potential: {V_potential(x0)}")
print(f" Temperature: {T:.2f}")
print(f" Timestep: {dt:.2e}ns")

# Primary MD Engine
t0 = time.time()

for i in range(steps):
    # Check if we should deposit a hill on the FES
    if config.metad:
        s = np.append(s, q[i]) if i % hfreq == 0 else s # append a sigma as fxn of hfreq

#####---Langevian integrator (https://doi.org/10.1103/PhysRevE.75.056707)---#####
    v, f = force(q[i], s, w, delta) # q[0] is already cast as x0
    R1 = np.random.rand() - 0.5
    R2 = np.random.rand() - 0.5

    pplus = c1 * p + c2 * R1 # eq 12a from Bussi and Parrinello

#####---WRAPPING NEW POSITION IN PBC FUNCTION IS CRUCIAL---#####
    q[i + 1] += pbc(q[i] + (pplus / m) * dt + f / m * (dt**2 / 2)) # eq 12b w/ PBC effect
    v2, f2 = force(q[i + 1], s, w, delta) # obtain updated potentials and forces from updated position 
    pminus = pplus + (f / 2 + f2 / 2) * dt # prev momentum
    p = c1 * pminus + c2 * R2 # eq12a, but calculating current step's momentum 

    E[i + 1] = 0.5 * p**2 + v2 # Updated energy, classic Newtonian eq

    if config.metad:
        if i % hfreq == 0: 
            logger.info(f"""
        *******--- METADYNAMICS STEP ---*******
        step: {i}
        energy: {V[i]}
        radians: {q[i]}""")
        #else: # from 111,118.324 ns/day --> 849,417.845 ns/day. HUH?????
            if len(s) > 1: 
                for k in range(len(xlong)):
                
                ####---HANDLING PBC OF GAUSSIAN ---#####
                    # V(s) is where I want to intervene, NOT V(s, t). 
                    # But the dimensions of the bias added to the gaussian need to be checked for periodicity
                    
                    bias_k = w * np.exp(-(xlong[k] - np.array(s)) ** 2 / (2 * delta**2)) #Bias(rads)
                    rad_k = xlong[k] # where on the x-axis we are biasing

                    #dimensions of gaussian
                    mean_s = np.mean(bias_k)
                    sigma_s = np.std(bias_k)
                    # print(mean_s + 5*sigma_s)

                    if rad_k + (mean_s + 5 * sigma_s) > np.pi: # the 2d gaussian stretches arcross π
                        # print('***PBC ENCOUNTERED***')
                        bias[k - len(xlong)] += np.sum(bias_k)
                    
                    if rad_k - (mean_s - 5 * sigma_s) < -np.pi: # the 2d gaussian stretches arcross -π
                        # print('***PBC ENCOUNTERED***')
                        bias[k + len(xlong)] += np.sum(bias_k)
                    
                    else:
                        # print('***NORMAL METAD***')
                        bias[k] += np.sum(bias_k) #summation step

                    # PRIOR TO THINKING ABOUT PBC
                    # bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))

        
        # append the biased potential to existing potential 
        v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # main metad step

        V[i] = v #THIS IS CRUCIAL!!
    
    else:
        V[i] = v # Store unbiased potential 
        bias = 0
    
    if i % mratio == 0: 
        logger.info(f"""
            step: {i}
            energy: {V[i]}
            radians: {q[i]}""")
        
        # plot all deposited hills at once, but not at once?
        # plt.plot(xlong, bias, linewidth=4, color='red', label='Bias')
        # plt.plot(xlong, vcalc, linewidth=2, label='FES')
        # plt.plot([q[i + 1]], [v], 'ro', markersize=10, markerfacecolor='r')
        # plt.xlabel('CV (s)', fontsize=16)
        # plt.ylabel('F(s) (arb)', fontsize=16)
        # plt.show()

tplus = time.time()

integrator_performance(t0, tplus)

print(np.shape(bias))

#####---Plots as functions from plots.py---#####

# Because we decided to increase the size of arrays and not handle errors..

#sim_time = np.arange(0, steps + 1) * dt * 10e-9 # ns
# OR we can do thisfor legibility
sim_time = np.linspace(0, steps+1, steps+1) * dt #ns


def reweight(bias):
    x = np.linspace(-np.pi, np.pi, len(bias))

    #F(s, t) ~= -V(s, t) + C
    C = (bias - np.min(bias)) #normalization constant of integration?
    # print(C)
    plt.plot(x, -bias - C, label='Correct for C')
    plt.plot(x, -bias, label='no C')

reweight(bias)
# fes(V_potential)
# rads_time(q, sim_time)
# energy_time(E, sim_time)
animate_md(V, bias, q)

plt.show()

