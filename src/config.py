# Comprehensive configuration file for VisMetaDynamics
# Handles both metadynamics and umbrella sampling simulations

# This is an improvement over two separate config files that were written/overwritten depending on enhanced sampling protocol

import numpy as np

# =============================================================================
# SIMULATION PARAMETERS (Common to both metadynamics and umbrella sampling)
# =============================================================================

# Basic simulation parameters
steps = 145870
temp = 310
x0 = 0.01

# =============================================================================
# METADYNAMICS PARAMETERS
# =============================================================================

# Metadynamics simulation type
metad = True

# Metadynamics-specific parameters
w = 0.8
delta = 0.15
hfreq = 150

# =============================================================================
# UMBRELLA SAMPLING PARAMETERS
# =============================================================================

# Umbrella sampling simulation type
us = False

# Umbrella sampling-specific parameters
kappa = 100
bins = 10

# Window configuration (generated automatically for umbrella sampling)
# These are set when umbrella sampling is enabled
windows = np.array([-3.14159265, -2.6927937 , -2.24399475, -1.7951958 , -1.34639685,
                    -0.8975979 , -0.44879895,  0.        ,  0.44879895,  0.8975979 ,
                     1.34639685,  1.7951958 ,  2.24399475,  2.6927937 ,  3.14159265])
centers = np.array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14])







