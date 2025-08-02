"""
Utility functions for VisMetaDynamics
Organized by functionality for clean imports and maintainability
"""

# Import all utility functions for easy access
from .logging_utils import (
    setup_logger, 
    setup_umbrella_logging,
    log_simulation_header, 
    log_umbrella_ensemble_header,
    log_window_progress,
    log_ensemble_summary,
    log_metadynamics_event,
    log_umbrella_sampling_metrics,
    log_simulation_summary
)
from .file_utils import load_pickle_file, update_progress
from .performance_utils import integrator_performance 
from .config_utils import (get_simulation_type, 
    get_center_for_simulation, 
    print_config_summary,
    set_metadynamics_preset,
    set_umbrella_sampling_preset,
    set_standard_md_preset,
    validate_command_line_args, 
    validate_config)

# Define what gets imported with "from utils import *"
__all__ = [
    # Logging utilities
    'setup_logger',
    'setup_umbrella_logging',
    'log_simulation_header',
    'log_umbrella_ensemble_header', 
    'log_window_progress',
    'log_ensemble_summary',
    'log_metadynamics_event',
    'log_umbrella_sampling_metrics',
    'log_simulation_summary',
    
    # File utilities
    'load_pickle_file',
    'update_progress',
    
    # Validation utilities
    'validate_command_line_args',
    'validate_config',
    
    # Performance utilities
    'integrator_performance',
    
    # Configuration utilities
    'get_simulation_type',
    'get_center_for_simulation',
    'print_config_summary'
]

# You can also add package-level documentation
__version__ = "1.0.0"
__author__ = "Your Name"
