import matplotlib.pyplot as plt
import numpy as np
from dipep_potential import V_x
import matplotlib.animation as animation

# - All of these functions should take in arrays and spit out a graph.
#   - but what if I want it to update EACH FRAME and plot LIVE data?
# - Function of time or function of steps??? time is certainly more interpretable

# Universal values 
plt.rcParams["axes.grid"] = True  # Enables grid for all plots



# This should work for updating both scatter and line plots. For later!
def update(frame, x_data, y_data, obj, plot_type='scatter'):
    # for each frame, update the data stored on each artist.
    x = x_data[:frame]
    y = y_data [:frame]
    
    if plot_type == 'scatter':
        offsets = np.column_stack((x, y))
        obj.set_offsets(offsets)
    elif plot_type == 'line':
        obj.set_data(x, y)
    else:
        raise ValueError('plot type not recognized')

def hills_time(hills, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, hills)
    return (fig, scat)

def rads_time(rad, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time[0], rad[0])
    return (fig, scat)


def energy_time(energy, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time[0], energy)
    return (fig,scat)

# this should be static and doesn't need updates
def fes(potential):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, 100)
    V = V_x(x)
    plot = ax.plot(x, V)

    ax.set(xlim=[-np.pi, np.pi], ylim=[0, 100], 
        xlabel = 'phi (radians)',
        ylabel='Change in Free Energy')
    return (fig, plot)

