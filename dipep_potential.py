import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



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
    return x, y

phi, energy = read_fes('MD/fes-std.dat')


#####---Evaluate the best fitting for polynomial function---#####
#I want to describe the standard FES as a polynomial to describe the 'known' potential V(x)

#loop through to test a variety of degrees 
def poly_fitting(x, y, degree):
    coeffs = np.polyfit(x, y, degree)
    p = np.poly1d(coeffs)
    y_pred = p(x)
    mse = np.mean((y-y_pred)**2)
    return mse, p

degrees = range(1, 20)
errors = []
polynomials = []

for degree in degrees:
    mse, polynomial = poly_fitting(phi, energy, degree)
    errors.append(mse)
    polynomials.append(polynomial)

min_error_degree = degrees[np.argmin(errors)] #best degree, should be integer

coeffs = np.polyfit(phi, energy, min_error_degree) #best fitting

V_x = np.poly1d(coeffs) #a priori potential 



#plot original data and the best polynomial fitting

if __name__ == '__main__':  
    plt.scatter(phi, energy, label='Free-energy surface of Alanine Dipeptide dihedral')
    plt.plot(phi, polynomials[min_error_degree - 1](phi), label='best fit', color='red')
    plt.legend()
    plt.show()