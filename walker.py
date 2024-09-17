import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from dipep_potential import V_x
from plots import hills_time, fes   
from src import config
import time
from numba import jit



# Ideas:
#   - put all the different types of plots im using for diagnostics into functions?
#       - Would make plotting and calling accessory scripts later really easy.
#       - I already need to do that for something to interact with the integrator (mainscript)
#   - I need to think about the scale of which tunable parameters can be explored. 
#  

# Define parameters
steps = 10000
iratio = 10
mratio = 100
x0 = 2.0
T = 310  # Initial temperature | ADJUSTs
dt = 0.005  # Time step
t = 0  # Time
m = 1  # Mass


# Subfunction to calculate PE and force
@jit #complains about calling pbc() function, but INSANE performance speedup!
def force(r, s, w, delta):
    r = pbc(r)
    V = V_x(r)
    F = V_x.deriv() #function notation is at odds with the potential one-liner 
    Fpot = -F(r)

    if config.metad: #ON/OFF SWITCH
        Fbias = np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2))) # Metadynamics

    else:
        Fbias = 0

    # Handle boundary conditions element-wise 
    # V = np.where(r < -np.pi, 100 * (r + np.pi)**4, V) # V = 100(r + pi)^4 | I don't recognize this equation?
    # F = np.where(r < -np.pi, -100 * 4 * (r + np.pi), Fpot + Fbias)
    
    # V = np.where(r > np.pi, 100 * (r - np.pi)**4, V)
    # F = np.where(r > np.pi, -100 * 4 * (r - np.pi), Fpot + Fbias)

    return V, Fpot + Fbias

# Lean PBC function for improving performance, but is it correct??
def pbc(r, bc=np.pi):
    return (((r + bc) % (2 * bc)) - bc)


def integrator_performance(t_start, t_end):
    delta_t = t_end - t_start
    ns_day = (steps / delta_t) * dt * 86400 # nanoseconds per day
    time_step = delta_t / steps
    print('SIMULATION SUMMARY:')
    print(f'nanoseconds per day: {ns_day:.3f}')
    print(f'time per step: {time_step:.7f}')


print("Parameters:")
print(f" Number of steps: {steps}")
print(f" Initial x coord: {x0:.2f}")
print(f" Initial Potential: {V_x(x0)}")
print(f" 'Temperature': {T:.2f}")
print(f" Timestep: {dt:.2e}")

# Parameters for integrator
gamma = 5.0
beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol
c1 = np.exp(-gamma * dt / 2)
c2 = np.sqrt((1 - c1**2) * m / beta)

print(f"\n  c1: {c1:.5f}")
print(f"  c2: {c2:.5f}")

# Metadynamics parameters
w = 1.2 #ADJUST
delta = 0.1 #ADJUST
hfreq = 10 #ADJUST | hill deposition rate

# Empty arrays to store things I need. 
q = np.zeros(steps + 1) # Making room for final radian
E = np.zeros(steps + 1) # Making room for final energy
V = np.zeros(steps + 1) # Making room for final potential
hills = np.zeros(steps + 1)

# Initial configuration
q[0] = x0
v0 = np.random.rand() - 0.5 #random initial potential
p = v0 * m
s = [0]
v, f = force(q[0], 0, w, delta)
E[0] = 0.5 * p**2 + v


# Plot 1D FES
xlong = np.arange(-np.pi, np.pi, 0.01)
vcalc, first = force(xlong, 0, w, delta)

# Primary MD Engine
frame = 0
t0 = time.time()

# Given this is the most time-consuming part of the code, putting it in function like mdrun() might be helpful?
# It's 
for i in range(steps):

    # Check if we should deposit a hill on the FES
    if config.metad:
        s = np.append(s, q[i]) if i % hfreq == 0 else s #potentially MUCH faster one-liner?
        # if i % hfreq == 0: #if no remainder
        #     s.append(q[i]) #append to sigma array

#####---Langevian integrator (https://doi.org/10.1103/PhysRevE.75.056707)---#####
    v, f = force(q[i], s, w, delta) # q[0] is already cast as x0
    R1 = np.random.rand() - 0.5
    R2 = np.random.rand() - 0.5

    pplus = c1 * p + c2 * R1 # eq 12a from Bussi and Parrinello
    q[i + 1] += q[i] + (pplus / m) * dt + f / m * (dt**2 / 2) # eq 12b
    v2, f2 = force(q[i + 1], s, w, delta) # obtain updated potentials and forces from updated position 
    pminus = pplus + (f / 2 + f2 / 2) * dt # prev momentum?
    p = c1 * pminus + c2 * R2 # eq12a, but calculating current step's momentum 

    E[i + 1] = 0.5 * p**2 + v2 # Updated energy, classic Newtonian eq

    if config.metad:
        if i % iratio == 0: 
            bias = vcalc.copy()
            if len(s) > 1: 
                for k in range(len(xlong)):
                    bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))
                    hills[k] = bias[k]
    # consider making this a logger
            print(f"""
        *******--- METADYNAMICS STEP ---*******
        step: {i}
        bias: {bias[k]}
        energy: {V[i]}
        radians: {q[i]}""")
        v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # metad
        V[i] = v #THIS IS CRUCIAL

    else:
        V[i] = v # Store unbiased potential 
        hills[i] = 0 # Add a zero to deposited hills 
    print(f"""
        step: {i}
        energy: {V[i]}
        radians: {q[i]}""")

tplus = time.time()

integrator_performance(t0, tplus)

# Because we decided to increase the size of arrays and not handle errors..
sim_time = np.arange(0, steps + 1) * dt * 10e-9 # ns

hills_time(hills, sim_time)
fes(V_x)

plt.show()


