import logging
import os
import numpy as np


def setup_logger(name, log_file, log_level, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def setup_umbrella_logging(logger):
    """Set up logging for umbrella sampling simulations"""
    logger.info("=" * 80)
    logger.info("UMBRELLA SAMPLING SIMULATION SETUP")
    logger.info("=" * 80)

def log_umbrella_ensemble_header(logger, kappa, bins, windows, centers):
    """Log umbrella sampling ensemble initialization"""
    logger.info("UMBRELLA SAMPLING ENSEMBLE PARAMETERS:")
    logger.info(f"Force constant (kappa): {kappa} kJ/mol/rad²")
    logger.info(f"Number of windows: {bins}")
    logger.info(f"Window centers: {windows}")
    logger.info(f"Window indices: {centers}")
    logger.info(f"Total ensemble simulations: {len(centers)}")
    logger.info("=" * 80)

def log_window_progress(logger, window_idx, total_windows, center, window_data):
    """Log progress for individual window simulations"""
    logger.info(f"WINDOW {window_idx}/{total_windows}: Center = {center:.6f} radians")
    logger.info(f"  Simulation time: {window_data['sim_time']:.2f} seconds")
    logger.info(f"  Performance: {window_data['ns/day']:.1f} ns/day")
    logger.info(f"  Final position: {window_data['q'][-1]:.6f} radians")
    logger.info(f"  Final energy: {window_data['E'][-1]:.4f} kJ/mol")

def log_ensemble_summary(logger, simulation_ensemble, total_time):
    """Log final ensemble simulation summary"""
    logger.info("=" * 80)
    logger.info("UMBRELLA SAMPLING ENSEMBLE SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total ensemble time: {total_time:.2f} seconds")
    logger.info(f"Number of windows completed: {len(simulation_ensemble)}")
    
    # Calculate ensemble statistics
    final_positions = [data['q'][-1] for data in simulation_ensemble.values()]
    final_energies = [data['E'][-1] for data in simulation_ensemble.values()]
    
    logger.info(f"Position range: [{min(final_positions):.6f}, {max(final_positions):.6f}] radians")
    logger.info(f"Energy range: [{min(final_energies):.4f}, {max(final_energies):.4f}] kJ/mol")
    logger.info(f"Average final energy: {np.mean(final_energies):.4f} kJ/mol")
    logger.info("=" * 80)

def log_simulation_header(logger, steps, x0, T, metad, w, delta, hfreq, us, kappa, center):
    """Log simulation initialization parameters like a real MD engine"""
    logger.info("=" * 80)
    logger.info("MOLECULAR DYNAMICS SIMULATION INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"Simulation type: {'Metadynamics' if metad else 'Umbrella Sampling' if us else 'Standard MD'}")
    logger.info(f"Total simulation steps: {steps}")
    #logger.info(f"Time step (dt): {dt} ps")
    #logger.info(f"Total simulation time: {steps * dt:.3f} ps")
    logger.info(f"Temperature: {T} K")
    logger.info(f"Initial position (x0): {x0:.6f} radians")
    
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

def log_metadynamics_event(logger, step, q, s, bias_contribution):
    """Log metadynamics hill deposition events"""
    logger.info(f"METADYNAMICS: Hill deposited at step {step}")
    logger.info(f"  Current position: {q:.6f} radians")
    logger.info(f"  Total hills deposited: {len(s)}")
    logger.info(f"  Bias contribution: {bias_contribution:.4f} kJ/mol")

def log_umbrella_sampling_metrics(logger, step, q, center, kappa, force):
    """Log umbrella sampling specific metrics"""
    if step % 100 == 0:  # Log every 100 steps
        restraint_energy = 0.5 * kappa * (q - center)**2
        logger.info(f"UMBRELLA SAMPLING: Step {step}")
        logger.info(f"  Position: {q:.6f} radians")
        logger.info(f"  Restraint center: {center:.6f} radians")
        logger.info(f"  Restraint force: {force:.4f} kJ/mol/rad")
        logger.info(f"  Restraint energy: {restraint_energy:.4f} kJ/mol")

def log_simulation_summary(logger, simulation_data, t_start, t_end):
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



