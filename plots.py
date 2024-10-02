import matplotlib.pyplot as plt
import numpy as np
from dipep_potential import V_x
import matplotlib.animation as animation
import os


# - All of these functions should take in arrays and spit out a graph.
#   - but what if I want it to update EACH FRAME and plot LIVE data?
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
        
        else: #write backup file as bck.fes_{n}.png where n is lowest common integer
            while os.path.exists(os.path.join('static', f"bck.fes_{n}.png")):
                n += 1
            
            backup_path = os.path.join('static', f"bck.fes_{n}.png")
            os.rename(image_path, backup_path)


# This should work for updating both scatter and line plots. For later!
def update(frame, x_data, y_data, obj, plot_type='scatter'):
    # for each frame, update the data stored on each artist.
    x = x_data[:frame:10]
    y = y_data [:frame:10]
    
    if plot_type == 'scatter':
        offsets = np.column_stack((x, y))
        obj.set_offsets(offsets)
    elif plot_type == 'line':
        obj.set_data(x, y)
    else:
        raise ValueError('plot type not recognized')
    
    # updates artist objects to be read for animation
    return obj,

def hills_time(hills, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, hills)

    ax.set(xlabel='Time (ns)',
        ylabel='hill height (kcal/mol)',
        title='Evolution of Gaussian Height')
    return (fig, scat)

def rads_time(rad, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, rad, s=2)

    ax.set(xlabel='Time (ns)',
        ylabel='Dihedral angle (rad)', 
        title='Dihedral angle (φ) of Alanine Dipeptide')
    return (fig, scat)

def energy_time(energy, time):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, energy)

    ax.set(xlabel='Time (ns)',
        ylabel='Energy (kcal/mol)', 
        title='Potential Energy of Dihedral Angle')
    return (fig,scat)

#####-----Template for formatting images for the Flask app-----#####
# - This is the simplest case, other functions will be different
def fes(potential):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, 100)
    V = potential(x) # this is assuming np.poly1D function notation
    plot = ax.plot(x, V)

    ax.set(xlim=[-np.pi, np.pi], ylim=[0, 100], 
        xlabel = 'phi (radians)',
        ylabel='Change in Free Energy')

    
    
    # MUST ADD TO EACH FUNCTION I USE IF I WANT to populate the Flask application
    fig.savefig('static/fes.png')

    return (fig, plot)


def animate_md(V, hills, rads):

    # copied from fes()
    fig, ax = plt.subplots()
    
    # ensures equal length arrays
    x = np.arange(-np.pi, np.pi, (2*np.pi / len(hills)))
    
    #pre plots
    ax.plot(x, V_x(x), alpha=0.6, label='free energy surface')
    # ax.plot(x, hills, linewidth=2, label='Bias')
    
    # need to change the size (volume of the Gaussian) for each deposition
    scatter = ax.scatter(rads, V, s=3, label='simulation steps') #to be updated

    ani = animation.FuncAnimation(
    fig=fig, 
    func=update, 
    frames=len(V), # might want to make this fxn of input param (mratio)?
    fargs=(rads, V, scatter, 'scatter'),
    interval=1, 
    blit=False)

    ax.set(xlim=[-np.pi, np.pi], ylim=[0, 100], 
        xlabel = 'phi (radians)',
        ylabel='Change in Free Energy',
        title='Metadynamics Simulation of Alanine Dipeptide Dihedral Angle')

    # This either takes a REALLY long time or isn't working 
    # ani.save('MD_simulation.gif', writer='pillow', fps=30)
    # plt.show() #must be inside the function, NOT walker.py to pass animation

    return ani  



