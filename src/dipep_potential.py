import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pickle   
#####---Sine/cosine fit because F(-pi) == F(pi) in a truly periodic system---#####

#generic function to read simple files
def read_fes(file):
    infile = open(file, 'r')
    infile_read = infile.readlines()[0:]
    x = []
    y = []
    for line in infile_read:
        columns = line.split()
        if not line.startswith(('#', '!', ';')): #exclude all sorts of comments
            x.append(float(columns[0]))
            y.append(float(columns[1]))
    infile.close()
    return np.array(x), np.array(y)

# we need two functions because there are two parameters to tune for:
#   - number of sine/cosine terms to add
#   - the coefficients ouside each sine/cosine term

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

phi, energy = read_fes('fes-std.dat')

terms = range(1, 10)
errors = []
fitted_params = []

for num_terms in terms:
    params = fit_sine_cosine(phi, energy, num_terms)
    y_pred = sine_cosine_fit(phi, *params)
    mse = np.mean((energy - y_pred) ** 2)
    errors.append(mse)
    fitted_params.append(params)

min_error_terms = terms[np.argmin(errors)]  # Best number of terms

# Get the best fitting coefficients
best_params = fitted_params[np.argmin(errors)]


# Define the best-fitting potential function V(x)

if __name__ == '__main__':
    from V_x_functions import V_x   

    ###---Save computation time by accessing and serializing your own potential---###
    ###---re-run this script to load new potential, but check V_x_functions.py---###

    v_x_instance = V_x(best_params)
    with open ("V_x_functions.pkl", 'wb') as f:
        pickle.dump(v_x_instance, f)

    x = np.arange(-np.pi, np.pi, 0.01)
# Plot original data and the best sine-cosine fitting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set(xlim=[-np.pi, np.pi], ylim=[-100, 100])

    plt.title('Alanine Dipeptide Free Energy Surface of Φ Dihedral Angle', fontsize=16)
    plt.ylabel('Energy (kcal)', fontsize=15)
    plt.xlabel('Φ (Degrees)', fontsize=15)

    ax.tick_params(axis='both', which='major', labelsize=14, width=1, length=4)
    xticks_radians = np.linspace(-np.pi, np.pi, 5) 
    ax.set_xticks(xticks_radians)
    ax.set_xticklabels(np.degrees(xticks_radians).astype(int)) 
    ax.minorticks_on()

    plt.scatter(phi, energy, label='Metadynamics FES',
    marker='s', s=16, color='gray', alpha=0.8)

    plt.plot(x, v_x_instance.potential(x), label='Best sine-cosine fit', color='dodgerblue')
    plt.plot(x, v_x_instance.force(x), label='F(x)', color='red')
    
    fig.tight_layout()
    plt.legend()
    fig.savefig('underlying_fes.png', dpi=200)
    plt.show()


#####---Evaluate the best fitting for polynomial function (DEPRECATED)---#####
# This method is problematic because F(pi) != F(-pi) and for this to be truly periodic,
# we need to make sure they are the same. 
# I want to describe the standard FES as a polynomial to describe the 'known' potential V(x)

#loop through to test a variety of degrees 
# def poly_fitting(x, y, degree):
#     coeffs = np.polyfit(x, y, degree)
#     p = np.poly1d(coeffs)
#     y_pred = p(x)
#     mse = np.mean((y-y_pred)**2)
#     return mse, p

# degrees = range(1, 20)
# errors = []
# polynomials = []

# for degree in degrees:
#     mse, polynomial = poly_fitting(phi, energy, degree)
#     errors.append(mse)
#     polynomials.append(polynomial)

# min_error_degree = degrees[np.argmin(errors)] #best degree, should be integer

# coeffs = np.polyfit(phi, energy, min_error_degree) #best fitting

# V_x = np.poly1d(coeffs) #a priori potential 

