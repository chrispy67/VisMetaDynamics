import numpy as np
import argparse
import pickle
import config as config
import time
import matplotlib.pyplot as plt
import json

# Define parameters that aren't set by user
mratio = 10 # sets log ratio for site progress bar AND logger

dt = 0.02  # Time step is FIXED now
t = 0  # Time
m = 1  # Mass

def integrator_performance(t_start, t_end):
    delta_t = t_end - t_start
    ns_day = (config.steps / delta_t) * dt * 86400 # nanoseconds per day

    performance_summary = {
        'sim_time': delta_t,
        'ns/day': ns_day, 
    }

    return performance_summary

# overwrites progress bar value as .json as function of mratio
def update_progress(value):
    with open('static/.progress.json', 'w') as f:
        json.dump({"value": value}, f)

# Primary MD Engine
# All functions that are necessary to these calculations are INSIDE THIS FUNCTION
def walker(steps, x0, T, metad, w, delta, hfreq):
    
    t0 = time.time()
    # Load in potential
    try: # Running as script
        with open ('V_x_functions.pkl', 'rb') as f:
            V_x_class = pickle.load(f)

    except FileNotFoundError: # Running as MODULE
        with open('src/V_x_functions.pkl', 'rb') as f:
            V_x_class = pickle.load(f)

    # Subfunction to calculate PE and force
    def force(r, s, w, delta):
        r = pbc(r)
        V = V_x_class.potential(r)
        F = V_x_class.force(r) #function notation is at odds with the potential one-liner 
        Fpot = -F

        if metad:
            Fbias = np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2))) # Metadynamics eq
        else:
            Fbias = 0
        return V, Fpot + Fbias

    def pbc(r, bc=np.pi):
        # This potential is on the domain [-π, π]. Any other potential is going to need another PBC function!
        if r > bc:
            return r - 2 * bc

        elif r < -bc:
            return r + 2 * bc

        else:
        # If r is within [-π, π], no adjustment is needed
            return r

        # Deprecated 11/11 as it is INCORRECT
        # return (((r + bc) % (2 * bc)) - bc) 

    # Metadynamics functions and equations
    gamma = 5.0 #
    beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol ### UNIT CHECK
    c1 = np.exp(-gamma * dt / 2)
    c2 = np.sqrt((1 - c1**2) * m / beta)

    
    # Empty arrays to store information and underlying potential
    xlong = np.linspace(-np.pi, np.pi, 100) #len of bias array is directly related to this. 
    q = np.zeros(steps + 1) # Making room for final radian
    E = np.zeros(steps + 1) # Making room for final energy
    V = np.zeros(steps + 1) # Making room for final potential
    bias = np.zeros((len(xlong)), dtype=float) # this array does NOT need to change size; bias[-1] = is just the last entry

    # Initial configurations 
    q[0] = x0
    v0 = np.random.rand() - 0.5 #random initial potential
    p = v0 * m
    s = [0]
    v, f = force(q[0], 0, w, delta)
    E[0] = 0.5 * p**2 + v

    for i in range(steps):
        # Check if we should deposit a hill on the FES
        if metad:
            s = np.append(s, q[i]) if i % hfreq == 0 else s # append a sigma as fxn of hfreq s[i % hfreq]

    #####---Langevian integrator (https://doi.org/10.1103/PhysRevE.75.056707)---#####
        v, f = force(pbc(q[i]), s, w, delta) # q[0] is already cast as x0
        R1 = np.random.rand() - 0.5
        R2 = np.random.rand() - 0.5

        pplus = c1 * p + c2 * R1 # eq 12a from Bussi and Parrinello

    #####---WRAPPING NEW POSITION IN PBC FUNCTIONS---#####
        q[i + 1] += pbc(q[i] + (pplus / m) * dt + f / m * (dt**2 / 2)) # eq 12b w/ PBC effect
        v2, f2 = force(q[i + 1], s, w, delta) # obtain updated potentials and forces from updated position 
        pminus = pplus + (f / 2 + f2 / 2) * dt # prev momentum
        p = c1 * pminus + c2 * R2 # eq12a, but calculating current step's momentum 

        E[i + 1] = 0.5 * p**2 + v2 # Updated energy, classic Newtonian eq 

        if metad:
            if i % hfreq == 0: 
                if len(s) > 1: 

                    for k in range(len(xlong)):

                        rad_k = xlong[k] # where on the x-axis we are biasing

                        # A simple harmonic restraint. OG
                        bias_k = w * np.exp(-(rad_k - np.array(s)) ** 2 / (2 * delta**2)) #Bias(rads) and length increases each hfreq

                        # Dimensions of gaussian
                        mean_s = np.mean(bias_k)
                        sigma_s = np.std(bias_k)

                        ####---HANDLING PBC OF GAUSSIAN ---#####
                        if rad_k + (mean_s + 4 * sigma_s) > np.pi: # the 2d gaussian stretches arcross π
                            # print(f'**PBC ENCOUNTERED AT π (step {i}) at summation on {rad_k} radians**:')
                            # print(f'dimensions of sigma: {mean_s} ± {sigma_s}')
                            # print(f'added to the following bin: {k}')
                            # print('\n')
                            bias[k - len(xlong)] += np.sum(bias_k)

                        if rad_k - (mean_s - 4 * sigma_s) < -np.pi: # the 2d gaussian stretches arcross -π
                            # print(f'**PBC ENCOUNTERED AT- π (step {i}) at summation on {rad_k} radians**:')
                            # print(f'dimensions of sigma: {mean_s} ± {sigma_s}')
                            # print(f'added to the following bins: {k}')
                            # print('\n')
                            bias[k + len(xlong)] += np.sum(bias_k)

                        else:
                            # print(f'**PBC ENCOUNTERED AT- π (step {i}) at summation on {rad_k} radians**:')
                            # print(f"**NORMAL CASE ENCOUNTERED (step {i}) at summation on {rad_k}")
                            # print(f'dimensions of sigma: {mean_s} ± {sigma_s}')
                            # print(f'added to the following bins: {k}')
                            # print('\n')
                            bias[k] += np.sum(bias_k) #summation step

                        # PRIOR TO THINKING ABOUT PBC
                        # bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))


            # append the biased potential to existing potential 
            v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # main metad step
            
            V[i] = v #THIS IS CRUCIAL!!

        else:
            V[i] = v # Store unbiased potential 

        if i % mratio == 0: 

            # mratio is also tied to progress bar
            progress_value = int((i / steps) * 100)
            try:
                update_progress(progress_value)
            
            except FileNotFoundError:
                pass


    tplus = time.time()
    PERFORMANCE_SUMMARY = integrator_performance(t0, tplus)

    # A dict{} is a nice way to store the simulation data
    SIMULATION_DATA ={
        'bias': bias.tolist(),
        'q': q.tolist(),
        'V': V.tolist(),
        'E': E.tolist(),
        
    }

    # Now that I am moving this data as a JSON 
    SIMULATION_DATA.update(PERFORMANCE_SUMMARY)
    
    return SIMULATION_DATA


if __name__ == '__main__':
    import time
    from plots import animate_md, fes, neg_bias, rads_time, histogram
    # If you want to pickle a class, the same script MUST know the format of the class
    from V_x_functions import V_x   

    try:
        with open("V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)

    except FileNotFoundError:
        with open("src/V_x_functions.pkl", 'rb') as f:
            V_x_class = pickle.load(f)

    # Start timer now since it is used in the parsing logic
    t0 = time.time()

    ###--Parse optional commandline arguments for debugging purposes or alternate usecase--###
    parser = argparse.ArgumentParser(description="A command line interface for producing the same figures and data found on the Flask site. Check default values!!")

    parser.add_argument('-steps', '--steps',
        type = str,
        default = '1000',
        help = 'Number of simulation steps to be performed')
    
    parser.add_argument('-t', '--temp',
        type = str, 
        default = '310',
        help = 'Temperature of system in Kelvin. This integrator does not use a complex thermostat found in standard MD engines')

    parser.add_argument('-x0', '--x0',
        type = str,
        default = '0.01', 
        help = 'Starting point of the dihedral angle')
    
    parser.add_argument('-metad', '--metad',
        action='store_true',
        help = 'turn metadynamics on/off')

    parser.add_argument('-w', '--w',
        type = str,
        default = '1.2',
        help = 'Height of deposited gaussians in units of energy')

    parser.add_argument('-delta', '--delta',
        type = str, 
        default = '0.01',
        help = 'The width of the depoostied gaussians in units of the collective variable (radians)')

    parser.add_argument('-hfreq', '--hfreq', '--frequency', 
        type = str,
        default = '50',
        help = 'Rate of hill deposition in terms of simulation steps.')

    args = parser.parse_args()

    # Error handling for user responses
    try:
        if int(args.steps) <= 0:
            raise ValueError("Simulation steps must be a positive integer.")
        
        if int(args.temp) <= 0:
            raise ValueError("Simulation temperature must be positive integer. Reminder, this is in Kelvin!")

        if float(args.x0) < -np.pi or float(args.x0) > np.pi:
            raise ValueError("The collective variable in this tutorial is a dihedral angle it is periodic on the domain [-π, π]. Enter whole numbers between -3 and 3.")
        
        if not args.metad:
            # In case metadynamics was turned off, this would avoid conflicts with default values for metadynamics paramters; crucial!
            args.w = '0.0'
            args.delta = '0.0'
            args.hfreq = '0.0'
        
        if float(args.w) < 0:
            raise ValueError("Gaussian weight must be a positive floating point number, preferrably between 0.1 and 5")

        if float(args.delta) < 0:
            raise ValueError("Gaussian width must be a positive floating point number, preferrably between 0.01 and 1")

        if float(args.hfreq) < 0:
            raise ValueError("Frequency of gaussian deposition must be a positive integer, preferrably between 10 and 500")

    except ValueError as e:
        print(e)
        exit(1)

    # build a dictionary of all the arguments that have been PARSED or given default values
    args_dict = vars(args)
    print(args_dict)
    with open('src/config.py', 'w') as f:
        f.write(f"#These parameters were written by the commandline interface of walker.py @ {t0}\n")

        # Ensuring that the arguments being written in config.py are the SAME that are being referenced all throughout this program
        # These are EXACTLY how they are written in config.py. Perhaps more flexibility should be added...
        config_list = ['steps', 'temp', 'x0', 'metad', 'w', 'delta', 'hfreq']
        
        # Loop through each parsed argument and write it to config.py. 
        for key, value in args_dict.items():
            if key in config_list:
                f.write(f"{key} = {value}\n") 
        f.close()
        
    print("Parameters written to src.config.py")
    
    # The import AFTER writing all these parameters is crucial 
    import config as config

    ###--Beginning the main Metadynamics logic and calling integrator--###
    summary_dict = walker(config.steps, config.x0, config.temp,
        config.metad, config.w, config.delta, config.hfreq)
    
    tplus = time.time()
    
    # Need to define generic domain because of new class notation
    x = np.linspace(-np.pi, np.pi, 100)
    sim_time = np.linspace(0, config.steps+1, config.steps+1) * dt #ns
    
    # Generates plots that populate Flask page and appear in matplitlib window (CLI)
    fes()
    neg_bias(summary_dict['bias'], summary_dict['q'])
    rads_time(summary_dict['q'], sim_time)
    animate_md(summary_dict['V'], summary_dict['bias'], summary_dict['q'])


    # Basic printout for performance
    print(f" Simulation time: {summary_dict['sim_time']} seconds")
    print(f" Simulation performance: {summary_dict['ns/day']} ns/day ")

    plt.show()