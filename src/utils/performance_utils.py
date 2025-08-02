def integrator_performance(t_start, t_end, steps):
    delta_t = t_end - t_start
    ns_day = (steps / delta_t) * 0.02 * 86400 # nanoseconds per day

    performance_summary = {
        'sim_time': delta_t,
        'ns/day': ns_day, 
    }

    return performance_summary
