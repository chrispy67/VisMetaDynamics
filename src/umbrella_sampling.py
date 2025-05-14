import numpy as np
import argparse
import pickle
import config as config
import time
import matplotlib.pyplot as plt
import json

from walker import CLI, integrator_performance, update_progress, walker
from plots import animate_md


def umbrella_sampling(kappa=100, bins=20):

    from V_x_functions import V_x, UmbrellaPotential
    
    try:
        with open("V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)

    except FileNotFoundError:
        with open("src/V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)
    
    
    windows, spacing = np.linspace(-np.pi, np.pi, bins, retstep=True)
    print('Window centers (rad):', windows)

    # this acts as a ZERO INDEX for windows 
    centers = np.linspace(0, len(windows) - 1, bins, dtype=int)

    x = np.linspace(-np.pi, np.pi, 100)

    # The default underlying potential is still used in walker.py
    ###---Visualizing US windows and harmonic restraints---###
    plt.figure(figsize=(10, 6))

    sim_ensemble = {}

    ## MAIN LOOP FOR BINNING 
    for center in centers:

        # This is the value of the KNOWN, underlying potential at the center of the restraint
        underlying_potential = V_x_class.potential(windows[center]) 

        # Harmonic restraint as fxn of centers. 
        umbrella_potential = UmbrellaPotential(center=windows[center], kappa=kappa, bins=bins)

        summary = walker(
            steps = config.steps,
            x0 = windows[center], # STARTING POINT IS BOTTOM OF WELL/ CENTER OF HARMONIC RESTRAINT 
            T = config.temp,
            metad=False, 
            w = config.w, 
            delta =config.delta, 
            hfreq = config.hfreq,
            
            # Passing a harmonic restraint to walker.py to override default behavior
            V_x=umbrella_potential) # THIS NEEDS TO BE HARMONIC RESTRAINT
        
        
        sim_ensemble[f'Window{center}'] = summary
        sim_time = np.linspace(0, config.steps+1, config.steps+1)

        # THIS PLOTS THE WINDOWS OVER THE KNOWN POTENTIAL
        plt.plot(x, umbrella_potential.potential(x) + underlying_potential)


    # Something is up with the force() function and the imported potential?
    # print(sim_ensemble['Window1']['V'])


    plt.plot(x, V_x_class.potential(x), label='known potential', linestyle='--')

    plt.xlim(-10, 10)
    plt.ylim(-25, 60)
    plt.grid(True)
    plt.legend()
    plt.show()
    


if __name__ == '__main__':


    umbrella_sampling()

    ###---Umbrella Sampling---###
    # Arguments given to a simple PLUMED simulation are:
    #   - KAPPA (kJ/mol) 
    #   - AT (radians) which is the center of the restraint

    # Simulation arguments for adequate sampling:
    #   - BINS!! 
    #       AKA how many independent configurations/simulations? 
    #       I don't believe that harmonic potentials are supposed to overlap? 
    #   - FORCE CONSTANT (KAPPA)
    #       Affects the 'width' of each window. 
    #       However, it seems that my 'system'doesn't move very freely based on building thet metad tutorial. Perphas there is some parameter in walker.py that I am overlooking like gamma?
    




