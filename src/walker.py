import numpy as np
import logging
import argparse
import pickle
import config as config
import json
import time
from plots import animate_md, fes
import matplotlib.pyplot as plt

# Parse arguments and python logger options
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='set log level')
parser.add_argument('--log', default='INFO', help='log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
args = parser.parse_args()

# Helper function for logger
def setup_logger(level):
    logging.basicConfig(level=level,
    format='%(levelname)s:%(message)s',
    filename='MD_sim.log')

log_level = getattr(logging, args.log.upper(), None)
setup_logger(log_level)

# Define parameters that aren't set by user
mratio = 10 #what to do here? Maybe this is something I enforce a min/max for as a function of steps?
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

    # Lean periodic boundary condition function for improving performance
    def pbc(r, bc=np.pi):
        # This potential is on the domain [π, π]. Any other potential is going to need another PBC functions
        return (((r + bc) % (2 * bc)) - bc) 

    # Metadynamics functions and equations
    gamma = 5.0 #
    beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol
    c1 = np.exp(-gamma * dt / 2)
    c2 = np.sqrt((1 - c1**2) * m / beta)

    
    # Empty arrays to store information and underlying potential
    xlong = np.arange(-np.pi, np.pi, 0.01) #len of bias array is directly related to this. 
    q = np.zeros(steps + 1) # Making room for final radian
    E = np.zeros(steps + 1) # Making room for final energy
    V = np.zeros(steps + 1) # Making room for final potential
    bias = np.zeros((len(xlong) + 1, ), dtype=float) # this array does NOT need to change size; bias[-1] = is just the last entry

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
            s = np.append(s, q[i]) if i % hfreq == 0 else s # append a sigma as fxn of hfreq

    #####---Langevian integrator (https://doi.org/10.1103/PhysRevE.75.056707)---#####
        v, f = force(q[i], s, w, delta) # q[0] is already cast as x0
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
                logger.info(f"""
            *******--- METADYNAMICS STEP ---*******
            step: {i}
            energy: {V[i]}
            radians: {q[i]}""")
                if len(s) > 1: 
                    for k in range(len(xlong)):
                    
                    ####---HANDLING PBC OF GAUSSIAN ---#####
                        # V(s) is where I want to intervene, NOT V(s, t). 
                        # But the dimensions of the bias added to the gaussian need to be checked for periodicity

                        bias_k = w * np.exp(-(xlong[k] - np.array(s)) ** 2 / (2 * delta**2)) #Bias(rads)
                        rad_k = xlong[k] # where on the x-axis we are biasing

                        #dimensions of gaussian
                        mean_s = np.mean(bias_k)
                        sigma_s = np.std(bias_k)

                        if rad_k + (mean_s + 5 * sigma_s) > np.pi: # the 2d gaussian stretches arcross π
                            bias[k - len(xlong)] += np.sum(bias_k)

                        if rad_k - (mean_s - 5 * sigma_s) < -np.pi: # the 2d gaussian stretches arcross -π
                            bias[k + len(xlong)] += np.sum(bias_k)

                        else:
                            bias[k] += np.sum(bias_k) #summation step

                        # PRIOR TO THINKING ABOUT PBC
                        # bias[k] += np.sum(w * np.exp(-(xlong[k] - np.array(s))**2 / (2 * delta**2)))


            # append the biased potential to existing potential 
            v += np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2))) # main metad step

            V[i] = v #THIS IS CRUCIAL!!

        else:
            V[i] = v # Store unbiased potential 
            bias = 0

        if i % mratio == 0: 
            logger.info(f"""
                step: {i}
                energy: {V[i]}
                radians: {q[i]}""")


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

# summary_dict = walker(config.steps, config.x0, config.temp, 
#     config.metad, config.w, config.delta, config.hfreq)


# fes()
# animate_md(summary_dict['V'], summary_dict['bias'], summary_dict['q'])
# plt.show()
# print(json.dumps(summary_dict))


if __name__ == '__main__':
    import config as config 
    import time
    
    # If you want to pickle a class, the same script MUST know the format of the class
    from V_x_functions import V_x   

    with open("V_x_functions.pkl", 'rb') as f:
        V_x_class = pickle.load(f)

    t0 = time.time()

    summary_dict = walker(config.steps, config.x0, config.temp,
        config.metad, config.w, config.delta, config.hfreq)
    
    tplus = time.time()
    
    # Need to define generic domain because of new class notation
    x = np.arange(-np.pi, np.pi, 0.01)
    sim_time = np.linspace(0, config.steps+1, config.steps+1) * dt #ns
    
    # fes(V_x_class.potential(x))
    # reweight(bias)
    # rads_time(q, sim_time)
    # animate_md(V, bias, q)
    
    plt.show()

    print(f" Number of steps: {config.steps}")
    print(f" Initial x coord: {config.x0:.2f} radians")
    print(f" Temperature: {config.temp:.2f}")
    print(f" Timestep: {dt:.2e}ns")

