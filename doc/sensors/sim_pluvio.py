__author__ = 'oli'

import numpy as np
import matplotlib.pyplot as plt


draw_graphs = False  # True  #
load_calibration =  True # True
save_calibration = False
calibration_file = 'calibration.txt'
fixed_flow = True


def schmitt_trigger(ts, low, high, threshold):
    filtered = []
    fd = []
    is_high = False
    is_low = False
    state = np.NaN
    for i in ts:
        d = 0
        if i < low:
            is_low = True
            state = 0
        elif i > high:
            is_high = True
            state = 1
        if is_low and i > threshold:
            is_low = False
            state = 1
            d = 1
        elif is_high and i < threshold:
            is_high = False
            state = 0
            d = 0
        filtered.append(state)
        fd.append(d)
    return filtered, fd


def comb_to_linapprox(comb):
    sawtooth = np.zeros_like(comb, 'float64')
    slope = np.zeros_like(comb, 'float64')
    i = 0
    start_tooth = i
    while i < len(comb):
        stop_tooth = i
        if comb[i] == 0:
            i += 1
        else:
            sawtooth[start_tooth:stop_tooth+1] = sawtooth[start_tooth:start_tooth+1]*np.ones(stop_tooth - start_tooth + 1) + np.linspace(0.0, 1.0, stop_tooth - start_tooth + 1)
            slope[start_tooth:stop_tooth+1] = 1.0/(stop_tooth - start_tooth + 1)
            start_tooth = i
            i += 1

    return sawtooth, slope

def get_inflow(t, inflow_mean, inflow_variation, inflow_var_period, inflow_var_phase, inflow_random, random=False):
    if random:
        inflow = inflow_mean + inflow_variation*np.sin(2*np.pi*t/inflow_var_period+inflow_var_phase) + np.random.normal(0.0, inflow_random, 1)
    else:
        inflow = inflow_mean + inflow_variation*np.sin(2*np.pi*t/inflow_var_period+inflow_var_phase)
    return inflow


if __name__ == '__main__':
    inflow = []
    estimated_inflow = []
    for tk_inflow_mean in np.arange(2.5, 3.0, 0.5):
        # General constants
        g = 9810  # [mm/s²]
        eps0 = 8.85E-12  # void electric permittivity
        epsr_teflon = 2.1

        # Tank parameters
        tk_overflow_height = 3.1  # height above tube in tank [mm]
        tk_tube_height = 4.05  # height of the tube above the bottom of the tank [mm]
        tk_tube_diameter = 3.5  # hole diameter [mm]
        tk_tank_diameter = 80  # tank diameter [mm]

         # Siphon gauge parameters
        sg_siphon_height = 70.4  # height between bottom and top of siphon [mm]
        sg_tube_diameter = 80.0  # siphon gauge tank diameter [mm]
        sg_siphon_diameter = 6.0  # siphon tube diameter [mm]
        sg_siphon_length = 300.0  # siphon tube length for outflow [mm]
        sg_desiphoning_level = 1.5  # water level at which siphon stops to be active when level drops in the gauge [mm]
        sg_residual_water_height = 39.5  # height of residual water after siphoning [mm]

        # Sensor parameters
        ss_length = 150  # length of cylindrical capacitor [mm]
        ss_always_wet_length = tk_tube_height + sg_residual_water_height  # length of cylindrical capacitor that is always wet (at the base of the upper tank and the gauge below the siphon) [mm]
        ss_inner_radius = 10  # inner radius of the cylinder [mm]
        ss_outer_radius = 10.4  # outer radius of the cylinder [mm]
        ss_resistance = 500000  # R2 [ohm]

        # Data acquisition parameters
        das_period = 2  # sampling period [s]

        # Derived tank parameters
        tk_tank_area = np.pi/4*tk_tank_diameter**2 - np.pi*ss_outer_radius**2  # tank area [mm²]
        tk_hole_area = np.pi/4*tk_tube_diameter**2  # tank area [mm²]
        # Derived siphon gauge parameters
        sg_tube_area = np.pi/4*sg_tube_diameter**2 - np.pi*ss_outer_radius**2  # tank area [mm²]

        # Tank starting state
        tk_water_level = 4.05  # level of water in tank above the hole [mm]
        if fixed_flow:
            tk_inflow_mean = 4.0  # mean volumetric inflow [l/h]
            tk_inflow_variation = 2.0  # amplitude of the inflow variation [l/h]
            tk_inflow_var_period = 1800.0  # period of the inflow variation [s]
            tk_inflow_random = 0.010  # amplitude of random component on inflow [l/h]
            tk_inflow_var_phase = 0.0  # phase of the inflow variation [rad]
        else:
            tk_inflow_variation = 0.0  # amplitude of the inflow variation [l/h]
            tk_inflow_var_period = 1.0  # period of the inflow variation [s]
            tk_inflow_random = 0.0  # amplitude of random component on inflow [l/h]
            tk_inflow_var_phase = 0.0  # phase of the inflow variation [rad]

        tk_outflow = 0.0  # volumetric outflow [l/h]

        # Siphon gauge starting state
        sg_water_level = 1.5  # level of water in the siphon gauge tank above the base of the siphon [mm]
        sg_outflow = 0.0  # volumetric outflow [l/h]
        sg_active = 0  # 1 when siphon is active 0 otherwise

        # Simulation time
        time_start = 0.0  # simulation starting time
        time_end = 36000.0  # simulation ending time
        time_step = .2  # [s]

        # Initialisation
        time = time_start
        tk_inflow = get_inflow(time, tk_inflow_mean, tk_inflow_variation, tk_inflow_var_period, tk_inflow_var_phase, tk_inflow_random, fixed_flow)
        t = [time]
        tk_h = [tk_water_level]
        tk_o = [tk_outflow]
        tk_i = [tk_inflow]
        sg_h = [sg_water_level]
        sg_o = [sg_outflow]
        sg_a = [sg_active]
        sg_total_outflow_volume = 0
        ss_capacity = (ss_always_wet_length + sg_water_level + tk_water_level) * epsr_teflon / 500 * np.pi * eps0 / np.log(ss_outer_radius / ss_inner_radius)
        ss_frequency = 1/(0.693*2*ss_resistance*ss_capacity)
        ss_counter = [ss_frequency*time_step]

        # Theoretical siphoning time
        ts0 = 0.54*(sg_tube_area/100.0)*sg_siphon_length**(4/7)*sg_siphon_height**(3/7)/sg_siphon_diameter**(19/7)
        print('siphoning time without inflow : %4.1f s' % ts0)
        # Theoretical siphoning rate
        sr = sg_tube_area*sg_siphon_height*3.6/1000/ts0
        print('siphoning rate : %4.2f l/h' % sr)
        # Theoretical siphoning time with inflow
        ts = ts0/(1-tk_inflow_mean/sr)
        print('siphoning time with inflow of %4.2f l/h : %4.1f s' % (tk_inflow_mean, ts))
        # sensor low and high frequencies
        ss_min_capacity = ss_always_wet_length * epsr_teflon / 500 * np.pi * eps0 / np.log(ss_outer_radius / ss_inner_radius)
        ss_max_freq = 1/(0.693*2*ss_resistance*ss_min_capacity)
        ss_max_capacity = (ss_always_wet_length + sg_siphon_height + tk_overflow_height) * epsr_teflon / 500 * np.pi * eps0 / np.log(ss_outer_radius / ss_inner_radius)
        ss_min_freq = 1/(0.693*2*ss_resistance*ss_max_capacity)
        print('sensor frequency range [%5.0f Hz - %5.0f Hz]' % (ss_min_freq, ss_max_freq))

        # Simulation
        while time < time_end:
            time += time_step
            t.append(time)
            # tk update
            tk_net_input = time_step*(tk_inflow-tk_outflow)*1000/3.6  # net water input during time_step [mm³]
            tk_water_level += tk_net_input/tk_tank_area
            if tk_water_level > tk_overflow_height:
                tk_water_level = tk_overflow_height
            elif tk_water_level < 0.0:
                tk_water_level = 0.0
            tk_outflow = (2*g*tk_water_level)**(1/2)*tk_hole_area*3.6/1000  # [l/h]
            tk_inflow = get_inflow(time, tk_inflow_mean, tk_inflow_variation, tk_inflow_var_period, tk_inflow_var_phase, tk_inflow_random, fixed_flow)
            tk_h.append(tk_water_level)
            tk_o.append(tk_outflow)
            tk_i.append(tk_inflow)
            # sg update
            sg_net_input = time_step*(tk_outflow-sg_outflow)*1000/3.6  # net water input during time_step [mm³]
            sg_water_level += sg_net_input/sg_tube_area
            if sg_water_level > sg_siphon_height:
                sg_active = 1
            elif sg_water_level <= sg_desiphoning_level:
                sg_active = 0
            if sg_active == 1:
                sg_outflow = np.pi/900*(sg_water_level/(0.000016*sg_siphon_length))**(4/7)*sg_siphon_diameter**(19/7)  # [l/h]
            else:
                sg_outflow = 0.0
            sg_total_outflow_volume += (sg_outflow/3600)*time_step  # [l]
            sg_h.append(sg_water_level)
            sg_o.append(sg_outflow)
            sg_a.append(sg_active)
            # ss update
            ss_counter.append(ss_frequency*time_step)
            ss_capacity = (ss_always_wet_length + sg_water_level + tk_water_level) * epsr_teflon / 500 * np.pi * eps0 / np.log(ss_outer_radius / ss_inner_radius)
            ss_frequency = 1/(0.693*2*ss_resistance*ss_capacity)



        # # Simulation outputs
        #print('Total outflow of gauge over %4.1f s : %4.3f l' % (time_end-time_start, sg_total_outflow_volume))
        if draw_graphs:
            sim_fig = plt.figure('Tank and siphon gauge')
            # Tank
            tk_ax1 = sim_fig.add_subplot(4, 1, 1)
            tk_ax1.plot(t, tk_h, '-b')
            tk_ax1.set_ylabel('level in \nupper tank [mm]')
            tk_ax2 = sim_fig.add_subplot(4, 1, 2, sharex=tk_ax1)
            tk_ax2.plot(t, tk_o, '-r')
            tk_ax2.hold('on')
            tk_ax2.plot(t, tk_i, '-g')
            tk_ax2.set_ylabel('inflow in \nupper tank and\n outflow to \nsiphon gauge [l/h]')
            # Siphon
            tk_ax3 = sim_fig.add_subplot(4, 1, 3, sharex=tk_ax1)
            tk_ax3.plot(t, sg_h, '-b')
            tk_ax3.set_ylabel('level in \nsiphon gauge [mm]')
            tk_ax4 = sim_fig.add_subplot(4, 1, 4, sharex=tk_ax1)
            tk_ax4.plot(t, sg_o, '-g')
            tk_ax4.hold('on')
            tk_ax4.plot(t, sg_a, '-k')
            tk_ax4.set_xlabel('time [s]')
            tk_ax4.set_ylabel('outflow of \nsiphon gauge [l/h]')

            # Data acquisition system output
            das_fig = plt.figure('DAS acquisition')
            das_ax1 = das_fig.add_subplot(5, 1, 1, sharex=tk_ax1)
            das_ax1.plot(t, ss_counter, '-k')
            das_ax1.set_ylabel('Sensor oscillations [-]')

        # resample oscillations to compute DAS frequencies
        das_t = []
        das_frequencies = []
        for i in range(0, len(ss_counter)-int(das_period / time_step), int(das_period / time_step)):
            freq = 0
            for j in range(0, int(das_period / time_step)):
                freq += ss_counter[i+j]
            das_t.append(time_start+(i+j)*time_step)
            das_frequencies.append(freq/das_period)
        x, das_siphoning = schmitt_trigger(das_frequencies, 5000, 7000, 9000)
        das_sawtooth, das_slope = comb_to_linapprox(das_siphoning)
        das_volume = das_sawtooth*sg_siphon_height*sg_tube_area/1000000
        das_flow = das_slope *sg_siphon_height*sg_tube_area/1000000 / (das_period/3600)

        if draw_graphs:
            das_ax2 = das_fig.add_subplot(5, 1, 2, sharex=tk_ax1)
            das_ax2.plot(das_t, das_frequencies, '-r')
            das_ax2.set_ylabel('DAS Frequencies [Hz]')
            das_ax3 = das_fig.add_subplot(5, 1, 3, sharex=tk_ax1)
            das_ax3.plot(das_t, das_siphoning, '-k')
            das_ax3.set_ylabel('Siphoning [0/1]')
            das_ax4 = das_fig.add_subplot(5, 1, 4, sharex=tk_ax1)
            das_ax4.plot(das_t, das_volume, '-r')
            das_ax4.set_xlabel('time [s]')
            das_ax4.set_ylabel('Volume [l]')
            das_ax4.hold('on')
            das_ax4.plot(t, np.cumsum(tk_o)/3600*time_step, '-g')
            das_ax5 = das_fig.add_subplot(5, 1, 5, sharex=tk_ax1)
            das_ax5.plot(das_t, das_flow, '-g')
            das_ax5.set_xlabel('time [s]')
            das_ax5.set_ylabel('Flow [l/h]')
            plt.show()

        print('Estimated total Volume : %d x %4.3f l = %4.3f l' %(np.sum(das_siphoning), sg_tube_area*sg_siphon_height/1000000, np.sum(das_siphoning)*sg_tube_area*sg_siphon_height/1000000))
        print('________________________________________________')
        inflow.append(tk_inflow_mean)
        estimated_inflow.append(2*(das_volume[1349]-das_volume[449]))

    err_fig = plt.figure('errors')
    flow_error = []
    for i in range(0, len(inflow)):
        flow_error.append(100*(inflow[i] - estimated_inflow[i])/estimated_inflow[i])
    axes = err_fig.add_subplot(2, 1, 1)
    axes.plot(estimated_inflow, inflow, '-b')
    axes.set_xlabel('estimated inflow [l/h]')
    axes.set_ylabel('real inflow [l/h]')
    plt.xlim(0.0, 15.0)
    plt.ylim(0.0, 15.0)
    plt.grid(b=True, which='major', color='k', linestyle='-')
    axes2 = err_fig.add_subplot(2, 1, 2, sharex=axes)
    axes2.plot(estimated_inflow, flow_error, '-r')
    axes2.set_xlabel('estimated inflow [l/h]')
    axes2.set_ylabel('relative error [%]')
    plt.xlim(0.0, 15.0)
    plt.ylim(0.0, 50.0)
    plt.grid(b=True, which='major', color='k', linestyle='-')
    plt.show()

    calibration = []
    for i in range(len(flow_error)):
        calibration.append(str('\t'.join(list(map(str,[estimated_inflow[i],flow_error[i],'\n'])))))
    if save_calibration:
        with open(calibration_file,'w+') as cal_file:
            cal_file.writelines(calibration)

    if load_calibration:
        with open(calibration_file,'r') as cal_file:
            rows=[list(map(float,L.strip().split('\t'))) for L in cal_file]

        cal_estimated_inflow, cal_flow_error = [], []
        for i in range(len(rows)):
            cal_estimated_inflow.append(rows[i][0])
            cal_flow_error.append(rows[i][1])

        cal_inflow, cal_error = [], []
        for i in range(len(cal_estimated_inflow)-1):
            tmp_inflow=np.linspace(cal_estimated_inflow[i],cal_estimated_inflow[i+1],10)
            tmp_error=np.linspace(cal_flow_error[i],cal_flow_error[i+1],10)
            for j in range(len(tmp_error)):
                cal_inflow.append(tmp_inflow[j])
                cal_error.append(tmp_error[j])
        corr_flow = []
        for i in range(len(das_flow)):
            stop = 0
            for j in range(len(cal_error)):
                if round(das_flow[i],1) == round(cal_inflow[j],1) and stop == 0:
                    corr = cal_error[j]
                    stop ==1
            corr_flow.append(das_flow[i]*(1.0 + corr/100))
        corr_fig = plt.figure('Corrections')
        das_ax1 = corr_fig.add_subplot(1, 1, 1)
        das_ax1.plot(t, tk_i, '-g', label='simulated inflow')
        das_ax1.plot(das_t, das_flow, '-b',label='retrieved inflow')
        das_ax1.plot(das_t, corr_flow, '-r',label='corrected retrieved inflow')
        das_ax1.set_xlabel('time [s]')
        das_ax1.set_ylabel('Flow [l/h]')
        plt.legend()
        plt.show()