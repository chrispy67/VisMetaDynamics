import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# These functions are a bit redundant, but are a consequence of having a class in a  
#   central location to be loaded by many scripts. 
# 
# MAKE SURE TO CHECK dipep_potential.py for these SAME functions.  

def sine_cosine_fit(x, *coeffs):
    result = np.zeros_like(x)
    n = len(coeffs) // 2  # Number of sine-cosine pairs
    for i in range(n):
        result += coeffs[2*i] * np.sin((i+1) * x) + coeffs[2*i+1] * np.cos((i+1) * x)
    return result

def fit_sine_cosine(x, y, num_terms):
    # Initial guess has 2 * num_terms coefficients (sine and cosine terms)
    initial_guess = np.ones(2 * num_terms)
    params, _ = curve_fit(sine_cosine_fit, x, y, p0=initial_guess)
    return params

def sine_cosine_derivative(x, *coeffs):
    result = np.zeros_like(x)
    n = len(coeffs) // 2
    for i in range(n):
        result += (i+1) * coeffs[2*i] * np.cos((i+1) * x)  # Derivative of sine
        result -= (i+1) * coeffs[2*i+1] * np.sin((i+1) * x)  # Derivative of cosine
    return result

# This is what is ACTUALLY important, the class being accessible by every script,
#   trying to get rid of circular imports
class V_x:
    def __init__(self, params):
        self.params = params

    def potential(self, phi):
        # min_to_zero = np.abs(np.min(sine_cosine_fit(phi, *self.params)))
        return sine_cosine_fit(phi, *self.params)

    def force(self, phi):
        # min_to_zero = np.abs(np.min(sine_cosine_fit(phi, *self.params)))
        return sine_cosine_derivative(phi, *self.params) 