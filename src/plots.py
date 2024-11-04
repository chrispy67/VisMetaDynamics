import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import os
from src import config
import pickle
from V_x_functions import V_x   

try:
    with open("V_x_functions.pkl", "rb") as f:
        import V_x_functions
        V_x_class = pickle.load(f)

# Trying to get around source issue when importing as module
except FileNotFoundError:
    with open("src/V_x_functions.pkl", "rb") as f:
        V_x_class = pickle.load(f)



# - All of these functions should take in arrays and spit out a graph.
# - Function of time or function of steps??? time is certainly more interpretable

# Universal values | font size, colors, etc
plt.rcParams["axes.grid"] = True  # Enables grid for all plots

def clear_images(image_path, overwrite=True):
    """
    Because this application may be run many times, this is the best way to ensure that
    the files produced by walker.py from previous runs to do not populate the image.
    """
    if os.path.exists(image_path):
        if overwrite: #is True, keeping the files in place
            os.remove(image_path)
        
        else: #write backup file as bck.fes_{n}.png where n is lowest common integer (a la Plumed backup syntax)
            while os.path.exists(os.path.join('static', f"bck.fes_{n}.png")):
                n += 1
            
            backup_path = os.path.join('static', f"bck.fes_{n}.png")
            os.rename(image_path, backup_path)


mratio = 10 # as mratio increases, time between each frame increases

# This should work for updating both scatter and line plots. For later!
def update(frame, x_data, y_data, obj, plot_type='scatter'):
    # for each frame, update the data stored on each artist.
    x = x_data[:frame:mratio]
    y = y_data [:frame:mratio]
    # print(f"len(x): {len(x)}") # diagnostic
    
    if plot_type == 'scatter':
        offsets = np.column_stack((x, y))
        obj.set_offsets(offsets)
    elif plot_type == 'line':
        obj.set_data(x, y)
    else:
        raise ValueError('plot type not recognized')
    
    # updates artist objects to be read for animation
    return obj,


def hills_time(hills, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, hills)

    ax.set(xlabel='Time (ns)',
        ylabel='hill height (kcal/mol)',
        title='Evolution of Gaussian Height')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
    
    return (fig, scat)

def rads_time(rad, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, rad, s=2)

    ax.set(xlabel='Time (ns)',
        ylabel='Dihedral angle (rad)', 
        title='Dihedral angle (φ) of Alanine Dipeptide')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)

    plt.close()
    return (fig, scat)

def energy_time(energy, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, energy)

    ax.set(xlabel='Time (ns)',
        ylabel='Energy (kcal/mol)', 
        title='Potential Energy of Dihedral Angle')
    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
    return (fig,scat)

#####-----Template for formatting images for the Flask app-----#####
# - This is the simplest case, other functions will be different
def fes(save_path = None):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, 600)
    V = V_x_class.potential(x) # this is assuming np.poly1D function notation
    plot = ax.plot(x, V)

    ax.set(xlim=[-np.pi, np.pi], ylim=[-25, 100], 
        xlabel = 'phi (radians)',
        ylabel='Change in Free Energy')
    
    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
    return (fig, plot)


def reweight(bias, save_path = None):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, len(bias))

    bias_array = np.array(bias)

    #F(s, t) ~= -V(s, t) + C
    C = (bias - np.min(bias)) #normalization constant of integration? Need help here
    # print(C)
    # plt.plot(x, -bias - C, label='Correct for C')
    plot = plt.plot(x, -bias_array, label='-bias')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)

    plt.close()
    return (fig, plot)


# if steps < frames: sim is cut short
# if steps = frames: sim is way too long to watch or save
# if steps > frames: we have something we can work with. but how to make this ratio flexible?

def animate_md(V, hills, rads):
    # copied from fes()
    fig, ax = plt.subplots()
    frames = len(rads) 
    
    # ensures equal length arrays
    x = np.arange(-np.pi, np.pi, (2*np.pi / len(hills)))

    #pre plots
    ax.plot(x, V_x_class.potential(x), alpha=0.6, label='free energy surface')
    # ax.plot(x, hills, linewidth=2, label='Bias')
    
    # need to change the size (volume of the Gaussian) for each deposition
    scatter = ax.scatter(rads, V, s=3, label='simulation steps') #to be updated

    # Goal here is to make an animation that is:
        # NOT TOO LARGE OF A FILE (cap frames?)
        # NOT TOO LONG (mratio?) BUT SHOWS THE WHOLE SIMULATION (mratio will cut it short)
        # EASY TO LOOK AT 
        # PORTABLE (see 1 and 2)
        # RESPONSIVE (is there a faster way to draw this?)
    ani = animation.FuncAnimation(
    fig=fig, 
    func=update, 
    frames=frames, # must be integer | WILL TRUNCATE SIMULATION
    fargs=(rads, V, scatter, 'scatter'),
    interval=1, 
    blit=True)

    ax.set(xlim=[-np.pi, np.pi], ylim=[-25, 100], 
        xlabel = 'phi (radians)',
        ylabel='Change in Free Energy',
        title='Metadynamics Simulation of Alanine Dipeptide Dihedral Angle')

    # This is the rate limiting step here. For minimum steps and mratio of 10, just one of these GIFs is absurdly large. 
    # ani.save('static/MD_simulation.gif', writer='ffmpeg', fps=30)
    plt.show() #must be inside the function, NOT walker.py to pass animation

    return ani  



