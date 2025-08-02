

def print_config_summary():
    import config
    print("=" * 60)
    print("VISMETADYNAMICS CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Simulation type: {get_simulation_type()}")
    print(f"Steps: {config.steps}")
    print(f"Temperature: {config.temp} K")
    print(f"Initial position: {config.x0:.6f} radians")
    if metad:
        print("\nMETADYNAMICS PARAMETERS:")
        print(f"  Gaussian height (w): {config.w} kJ/mol")
        print(f"  Gaussian width (delta): {config.delta} radians")
        print(f"  Hill frequency: {config.hfreq} steps")
    if us:
        print("\nUMBRELLA SAMPLING PARAMETERS:")
        print(f"  Force constant (kappa): {config.kappa} kJ/mol/rad²")
        print(f"  Number of windows: {config.bins}")
        print(f"  Window centers: {len(config.windows)} windows")
    print("=" * 60)


# =============================================================================
# CONFIGURATION PRESETS
# =============================================================================

def set_metadynamics_preset():
    """Set configuration for metadynamics simulation"""
    global metad, us, w, delta, hfreq, kappa, bins
    metad = True
    us = False
    w = 1.2
    delta = 0.01
    hfreq = 50
    kappa = 100
    bins = 10

def set_umbrella_sampling_preset():
    """Set configuration for umbrella sampling simulation"""
    global metad, us, w, delta, hfreq, kappa, bins
    metad = False
    us = True
    w = 1.2
    delta = 0.01
    hfreq = 50
    kappa = 100
    bins = 10

def set_standard_md_preset():
    """Set configuration for standard molecular dynamics simulation"""
    global metad, us, w, delta, hfreq, kappa, bins
    metad = False
    us = False
    w = 0.0
    delta = 0.0
    hfreq = 0.0
    kappa = 0.0
    bins = 0

def validate_command_line_args(args):
    import numpy as np
    errors = []
    try:
        if int(args.steps) <= 0:
            errors.append("Simulation steps must be a positive integer.")
        if int(args.temp) <= 0:
            errors.append("Simulation temperature must be positive integer. Reminder, this is in Kelvin!")
        if float(args.x0) < -np.pi or float(args.x0) > np.pi:
            errors.append("The collective variable in this tutorial is a dihedral angle it is periodic on the domain [-π, π]. Enter whole numbers between -3 and 3.")
        if not args.metad:
            args.w = '0.0'
            args.delta = '0.0'
            args.hfreq = '0.0'
        if float(args.w) < 0:
            errors.append("Gaussian weight must be a positive floating point number, preferrably between 0.1 and 5")
        if float(args.delta) < 0:
            errors.append("Gaussian width must be a positive floating point number, preferrably between 0.01 and 1")
        if float(args.hfreq) < 0:
            errors.append("Frequency of gaussian deposition must be a positive integer, preferrably between 10 and 500")
        if float(args.kappa) < 0:
            errors.append("Force constant cannot be negative")
    except (ValueError, TypeError) as e:
        errors.append(f"Type conversion error: {str(e)}")
    return errors

def validate_config():
    import config
    import numpy as np

    errors = []
    if config.steps <= 0:
        errors.append("Simulation steps must be a positive integer")
    if config.temp <= 0:
        errors.append("Temperature must be positive")
    if config.x0 < -np.pi or config.x0 > np.pi:
        errors.append("Initial position must be within [-π, π] radians")
    if metad:
        if config.w < 0:
            errors.append("Gaussian height must be positive")
        if config.delta < 0:
            errors.append("Gaussian width must be positive")
        if config.hfreq < 0:
            errors.append("Hill frequency must be positive")
    if config.us:
        if config.kappa < 0:
            errors.append("Force constant must be positive")
        if config.bins <= 0:
            errors.append("Number of bins must be positive")
    if config.metad and config.us:
        errors.append("Cannot enable both metadynamics and umbrella sampling simultaneously")
    if not config.metad and not config.us:
        errors.append("Must enable either metadynamics or umbrella sampling")
    return errors

def get_simulation_type():
    if metad:
        return "metadynamics"
    elif us:
        return "umbrella_sampling"
    else:
        return "standard_md"

def get_center_for_simulation():
    import config
    if us:
        if hasattr(config.centers, '__len__') and len(config.centers) > 0:
            return config.windows[config.centers[0]]
        else:
            return 0.0
    else:
        return 0.0