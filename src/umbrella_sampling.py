import numpy as np
import argparse
import pickle
import config as config
import time
import matplotlib.pyplot as plt
import json

from walker import CLI, integrator_performance, update_progress, walker


from V_x_functions import V_x, UmbrellaPotential

try:
    with open("V_x_functions.pkl", 'rb') as f:
        V_x_class = pickle.load(f)

except FileNotFoundError:
    with open("src/V_x_functions.pkl", 'rb') as f:
        V_x_class = pickle.load(f)


# Will likely add user config input HERE
def umbrella_config(kappa, bins, write):

    # This function takes in arguments needed for the integrator and writes to a config file

    windows = np.linspace(-np.pi, np.pi, bins)

    # Zero index for windows
    centers = np.linspace(0, len(windows) - 1, bins, dtype=int)

    # Writing these parameters to a config file to 'meet in the middle' with walker.py and this script
    # Adding write bool if i want to avoid overwriting user parameters
    if write is True:
        try:
            with open('src/umbrella_config.py', 'w') as f:
                f.write(f"#This config file written by src/umbrella_sampling.py\n")
                f.write(f"import numpy as np\n")
                f.write(f"us = True")
                f.write(f"kappa = {kappa}\n") # string
                f.write(f"bins = {bins}\n") # string
                f.write(f"windows = np.array({np.array2string(windows, separator=', ')})\n")
                f.write(f"centers = np.array({np.array2string(centers, separator=', ')})\n")

        except Exception as e:
            print(e)

    return kappa, bins, windows, centers


def umbrella_sampling_visual():

    # from src import umbrella_config as uc # IMPORT AFTER WRITING CONFIG FILE
    import umbrella_config as uc
    kappa = uc.kappa
    bins = uc.bins
    centers = uc.centers
    windows = uc.windows
    
    x = np.linspace(-np.pi, np.pi, 100)
    plt.figure(figsize=(10, 6))


    for center in centers:
        # This is the value of the KNOWN, underlying potential at the center of the restraint
        underlying_potential = V_x_class.potential(windows[center]) 

        harmonic_potential = 0.5 * kappa * (x - windows[center]) ** 2

        # THIS PLOTS THE WINDOWS OVER THE KNOWN POTENTIAL
        plt.plot(x, harmonic_potential + underlying_potential)


    plt.plot(x, V_x_class.potential(x), label='known potential', linestyle='--')

    plt.xlim(-10, 10)
    plt.ylim(-25, 100)
    plt.grid(True)
    plt.legend()
    plt.show()
    


if __name__ == '__main__':
    
    # Pass user arguments and WRITE to config file
    umbrella_config(300, 15, write=True)
    import umbrella_config as uc
    from plots import animate_md

    # Load visualization (WIP)
    umbrella_sampling_visual()

    simulation_ensemble = {}

    for center in uc.centers:        
        window = walker(
            steps = config.steps,
            x0 = uc.windows[center],
            T = config.temp,
            metad = False,
            w = config.w, # OFF
            delta = config.delta, # OFF
            hfreq = config.delta, # OFF
            us = True, 
            kappa = uc.kappa, # force constant in kJ/mol
            center = uc.windows[center] # center of harmonic restraint in RADIANS is starting point and must be passed to integrator
        )

        x = np.linspace(0, len(window['q']), len(window['q']))
        # plt.plot(x, window['q'], label = f'window {center}')
        plt.plot(x, window['us_force'], label=f'window {center}')

        simulation_ensemble[f'Window{center}'] = window

    # plt.plot(x, simulation_ensemble['Window1']['us_force'])
    plt.legend()
    plt.show()

    # print(simulation_ensemble['Window1']['us_force'])
    # animate_md(simulation_ensemble['Window1']['V'], simulation_ensemble['Window1']['q'])


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
    




