import os
import pickle
from pathlib import Path
import json

# I was sick of having the same if/try/except block in every script that needed to load a pickle file. 
# Will place future helpful functions here, may as well even move existing functions here if I see fit. 




def load_pickle_file(filename, search_paths=None):

    if search_paths is None:
        # Default search paths: current directory, src/, and parent directory
        search_paths = [
            '.', 
            'src',  
            '..',  
            '../src' 
        ]
    
    for path in search_paths:
        file_path = Path(path) / filename
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError) as e:
                print(f"Warning: Could not load pickle file from {file_path}: {e}")
                continue
    
    # File not found 
    raise FileNotFoundError(f"Could not find {filename} in any of the search paths: {search_paths}")

 # overwrites progress bar value as .json as function of mratio
def update_progress(value):
    try:
        with open('static/.progress.json', 'w') as f:
            json.dump({"value": value}, f)
    except (IOError, OSError) as e:
        # Silently handle file writing errors to avoid crashing the simulation
        pass