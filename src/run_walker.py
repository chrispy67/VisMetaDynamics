from walker import walker
from plots import rads_time, neg_bias, animate_md, fes, histogram
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
import config
import json


# This intermediate script is meant to avoid circular imports of walker.py and is executed EVERY TIME the Begin Simulation button is pressed

if __name__ == '__main__':
    # Time consuming step here
    summary_dict = walker(config.steps, config.x0, config.temp, 
        config.metad, config.w, config.delta, config.hfreq)
    
    sim_time = np.linspace(0, config.steps+1, config.steps+1) * 0.02 #ns

    # These plots are crucial to the output on the Flask page
    rads_time(summary_dict['q'], sim_time, save_path='static/images/rads_time.png')
    neg_bias(summary_dict['bias'], summary_dict['q'], save_path='static/images/reweight_fes.png')
    fes(save_path='static/images/underlying_fes.png')
    animate_md(summary_dict['V'], summary_dict['bias'], summary_dict['q'], save_path='static/images/MD_simulation.gif')

    # histogram(summary_dict['q'], summary_dict['bias']) # FOR DEBUGGING PURPOSES!!
    plt.show()
    
# Primary output to flask page
    print(json.dumps(summary_dict))
    # dict_keys(['bias', 'q', 'V', 'E', 'sim_time', 'ns/day'])

    # plt.show()