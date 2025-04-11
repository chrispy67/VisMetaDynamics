import numpy as np
import argparse
import pickle
import config as config
import time
import matplotlib.pyplot as plt
import json

from walker import CLI, integrator_performance, update_progress, walker

def umbrella_sampling(kappa=500, bins=2):

    from V_x_functions import V_x
    
    try:
        with open("V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)

    except FileNotFoundError:
        with open("src/V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)
    
    # retstep=True gives us the spacing between windows, what fun!
    windows, spacing = np.linspace(-np.pi, np.pi, bins, retstep=True)

    # this acts as a ZERO INDEX for windows 
    centers = np.linspace(0, len(windows) - 1, bins, dtype=int)

    x = np.linspace(-np.pi, np.pi, 100)
    known_potential = V_x_class.potential(x) 

    ###---Visualizing US windows and harmonic restraints---###
    plt.figure(figsize=(10, 6))
    for center in centers:
        
        underlying_potential = V_x_class.potential(windows[center]) 
        c = 0.5 * kappa

        pot = c * (x - windows[center]) **2  

        # I need to refactor walker.py to handle different potentials
        summary = walker(
            steps = config.steps,
            x0 = config.x0, 
            T = config.temp,
            metad=False, 
            w = config.w, 
            delta =config.delta, 
            hfreq = config.hfreq)
        plt.plot(x, pot + underlying_potential)

    plt.plot(x, known_potential, label='known potential')

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
    




