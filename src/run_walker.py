from walker import walker
from plots import rads_time, reweight, animate_md
import matplotlib.pyplot as plt

import numpy as np
import config
import json


# This intermediate script is meant to avoid circular imports of walker.py

if __name__ == '__main__':
    summary_dict = walker(config.steps, config.x0, config.temp, 
        config.metad, config.w, config.delta, config.hfreq)
    
    sim_time = np.linspace(0, config.steps+1, config.steps+1) * 0.02 #ns

    rads_time(summary_dict['q'], sim_time, save_path='static/images/rads_time.png')
    reweight(summary_dict['bias'], save_path='static/images/reweight_fes.png')
    animate_md(summary_dict['V'], summary_dict['bias'], summary_dict['q'])

    # plt.show()
    print(json.dumps(summary_dict))
