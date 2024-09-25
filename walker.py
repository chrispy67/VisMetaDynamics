import numpy as np
import matplotlib.pyplot as plt
from dipep_potential import V_x
from plots import hills_time, fes, rads_time, animate_md, energy_time
from src import config
import time
import logging
import argparse

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
steps = 10000
mratio = 100
x0 = 1
T = 350  # Initial temperature | ADJUST
dt = 0.005  # Time step
t = 0  # Time
m = 1  # Mass

# Parameters for metadynamics
w = 1.2 #ADJUST
delta = 0.1 #ADJUST
hfreq = 10 #ADJUST | hill deposition rate

# Parameters for integrator
gamma = 5.0
beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol
c1 = np.exp(-gamma * dt / 2)
c2 = np.sqrt((1 - c1**2) * m / beta)

# Subfunction to calculate PE and force
def force(r, s, w, delta):
    r = pbc(r)
    V = V_x(r)
    F = V_x.deriv() #function notation is at odds with the potential one-liner 
    Fpot = -F(r)

    if config.metad: #ON/OFF SWITCH
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
    print('SIMULATION SUMMARY:')
    print(f'nanoseconds per day: {ns_day:.3f}')
    print(f'time per step: {time_step:.7f}')

# Empty arrays to store information
q = np.zeros(steps + 1) # Making room for final radian
E = np.zeros(steps + 1) # Making room for final energy
V = np.zeros(steps + 1) # Making room for final potential
COLVAR = [] # empty array to resemble COLVAR file (time, CV, CV.bias)
hills = np.zeros(steps + 1)

# Initial configurations 
q[0] = x0
v0 = np.random.rand() - 0.5 #random initial potential
p = v0 * m
s = [0]
v, f = force(q[0], 0, w, delta)
E[0] = 0.5 * p**2 + v


# Plot 1D FES
xlong = np.arange(-np.pi, np.pi, 0.01)
vcalc, first = force(xlong, 0, w, delta)

print("Parameters:")
print(f" Number of steps: {steps}")
print(f" Initial x coord: {x0:.2f}")
print(f" Initial Potential: {V_x(x0)}")
print(f" 'Temperature': {T:.2f}")
print(f" Timestep: {dt:.2e}")

# Primary MD Engine
t0 = time.time()

for i in range(steps):
    # Check if we should deposit a hill on the FES
    if config.metad:
        s = np.append(s, q[i]) if i % hfreq == 0 else s #potentially MUCH faster one-liner?

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
        if i % hfreq == 0: # ifreq vs hfreq? this USED to be ifreq
            bias = vcalc.copy()
            logger.info(f"""
        *******--- METADYNAMICS STEP ---*******
        step: {i}
        bias: {bias[k]}
        energy: {V[i]}
        radians: {q[i]}""")
        else:
            if len(s) > 1: 
                for k in range(len(xlong)):
                    bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))
                    hills[k] = bias[k]
        v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # metad
        V[i] = v #THIS IS CRUCIAL
    
    else:
        V[i] = v # Store unbiased potential 
        bias = 0
        hills[i] = bias # Add a zero to deposited hills
    
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

def reweight_bias(hills, kT, bins=100):
    pass


#####---Plots as functions from plots.py---#####

# Because we decided to increase the size of arrays and not handle errors..

#sim_time = np.arange(0, steps + 1) * dt * 10e-9 # ns
# OR we can do thisfor legibility
sim_time = np.linspace(0, steps+1, steps+1) * dt #ns

rads_time(q, sim_time)
hills_time(hills, sim_time)
energy_time(E, sim_time)
animate_md(V, hills, q)

plt.show()

