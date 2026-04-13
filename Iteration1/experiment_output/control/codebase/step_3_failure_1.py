# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime

def compute_fisher():
    data_dir = 'data/'
    with open(os.path.join(data_dir, 'hayashi_grid.json'), 'r') as f:
        grid_data = json.load(f)
    data_dict = {}
    tau_dict = {}
    for record in grid_data:
        if record['f_cool'] == 1.0:
            z = record['z']
            mcut = record['M_cut']
            data_dict[(z, mcut)] = np.array(record['cumulvec'])
            tau_dict[(z, mcut)] = np.array(record['tau_arr'])
    zs = [7.0, 8.0, 9.0, 10.0, 12.0, 15.0]
    N_sightlines_default = 10
    results = []
    fisher_results = {}
    print('--- 1-sigma M_cut constraints (N_sightlines = 10) ---')
    print('Marginalizing over unknown normalization A (fiducial A=1)')
    for z in zs:
        cumul_0 = data_dict[(z, 0.0)]
        cumul_1 = data_dict[(z, 10000.0)]
        tau_arr = tau_dict[(z, 0.0)]
        N_bin_0 = cumul_0[:-1] - cumul_0[1:]
        N_bin_1 = cumul_1[:-1] - cumul_1[1:]
        delta_tau = tau_arr[1:] - tau_arr[:-1]
        dN_dtau_0 = N_bin_0 / delta_tau
        dN_dtau_1 = N_bin_1 / delta_tau
        valid_bins = N_bin_0 > 1e-8
        dN_dtau_0 = dN_dtau_0[valid_bins]
        dN_dtau_1 = dN_dtau_1[valid_bins]
        delta_tau = delta_tau[valid_bins]
        d_dN_dtau_dMcut_scaled = (dN_dtau_1 - dN_dtau_0)
        d_dN_dtau_dA = dN_dtau_0
        mu = N_sightlines_default * dN_dtau_0 * delta_tau
        dmu_dMcut_scaled = N_sightlines_default * d_dN_dtau_dMcut_scaled * delta_tau
        dmu_dA = N_sightlines_default * d_dN_dtau_dA * delta_tau
        F_11_scaled = np.sum((dmu_dMcut_scaled ** 2) / mu)
        F_22 = np.sum((dmu_dA ** 2) / mu)
        F_12_scaled = np.sum((dmu_dMcut_scaled * dmu_dA) / mu)
        F_scaled = np.array([[F_11_scaled, F_12_scaled], [F_12_scaled, F_22]])
        F_base_scaled = F_scaled / N_sightlines_default
        fisher_results[z] = F_base_scaled
        try:
            C_scaled = np.linalg.inv(F_scaled)
            if C_scaled[0, 0] < 0:
                sigma_Mcut = np.inf
            else:
                sigma_Mcut = np.sqrt(C_scaled[0, 0]) * 10000.0
        except np.linalg.LinAlgError:
            sigma_Mcut = np.inf
        sigma_Mcut_unmarg = (1.0 / np.sqrt(F_11_scaled)) * 10000.0
        print('z = ' + str(z) + ': sigma(M_cut) = ' + str(round(sigma_Mcut, 2)) + ' M_sun (unmarginalized: ' + str(round(sigma_Mcut_unmarg, 2)) + ' M_sun)')
        results.append({'z': z, 'sigma_Mcut': sigma_Mcut})
    best_z = min(results, key=lambda x: x['sigma_Mcut'])['z']
    print('\nOptimal redshift for SKA observations: z = ' + str(best_z))
    N_sightlines_arr = np.arange(1, 101)
    sigma_Mcut_arr = []
    F_base_opt = fisher_results[best_z]
    for N_s in N_sightlines_arr:
        F_scaled = F_base_opt * N_s
        try:
            C_scaled = np.linalg.inv(F_scaled)
            if C_scaled[0, 0] < 0:
                sigma_Mcut_arr.append(np.inf)
            else:
                sigma_Mcut_arr.append(np.sqrt(C_scaled[0, 0]) * 10000.0)
        except np.linalg.LinAlgError:
            sigma_Mcut_arr.append(np.inf)
    sigma_Mcut_arr = np.array(sigma_Mcut_arr)
    print('At z = ' + str(best_z) + ', sigma(M_cut) with 10 sightlines = ' + str(round(sigma_Mcut_arr[9], 2)) + ' M_sun')
    print('At z = ' + str(best_z) + ', sigma(M_cut) with 100 sightlines = ' + str(round(sigma_Mcut_arr[99], 2)) + ' M_sun')
    np.savez(os.path.join(data_dir, 'fisher_forecast_results.npz'), zs=zs, sigma_Mcut_z=[r['sigma_Mcut'] for r in results], best_z=best_z, N_sightlines=N_sightlines_arr, sigma_Mcut_Nsightlines=sigma_Mcut_arr)
    print('\nFisher forecast results saved to data/fisher_forecast_results.npz')
    plt.rcParams['text.usetex'] = False
    plt.figure(figsize=(8, 6))
    valid_plot = np.isfinite(sigma_Mcut_arr)
    if np.any(valid_plot):
        plt.plot(N_sightlines_arr[valid_plot], sigma_Mcut_arr[valid_plot], 'b-', linewidth=2)
    else:
        plt.plot(N_sightlines_arr, sigma_Mcut_arr, 'b-', linewidth=2)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Number of Sightlines (N_obs)')
    plt.ylabel('1-sigma M_cut Constraint [M_sun]')
    plt.title('Fisher Forecast: M_cut Sensitivity vs Sightlines at z=' + str(best_z))
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = os.path.join(data_dir, 'fisher_mcut_vs_sightlines_3_' + timestamp + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('Fisher forecast plot saved to ' + plot_filename)
    plt.close()

if __name__ == '__main__':
    compute_fisher()