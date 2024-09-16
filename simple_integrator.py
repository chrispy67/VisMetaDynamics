import numpy as np
import matplotlib.pyplot as plt
from dipep_potential import V_x
import matplotlib.animation as animation
import random

# Langevian integrator


# Deciding Potential


#r = radians
def Force(r, s, w, delta, potential):
    # Define EQs
    potential = V_x(r)
    F_x = potential.deriv() *-1   # F = -dV/dx

    # F(x) notation
    Fpot = F_x(potential)
    Fbias = np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2)))
    print('radians: ', r)

    # Sum biases 
    F = -Fpot + Fbias

    # Handle boundary conditions element-wise using np.where since r is an array
    V = np.where(r < -np.pi, 100 * (r + np.pi)**4, V)
    F = np.where(r < -np.pi, -100 * 4 * (r + np.pi), -Fpot + Fbias)
    
    V = np.where(r > np.pi, 100 * (r - np.pi)**4, V)
    F = np.where(r > np.pi, -100 * 4 * (r - np.pi), F)
    
    print(f"""potentail:{V}
    radians: {r}
    force: {F})
    """)

    return V, F


# Is this at odds with the Langevian Integrator??

# I know this issue is coming from improperly inputting radians into the force fxn
#   in the walker() main for loop. Force() calculates the bias as a fxn of radians,
#   but where is radians stored?? or updated otherwise??
def UpdatePotential(v, rad, timestep):
    #eqs
    F_x = V_x.deriv()  #F = -dV/dx
    F = F_x(rad) *-1

    accel = F  # point system with mass=1 since we already know the potential?

    newv = v + timestep*accel
    newrad = rad + timestep*newv
    return newv, newrad, accel


def walker():
    # MD Settings
    steps = 5
    x0 = 2.0 # Starting position (radians)
    T = 310 # Temp (Kelvin)
    dt = 0.005 # Timestep (ns)
    m = 1
    # Equations
    gamma = 5.0 # for c1 calc ONLY
    beta = 1/T/1.987e-3
    c1 = np.exp(-gamma*dt/2)
    c2 = np.sqrt((1-c1**2)*m/beta)

    # Metadynamics Parameters
    w = 0.4 #vwidth of the sigmas 
    delta = 0.1 #unsure
    hfreq = 3000 # hill frequency 

    # Initial configuration
    q = np.zeros(steps) # empty array to hold potentials 
    E = np.zeros(steps) # empty array to hold energies

    ######## ISSUE HERE; FIRST POTENTIAL CANT BE IN RADIANS??
    q[0] = x0 # first entry in potential array is the starting point
    v0 = np.random.rand() - 0.5 #random initial velocity

    p = v0 * m # momentum
    s = np.array([0]) #EMPTY SIGMA ARRAY

    v, f = Force(V_x(x0), s, w, delta) # calculate potential and force as function of starting configuration
    # do I need to calculate an initial value?
    E[0] = 0.5*p**2 + v # energy

    for i in range(1, steps):
        if i % hfreq == 0: # leaves no remainder, is factor of.
            s = np.append(s, q[i - 1]) # append previous energies
        v, f = Force(q[i-1], s, w, delta) # main force calc from previous step's potential

        R1 = random.random() - 0.5
        R2 = random.random() - 0.5

        pplus = c1*p + c2*R1 #eq 12 from Bussi, Parrinello

        q[i] = q[i-1] + (pplus/m)*dt + f/m*(dt**2/2) #calculate potential
        v2, f2 = Force(q[i], s, w, delta)
        pminus = pplus + (f/2+ f2/2) * dt
        p = c1*pminus + c2*R2
        E[i] = 0.5 * p**2 + v2

    return q, E

q, E = walker()

x = np.linspace(0, len(q), len(q))

plt.plot(x, q)
# plt.show()
plt.plot(x, E)
# plt.show()

#####---Visualize the integrator (diagnostic purposes)---######

# fig, ax = plt.subplots()

# x = np.linspace(-np.pi, np.pi, 100)
# x0 = -1.756488 

# #underlying FES
# F_x = V_x.deriv() *-1
# fes = ax.plot(x, V_x(x), label='POTENTIAL')
# # deriv = ax.plot(x, F_x(x), lw=1, label='FORCE')

# #must plot first point of the plot to be updated
# scat = ax.scatter(q[0], V_x(x0), label='potential')

# #plot params
# ax.set(xlim=[-np.pi, np.pi], ylim=[0, 100], xlabel = 'phi (radians)', ylabel='Change in Free Energy')


# def update(frame):
#     radians = q[:frame]
#     energy = E[:frame]
#     data = np.stack([radians, energy]).T
#     scat.set_offsets(data)

# #perform animation
# ani = animation.FuncAnimation(fig=fig, func=update, frames=200, interval=30)
# plt.legend()


# plt.show()
