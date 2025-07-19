import numpy as np
import argparse
import config as config
import time
import matplotlib.pyplot as plt
import json
import logging
import os

## This script should be run via commandline for debugging purposes. 
## This avoids launching the flask window and allows for more flexible debugging. 
## the --DEMO flag can be used to run a simulation with ideal parameters.

# Set up logging
log_path = os.path.join(os.path.dirname(__file__), '../log/walker.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Define parameters that aren't set by user
mratio = 10 # sets log ratio for site progress bar 

dt = 0.02  # Time step is FIXED now
t = 0  # Time
m = 1  # Mass

def log_simulation_header(steps, x0, T, metad, w, delta, hfreq, us, kappa, center):
    """Log simulation initialization parameters like a real MD engine"""
    logger.info("=" * 80)
    logger.info("MOLECULAR DYNAMICS SIMULATION INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"Simulation type: {'Metadynamics' if metad else 'Umbrella Sampling' if us else 'Standard MD'}")
    logger.info(f"Total simulation steps: {steps}")
    logger.info(f"Time step (dt): {dt} ps")
    logger.info(f"Total simulation time: {steps * dt:.3f} ps")
    logger.info(f"Temperature: {T} K")
    logger.info(f"Initial position (x0): {x0:.6f} radians")
    logger.info(f"Mass: {m} amu")
    
    if metad:
        logger.info("METADYNAMICS PARAMETERS:")
        logger.info(f"  Gaussian height (w): {w} kJ/mol")
        logger.info(f"  Gaussian width (delta): {delta} radians")
        logger.info(f"  Hill deposition frequency: {hfreq} steps")
        logger.info(f"  Expected number of hills: {steps // hfreq}")
    
    if us:
        logger.info("UMBRELLA SAMPLING PARAMETERS:")
        logger.info(f"  Force constant (kappa): {kappa} kJ/mol/rad²")
        logger.info(f"  Restraint center: {center:.6f} radians")

def log_metadynamics_event(step, q, s, bias_contribution):
    """Log metadynamics hill deposition events"""
    logger.info(f"METADYNAMICS: Hill deposited at step {step}")
    logger.info(f"  Current position: {q:.6f} radians")
    logger.info(f"  Total hills deposited: {len(s)}")
    logger.info(f"  Bias contribution: {bias_contribution:.4f} kJ/mol")

def log_umbrella_sampling_metrics(step, q, center, kappa, force):
    """Log umbrella sampling specific metrics"""
    if step % 100 == 0:  # Log every 100 steps
        restraint_energy = 0.5 * kappa * (q - center)**2
        logger.info(f"UMBRELLA SAMPLING: Step {step}")
        logger.info(f"  Position: {q:.6f} radians")
        logger.info(f"  Restraint center: {center:.6f} radians")
        logger.info(f"  Restraint force: {force:.4f} kJ/mol/rad")
        logger.info(f"  Restraint energy: {restraint_energy:.4f} kJ/mol")

def log_simulation_summary(simulation_data, t_start, t_end):
    """Log final simulation summary"""
    logger.info("=" * 80)
    logger.info("SIMULATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total simulation time: {t_end - t_start:.2f} seconds")
    logger.info(f"Performance: {simulation_data['ns/day']:.1f} ns/day")
    
    if simulation_data['bias']:
        max_bias = max(simulation_data['bias'])
        logger.info(f"Maximum bias potential: {max_bias:.4f} kJ/mol")
    
    logger.info("=" * 80)


def CLI():
    ###--Parse optional commandline arguments for debugging purposes or alternate usecase--###
    parser = argparse.ArgumentParser(description="A command line interface for producing the same figures and data found on the Flask site. Check default values!!")

    ## Simulation Parameters
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
    
    ## Metadyanmics Parameters  
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

    ## METAD DEMO, HIDDEN FROM USER
    parser.add_argument('--DEMO', action='store_true',help=argparse.SUPPRESS)

    ## Everything below is for Umbrella Sampling
    parser.add_argument('-us', '--umbrella',
        action='store_true',
        dest='us',  # This maps the --umbrella flag to the 'us' attribute
        help = 'Umbrella sampling on/off')
    
    parser.add_argument('--kappa', '-k',
        type = str,
        default = '100', 
        help = 'Force constant of harmonic restraint (kJ/mol)')
    
    parser.add_argument('--bins', '--windows',
        type = int,
        default = '10',
        help = 'Number of evennly spaced windows (i.e. independent simulations) to run')

    args = parser.parse_args()

    ## Handle optional demo flag
    if getattr(args, 'DEMO', False):
        args.steps = 105000
        args.temp = 310
        args.x0 = 0.0
        args.metad = True,
        args.w = 1.2
        args.delta = 0.1
        args.hfreq = 100
        args.us = False
        args.kappa = 100 # args.us is False, parameter choice is not used
        args.bins = 10 # args.us is False, parameter choice is not used


    # Error handling for user responses using centralized validation
    validation_errors = config.validate_command_line_args(args)
    if validation_errors:
        for error in validation_errors:
            print(error)
        exit(1)

    # Build a dictionary of all the arguments that have been PARSED or given default values
    args_dict = vars(args)

    # Ensure 'us' is always present and is a boolean
    if 'us' not in args_dict:
        args_dict['us'] = False
    else:
        args_dict['us'] = bool(args_dict['us'])

    # Convert numeric values to correct types
    for key in ['steps', 'temp', 'x0', 'w', 'delta', 'hfreq', 'kappa', 'bins']:
        if key in args_dict:
            if key in ['steps', 'hfreq', 'bins']:
                args_dict[key] = int(float(args_dict[key]))
            else:
                args_dict[key] = float(args_dict[key])

    # Create a complete configuration dictionary that can be used directly
    # This avoids the need to modify config.py
    config_dict = {
        'steps': args_dict['steps'],
        'temp': args_dict['temp'], 
        'x0': args_dict['x0'],
        'metad': args_dict['metad'],
        'w': args_dict['w'],
        'delta': args_dict['delta'],
        'hfreq': args_dict['hfreq'],
        'us': args_dict['us'],
        'kappa': args_dict['kappa'],
        'bins': args_dict['bins']
    }
    
    print("Configuration loaded from command line arguments (no file modification)")
    print(f"Simulation parameters: {config_dict}")
        
    return config_dict

def integrator_performance(t_start, t_end, steps):
    delta_t = t_end - t_start
    ns_day = (steps / delta_t) * dt * 86400 # nanoseconds per day

    performance_summary = {
        'sim_time': delta_t,
        'ns/day': ns_day, 
    }

    return performance_summary

# overwrites progress bar value as .json as function of mratio
def update_progress(value):
    try:
        with open('static/.progress.json', 'w') as f:
            json.dump({"value": value}, f)
    except (IOError, OSError) as e:
        # Silently handle file writing errors to avoid crashing the simulation
        pass

# Primary MD Engine
# All functions that are necessary to these calculations are INSIDE THIS FUNCTION
def walker(steps, x0, T, # simulation parameters
        metad, w, delta, hfreq, # metadynamics parameters
        us, kappa, center): # umbrella sampling parameters
    
    t0 = time.time()
    last_log_time = t0

    # Log simulation initialization
    log_simulation_header(steps, x0, T, metad, w, delta, hfreq, us, kappa, center)

    # Load in potential depending on where script is executed
    # This is the underlying phi sine/cosine function and is ALWAYS loaded
    from utils import load_pickle_file
    V_x_class = load_pickle_file('V_x_functions.pkl')


    # Subfunction to calculate PE and force
    def force(r, s, w, delta, center_val):
        r = pbc(r)
        V = V_x_class.potential(r)
        F = V_x_class.force(r)
        Fpot = -F

        Fbias = 0 # Must define Fbias here since it is being added to by Fpot
        if metad:
            Fbias += np.sum(w * (r - s) / delta**2 * np.exp(-(r - s)**2 / (2 * delta**2)))
        if us:
            Fbias += - kappa * (r - center_val)
        return V, Fpot + Fbias, Fbias

    def pbc(r, bc=np.pi):
        return (((r + bc) % (2 * bc)) - bc) 

    # Metadynamics functions and equations
    gamma = 5.0 #
    beta = 1 / T / 1.987e-3  # assuming V is in kcal/mol ### UNIT CHECK
    c1 = np.exp(-gamma * dt / 2)
    c2 = np.sqrt((1 - c1**2) * m / beta)

    
    # Empty arrays to store information and underlying potential
    xlong = np.linspace(-np.pi, np.pi, 100) # This is the axis in which bias is stored. ADJUST FOR DIFFERENT RESOLUTION 
    q = np.zeros(steps + 1) # Making room for final radian
    E = np.zeros(steps + 1) # Making room for final energy
    V = np.zeros(steps + 1) # Making room for final potential
    bias = np.zeros((len(xlong)), dtype=float) # this array does NOT need to change size; bias[-1] = is just the last entry
    us_force = np.zeros(steps + 1) # Only populated with values if US is happening

    # Initial configurations 
    q[0] = x0
    v0 = np.random.rand() - 0.5 #random initial potential
    p = v0 * m
    s = [0]
    v, f, _ = force(q[0], 0, w, delta, center)  # Pass center as parameter
    E[0] = 0.5 * p**2 + v

    for i in range(steps):
        # Check if we should deposit a hill on the FES
        if metad:
            s = np.append(s, q[i]) if i % hfreq == 0 else s # append a sigma as fxn of hfreq s[i % hfreq]

    #####---Langevian integrator (https://doi.org/10.1103/PhysRevE.75.056707)---#####
        v, f, fbias = force(pbc(q[i]), s, w, delta, center)  # Pass center as parameter
        R1 = np.random.rand() - 0.5
        R2 = np.random.rand() - 0.5

        pplus = c1 * p + c2 * R1 # eq 12a from Bussi and Parrinello

    #####---WRAPPING NEW POSITION IN PBC FUNCTIONS---#####
        q[i + 1] += pbc(q[i] + (pplus / m) * dt + f / m * (dt**2 / 2)) # eq 12b w/ PBC effect
        
        # Do I need to store this force for US?
        v2, f2, _ = force(q[i + 1], s, w, delta, center)  # Pass center as parameter
        
        pminus = pplus + (f / 2 + f2 / 2) * dt # prev momentum
        p = c1 * pminus + c2 * R2 # eq12a, but calculating current step's momentum 

        E[i + 1] = 0.5 * p**2 + v2 # Updated energy, classic Newtonian eq
        
        # Log umbrella sampling metrics
        if us:
            log_umbrella_sampling_metrics(i, q[i], center, kappa, fbias)


        if metad:
            if i % hfreq == 0: 
                if len(s) > 1: 
                    # Log metadynamics hill deposition
                    bias_contribution = np.sum(w * np.exp(-(q[i + 1] - np.array(s))**2 / (2 * delta**2)))
                    log_metadynamics_event(i, q[i], s, bias_contribution)

                    for k in range(len(xlong)):

                        rad_k = xlong[k] # where on the x-axis we are biasing

                        # Calculate bias contribution for this bin
                        bias_k = w * np.exp(-(rad_k - np.array(s)) ** 2 / (2 * delta**2))
                        total_bias = np.sum(bias_k)
                        
                        # Always add to current bin
                        bias[k] += total_bias
                        
                        # Handle periodic boundary conditions properly
                        # For bins near π, also add to corresponding bin near -π
                        if rad_k > np.pi - 3 * delta:  # Near π boundary
                            # Find corresponding bin near -π
                            pbc_rad = rad_k - 2 * np.pi
                            pbc_k = int((pbc_rad - xlong[0]) / (xlong[1] - xlong[0]))
                            if 0 <= pbc_k < len(xlong):
                                bias[pbc_k] += total_bias
                        
                        # For bins near -π, also add to corresponding bin near π  
                        if rad_k < -np.pi + 3 * delta:  # Near -π boundary
                            # Find corresponding bin near π
                            pbc_rad = rad_k + 2 * np.pi
                            pbc_k = int((pbc_rad - xlong[0]) / (xlong[1] - xlong[0]))
                            if 0 <= pbc_k < len(xlong):
                                bias[pbc_k] += total_bias


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
    PERFORMANCE_SUMMARY = integrator_performance(t0, tplus, steps)

    # A dict{} is a nice way to store the simulation data
    SIMULATION_DATA = {
        'bias': bias.tolist(),
        'q': q.tolist(),
        'V': V.tolist(),
        'E': E.tolist(),
        'us_force': us_force.tolist()
    }

    # Now that I am moving this data as a JSON 
    SIMULATION_DATA.update(PERFORMANCE_SUMMARY)
    
    # Log final simulation summary
    log_simulation_summary(SIMULATION_DATA, t0, tplus)
    
    return SIMULATION_DATA


if __name__ == '__main__':
    import time
    from plots import animate_metad, fes, neg_bias, rads_time, histogram
    # If you want to pickle a class, the same script MUST know the format of the class
    from V_x_functions import V_x   
 
    from utils import load_pickle_file
    V_x_class = load_pickle_file("V_x_functions.pkl")


    # Where command line arguments are handled if run as script
    # CLI() returns a complete configuration dictionary
    config_dict = CLI()


    ###--Beginning the main Metadynamics logic and calling integrator--###
    t0 = time.time()
    
    logger.info("Starting molecular dynamics simulation...")
    logger.info(f"Command line arguments: {config_dict}")

    # Handle both metadynamics (scalar) and umbrella sampling (single window) cases
    if config_dict['us']:  # Use config_dict instead of config.us
        # For umbrella sampling, generate windows and centers if not present
        import numpy as np
        bins = config_dict.get('bins', 15)
        windows = np.linspace(-np.pi, np.pi, bins)
        centers = np.arange(bins, dtype=int)
        if len(centers) > 0:
            center = windows[centers[0]]  # Use the first window center
            logger.info(f"Running single umbrella sampling window at center: {center}")
        else:
            # Fallback if centers array is not available
            center = 0.0
            logger.warning("No centers found, using default center = 0.0")
    else:
        # For metadynamics, use a default center value (not used when us=False)
        center = 0.0  # Default value for metadynamics
        logger.info(f"Metadynamics simulation: center = {center} (this value is NOT used in metadynamics)")
        
    logger.info(f"Final center value passed to walker: {center}")
    logger.info(f"Simulation type: metad={config_dict['metad']}, us={config_dict['us']}")
    
    summary_dict = walker(config_dict['steps'], config_dict['x0'], config_dict['temp'],
        config_dict['metad'], config_dict['w'], config_dict['delta'], config_dict['hfreq'],
        config_dict['us'], config_dict['kappa'], center)  # Use config_dict parameters
    
    tplus = time.time()
    
    x = np.linspace(-np.pi, np.pi, 100)
    sim_time = np.linspace(0, config_dict['steps']+1, config_dict['steps']+1) * dt #ns
    
    # Generates plots that populate Flask page and appear in matplitlib window (CLI)
    fes()
    neg_bias(summary_dict['bias'], summary_dict['q'])
    rads_time(summary_dict['q'], sim_time)
    animate_metad(summary_dict['V'][:-1], summary_dict['q'][:-1])

    # Basic printout for performance
    logger.info("=" * 80)
    logger.info("SIMULATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"Simulation time: {summary_dict['sim_time']} seconds")
    logger.info(f"Simulation performance: {summary_dict['ns/day']} ns/day")
    logger.info(f"Simulation parameters: {config_dict}")
    logger.info("=" * 80)
    

    # One-liner to differentiate user inputs from simulation outputs
    # Parameters that produced figures are printed to Flask page (thanks Gareth Tribello)
    summary_dict.update({f"_{key}": value for key, value in config_dict.items()})

    print(summary_dict['bias'])

    bias_array = np.array(summary_dict['bias'])
    x = np.linspace(0, len(bias_array), len(bias_array))
    plt.plot(x, bias_array)
    plt.title('BIAS ARRAY AS FXN OF BIN NUMBER')
    plt.xlabel('BIN NUMBER')
    plt.ylabel('BIAS')
    plt.xlim(0, 100)
    plt.show()



    # UPDATED WITH US INTEGRATION
    #dict_keys(['bias', 'q', 'V', 'E', 'us_force', 'sim_time', 'ns/day', 
    # '_steps', '_temp', '_x0', '_metad', '_w', 
    # '_delta', '_hfreq', '_us', '_kappa', '_bins'])

    plt.show()  