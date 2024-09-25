metad = False

MD_parameters = {
    'steps': int(),
    'timestep': float(), # ns 
    'temp': float(), # Kelvin
    'x0': float(), # radians
    'mratio': int(),
    't': 0, #might not be needed
    'm': 1 # point mass, unlikely to be changed
}

metadynamics_parameters ={
    'w': float(), #height (kcal)
    'delta': float(), # width (rad)
    'hfreq': float() # how often to add hills
}
