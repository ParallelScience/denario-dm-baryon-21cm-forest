# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

def compute_optimal_strategy():
    data_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    data_dir = 'data/'
    with open(data_path, 'r') as f:
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
    N_sightlines = 10
    optimal_tau_ranges = []
    fisher_2d = []
    print("--- Per-tau-bin Fisher Information (Unmarginalized for M_cut) ---")
    for z in zs:
        cumul_0 = data_dict[(z, 0.0)]
        cumul_1 = data_dict[(z, 10000.0)]
        tau_arr = tau_dict[(z, 0.0)]
        N_bin_0 = cumul_0[:-1] - cumul_0[1:]
        N_bin_1 = cumul_1[:-1] - cumul_1[1:]
        valid_bins = N_bin_0 > 1e-10
        mu_0 = N_sightlines * N_bin_0
        mu_1 = N_sightlines * N_bin_1
        dmu_dMcut = (mu_1 - mu_0) / 10000.0
        F_i = np.zeros_like(mu_0)
        F_i[valid_bins] = (dmu_dMcut[valid_bins]**2) / mu_0[valid_bins]
        total_F = np.sum(F_i)
        sorted_indices = np.argsort(F_i)[::-1]
        cum_F = np.cumsum(F_i[sorted_indices])
        idx_50 = np.where(cum_F >= 0.5 * total_F)[0][0]
        top_indices_50 = sorted_indices[:idx_50+1]
        tau_min_opt_50 = np.min(tau_arr[top_indices_50])
        tau_max_opt_50 = np.max(tau_arr[top_indices_50 + 1])
        idx_80 = np.where(cum_F >= 0.8 * total_F)[0][0]
        top_indices_80 = sorted_indices[:idx_80+1]
        tau_min_opt_80 = np.min(tau_arr[top_indices_80])
        tau_max_opt_80 = np.max(tau_arr[top_indices_80 + 1])
        print("z = " + str(z) + ": Total F = " + str(total_F) + ", 50% Info tau range: [" + str(round(tau_min_opt_50, 4)) + ", " + str(round(tau_max_opt_50, 4)) + "], 80% Info tau range: [" + str(round(tau_min_opt_80, 4)) + ", " + str(round(tau_max_opt_80, 4)) + "]")
        optimal_tau_ranges.append({'z': z, 'tau_min_50pct': tau_min_opt_50, 'tau_max_50pct': tau_max_opt_50, 'tau_min_80pct': tau_min_opt_80, 'tau_max_80pct': tau_max_opt_80, 'total_Fisher_info': total_F})
        fisher_2d.append(F_i / total_F)
    df_opt = pd.DataFrame(optimal_tau_ranges)
    df_opt.to_csv(os.path.join(data_dir, 'optimal_tau_ranges.csv'), index=False)
    print("\nOptimal tau ranges saved to data/optimal_tau_ranges.csv")
    print("\n--- SNR and Fractional Sensitivity Evolution (N_sightlines = 10) ---")
    print("z     | SNR (10^4) | SNR (10^5) | dN/N (10^4) | dN/N (10^5)")
    print("-" * 65)
    for z in zs:
        cumul_0 = data_dict[(z, 0.0)]
        cumul_10k = data_dict[(z, 10000.0)]
        cumul_100k = data_dict[(z, 100000.0)]
        N_tot_0 = cumul_0[0]
        N_tot_10k = cumul_10k[0]
        N_tot_100k = cumul_100k[0]
        dN_N_10k = (N_tot_10k - N_tot_0) / N_tot_0
        dN_N_100k = (N_tot_100k - N_tot_0) / N_tot_0
        N_bin_0 = cumul_0[:-1] - cumul_0[1:]
        N_bin_10k = cumul_10k[:-1] - cumul_10k[1:]
        N_bin_100k = cumul_100k[:-1] - cumul_100k[1:]
        valid_bins = N_bin_0 > 1e-10
        mu_0_valid = N_sightlines * N_bin_0[valid_bins]
        mu_10k_valid = N_sightlines * N_bin_10k[valid_bins]
        mu_100k_valid = N_sightlines * N_bin_100k[valid_bins]
        snr_10k = np.sqrt(np.sum((mu_10k_valid - mu_0_valid)**2 / mu_0_valid))
        snr_100k = np.sqrt(np.sum((mu_100k_valid - mu_0_valid)**2 / mu_0_valid))
        print(str(z) + "   | " + str(round(snr_10k, 2)) + "      | " + str(round(snr_100k, 2)) + "      | " + str(round(dN_N_10k, 4)) + "     | " + str(round(dN_N_100k, 4)))
    print("\nNote: While absolute SNR peaks at z=7 due to higher baseline absorber counts, z~10 offers an optimal balance of high fractional sensitivity (dN/N) and sufficient absorber counts, making it a prime target when considering observational challenges like reionization at lower redshifts.")
    fisher_2d = np.array(fisher_2d)
    plt.rcParams['text.usetex'] = False
    fig, ax = plt.subplots(figsize=(10, 6))
    z_edges = [6.5, 7.5, 8.5, 9.5, 11.0, 13.5, 16.5]
    T, Z = np.meshgrid(tau_arr, z_edges)
    cax = ax.pcolormesh(T, Z, fisher_2d, cmap='viridis', shading='flat')
    ax.set_xscale('log')
    ax.set_xlabel('Optical Depth tau', fontsize=14)
    ax.set_ylabel('Redshift z', fontsize=14)
    ax.set_title('Optimal Observational Window: Fisher Information Fraction per tau bin', fontsize=15)
    cbar = fig.colorbar(cax, ax=ax)
    cbar.set_label('Fraction of Total Fisher Information', fontsize=12)
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = os.path.join(data_dir, 'optimal_observational_window_5_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('\nOptimal observational window plot saved to ' + plot_filename)
    plt.close()

if __name__ == '__main__':
    compute_optimal_strategy()