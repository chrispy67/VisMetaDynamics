import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from dipep_potential import V_x
from plots import hills_time

import time

# Ideas:
#   - put all the different types of plots im using for diagnostics into functions?
#       - Would make plotting and calling accessory scripts later really easy.
#       - I already need to do that for something to interact with the integrator (mainscript)
#   - I need to think about the scale of which tunable parameters can be explored. 
#       - just playing with dummy numbers, some simulations are VERY slow.



# Define parameters
steps = 10000
iratio = 10
mratio = 100
movieflag = 10  # Set to 1 to make a movie
x0 = 2.0
T = 310  # Initial temperature | ADJUST
dt = 0.005  # Time step
t = 0  # Time
m = 1  # Mass


# Subfunction to calculate PE and force
def force(r, s, w, delta):
    # OLD VALUES THAT WORK!
    V = V_x(r)
    F = V_x.deriv() #function notation is at odds with the potential one-liner 
    Fpot = -F(r)

    # print(r) #info

    Fbias = np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2))) # Metadynamics

    # Handle boundary conditions element-wise 
    V = np.where(r < -np.pi, 100 * (r + np.pi)**4, V) # V = 100(r + pi)^4 | I don't recognize this equation?
    F = np.where(r < -np.pi, -100 * 4 * (r + np.pi), Fpot + Fbias)
    
    V = np.where(r > np.pi, 100 * (r - np.pi)**4, V)
    F = np.where(r > np.pi, -100 * 4 * (r - np.pi), F)

    return V, F

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


# Loop over number of steps
if movieflag == 1:
    os.makedirs('movie', exist_ok=True)



# Plot 1D FES
xlong = np.arange(-np.pi, np.pi, 0.01)
vcalc, first = force(xlong, 0, w, delta)

# DIAGNOSTIC
# plt.plot(xlong, vcalc, label='V(x)', linewidth=2)
# plt.plot(xlong, first, label='F(x)', linewidth=2)
# plt.xlabel('CV (s)', fontsize=16)
# plt.ylabel('F(s) (arb)', fontsize=16)
# plt.grid()
# plt.legend()

# # INITIAL POINT! This will work with the animation
# plt.plot(xlong, vcalc)
# plt.plot([x0], [v], 'ro', markersize=10, markerfacecolor='r')
# plt.xlabel('s')
# plt.ylabel('F (arb)')


frame = 0

for i in range(steps):

    # Check if we should deposit a hill on the FES
    if i % hfreq == 0: #if no remainder
        s.append(q[i]) #append the step's potential to the empty sigma array?

    v, f = force(q[i], s, w, delta) # q[0] is already cast as x0
    R1 = np.random.rand() - 0.5
    R2 = np.random.rand() - 0.5

    pplus = c1 * p + c2 * R1 # eq 12a from Bussi and Parrinello
    q[i + 1] = q[i] + (pplus / m) * dt + f / m * (dt**2 / 2) # eq 12b
    v2, f2 = force(q[i + 1], s, w, delta) # obtain updated potentials and forces from updated position 
    pminus = pplus + (f / 2 + f2 / 2) * dt # prev momentum?
    p = c1 * pminus + c2 * R2 # eq12a, but calculating current step's momentum 

    E[i + 1] = 0.5 * p**2 + v2 # Updated energy, classic Newtonian eq

    if i % iratio == 0: 
        bias = vcalc.copy()
        if len(s) > 1: 
            for k in range(len(xlong)):
                bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))
                hills[k] = bias[k]
                
        v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # metad
        V[i] = v #THIS IS CRUCIAL
        
        print(f"""
        *******--- METADYNAMICS STEP ---*******
        step: {i}
        bias: {bias[k]}
        energy: {V[i]}
        radians: {q[i]}""")
    else:
        V[i] = v # we need to define an energy here
        hills[i] = 0
    print(f"""
        step: {i}
        energy: {V[i]}
        radians: {q[i]}""")

        #plot all deposited hills at once, but not at once?
        # plt.plot(xlong, bias, linewidth=4, color='red', label='Bias')
        # plt.plot(xlong, vcalc, linewidth=2, label='FES')
        # plt.plot([q[i + 1]], [v], 'ro', markersize=10, markerfacecolor='r')
        # plt.xlabel('CV (s)', fontsize=16)
        # plt.ylabel('F(s) (arb)', fontsize=16)



#####---Visualize the Integrator---######
# print(np.shape(V), np.shape(q))
# fig, ax = plt.subplots()


# scat = ax.scatter(q[0], V[0])
# ax.plot(xlong, vcalc) #underlying FES

# #close
# def update(frame):
#     radians = q[:frame:10]
#     energy = V[:frame:10]
#     data = np.stack([radians, energy]).T
#     scat.set_offsets(data)  # Update plot with the new data

# ax.set(xlim=[-np.pi, np.pi], ylim=[0, 100], 
#     xlabel = 'phi (radians)',
#     ylabel='Change in Free Energy')


# ani = animation.FuncAnimation(fig=fig, func=update, frames=5000, interval=1)


# plt.plot(q[0::10], V[0::10])

x = np.linspace(0, len(hills), len(hills))


hills_time(hills, x)


