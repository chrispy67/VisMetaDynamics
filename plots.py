import matplotlib.pyplot as plt
import numpy as np
from dipep_potential import V_x
import matplotlib.animation as animation

# - All of these functions should take in arrays and spit out a graph.
#   - but what if I want it to update EACH FRAME and plot LIVE data?


def update(x_data, y_data, frame, plot):
    # for each frame, update the data stored on each artist.
    x = x_data[:frame]
    y = y_data [:frame]
    # update the scatter plot:
    data = np.stack([x, y]).T
    plot.set_offsets(data)
    # update the line plot:
    return (plot, data)

# Universal values 
plt.rcParams["axes.grid"] = True  # Enables grid for all plots

#fx of time or fx of steps??? time is certainly more interpretable

def hills_time(hills, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time[0], hills[0])
    return scat

def rads_time(rad, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time[0], rad[0])
    return scat
    

def energy_time(energy, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time[0], energy)
    return scat

# this should be static
def fes(potential):
    x = np.linspace(-np.pi, np.pi, 100)
    V = V_x(x)
    plot = plt.plot(x, V)
    return plot

