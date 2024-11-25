import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import config
import pickle
from V_x_functions import V_x  
import time
from matplotlib.ticker import FixedLocator, FixedFormatter


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
# matplotlib.rcParams['animation.ffmpeg_args'] = '-threads 4'


mratio = 10 # as mratio increases, time between each frame increases

# This should work for updating both scatter and line plots. For later!
def update(frame, x_data, y_data, obj):
    # for each frame, update the data stored on each artist.
    x = x_data[:frame:mratio]
    y = y_data [:frame:mratio]
    
    offsets = np.column_stack((x, y))
    obj.set_offsets(offsets)
    
    # Updates artist objects to be read for animation
    return obj,


def hills_time(hills, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, hills)

    ax.set(xlabel='Time (ns)',
        ylabel='hill height (kcal/mol)',
        title='Evolution of Gaussian Height')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
        plt.close()
    return (fig, scat)

def rads_time(rad, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, rad, s=2, color='#6b4f9e')

    ax.set_xlabel('Time (ns)', fontweight='bold')
    ax.set_ylabel('Dihedral angle (radians)', fontweight='bold')
    ax.set_title('Dihedral Angle (φ) of Alanine Dipeptide', fontweight='bold')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
        plt.close()

    return (fig, scat)

def energy_time(energy, time, save_path = None):
    fig, ax = plt.subplots()
    scat = ax.scatter(time, energy)

    ax.set_xlabel('Time (ns)', fontweight='bold')
    ax.set_ylabel('Energy (kcal/mol)', fontweight='bold')
    ax.set_title('Potential Energy of φ Dihedral Angle on Alanine Dipeptide')

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
        plt.close()
    return (fig,scat)

#####-----Template for formatting images for the Flask app-----#####
# - This is the simplest case, other functions will be different
def fes(save_path = None):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, 600)
    V = V_x_class.potential(x) # this is assuming np.poly1D function notation
    plot = ax.plot(x, V, color='#6b4f9e')

    ax.set_xlabel('φ Dihedral Angle (radians)', fontweight='bold')
    ax.set_ylabel('Δ Free Energy (kcal)', fontweight='bold')
    ax.set_title('Underlying Potential Energy Defined by Integrator', fontweight='bold')
    ax.set(xlim=[-np.pi, np.pi], ylim=[-25, 100])
    
    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
        plt.close()
    return (fig, plot)


def reweight(bias, save_path = None):
    fig, ax = plt.subplots()
    x = np.linspace(-np.pi, np.pi, len(bias))

    bias_array = np.array(bias) - np.max(bias)

    ax.set_xlabel('φ Dihedral Angle (radians)', fontweight='bold')
    ax.set_ylabel('Δ Free Energy (generic units)', fontweight='bold')
    ax.set_title('Free Energy of Dihedral Angle (φ) of Alanine Dipeptide', fontweight='bold')
    

    #F(s, t) ~= -V(s, t) + C
    plot = plt.plot(x, -bias_array, label='-bias', color='#6b4f9e')

    # Generic energy units here for y-axis
    yticks = ax.get_yticks()  # Get the current tick positions
    tick_scale = str(yticks[-1])  # Find the max value of the FES AFTER min-to-zero correction
    new_ytick_scale = [str(float(label / 10**len(tick_scale))) for label in yticks]  # Scale tick labels

    # Apply FixedLocator and FixedFormatter
    ax.yaxis.set_major_locator(FixedLocator(yticks))  # Set tick positions
    ax.yaxis.set_major_formatter(FixedFormatter(new_ytick_scale))  # Set formatted labels

    if save_path:
        fig.savefig(save_path, format='png', dpi=300)
        plt.close()
    return (fig, plot)


def animate_md(V, hills, rads, save_path = None):
    # copied from fes()
    fig, ax = plt.subplots()
    t_0 = time.time()


    frames = range(0, len(rads), 300)
    
    # ensures equal length arrays
    x = np.arange(-np.pi, np.pi, (2*np.pi / len(hills)))

    #pre plots
    ax.plot(x, V_x_class.potential(x), alpha=0.6, label='free energy surface', color='black')
    
    # need to change the size (volume of the Gaussian) for each deposition
    scatter = ax.scatter(rads, V, s=2, label='simulation steps', color='#6b4f9e') #to be updated

    ani = animation.FuncAnimation(
    fig=fig, 
    func=update, 
    frames=frames, 
    fargs=(rads, V, scatter),
    interval=30, 
    blit=True)

    ax.set_xlabel('φ Dihedral Angle (radians)', fontweight='bold')
    ax.set_ylabel('Δ Free Energy (kcal)', fontweight='bold')
    ax.set_title('Metadynamics Simulation of Alanine Dipeptide Dihedral Angle', fontweight='bold')

    # This is the rate limiting step here. For minimum steps and mratio of 10, just one of these GIFs is absurdly large. 
    # ani.save('static/MD_simulation.gif', writer='ffmpeg', fps=30)

    if save_path:
        writervideo = animation.FFMpegWriter(fps=60, bitrate=2000, codec='libx264')
        ani.save(save_path, writer=writervideo)
        plt.close()

    tplus = time.time()
    # print(f"Time to save simulation: {tplus - t_0:.4f} seconds")
    plt.show() #must be inside the function, NOT walker.py to pass animation

    return ani  



