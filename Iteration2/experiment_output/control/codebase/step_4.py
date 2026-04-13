# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

def compute_fisher_and_optimal_window():
    json_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
    z_list = sorted(list(set([d['z'] for d in grid_data])))
    N_sightlines = 10.0
    def get_xHI_bar(z):
        if z == 7.0: return 0.1
        if z == 8.0: return 0.5
        if z == 9.0: return 0.9
        return 1.0
    results = []
    optimal_tau_info = []
    for z in z_list:
        xHI = get_xHI_bar(z)
        N_eff = N_sightlines * xHI
        d_base = next(d for d in grid_data if d['z'] == z and d['f_cool'] == 1.0 and d['M_cut'] == 0.0)
        tau_arr = np.array(d_base['tau_arr'])
        cumul_base = np.array(d_base['cumulvec'])
        delta_N_base = -np.diff(cumul_base)
        tau_bins = (tau_arr[:-1] + tau_arr[1:]) / 2.0
        d_mcut = next((d for d in grid_data if d['z'] == z and d['f_cool'] == 1.0 and d['M_cut'] == 10000.0), None)
        if d_mcut is None: continue
        cumul_mcut = np.array(d_mcut['cumulvec'])
        delta_N_mcut = -np.diff(cumul_mcut)
        dN_dMcut = (delta_N_mcut - delta_N_base) / 10000.0
        dx = 0.01
        cumul_xhi = np.interp(tau_arr / (1.0 + dx), tau_arr, cumul_base, left=cumul_base[0], right=0.0)
        delta_N_xhi = -np.diff(cumul_xhi)
        dN_dxHI = (delta_N_xhi - delta_N_base) / dx
        dMJ_dJ21 = 0.5 * 1e5 / np.sqrt(0.1)
        dN_dJ21 = dN_dMcut * dMJ_dJ21
        valid = delta_N_base > 1e-5
        F = np.zeros((3, 3))
        derivatives = [dN_dMcut, dN_dxHI, dN_dJ21]
        for i in range(3):
            for j in range(3):
                F[i, j] = N_eff * np.sum((derivatives[i][valid] * derivatives[j][valid]) / delta_N_base[valid])
        P = np.zeros((3, 3))
        P[1, 1] = 1.0 / (0.1**2)
        P[2, 2] = 1.0 / (0.1**2)
        F_tot = F + P
        try:
            Cov = np.linalg.inv(F_tot)
            sigma_Mcut_marg = np.sqrt(Cov[0, 0])
            sigma_Mcut_unmarg = np.sqrt(1.0 / F[0, 0]) if F[0, 0] > 0 else np.inf
        except np.linalg.LinAlgError:
            sigma_Mcut_marg = np.inf
            sigma_Mcut_unmarg = np.inf
        results.append({'z': z, 'xHI_bar': xHI, 'N_eff': N_eff, 'sigma_Mcut_unmarg': sigma_Mcut_unmarg, 'sigma_Mcut_marg': sigma_Mcut_marg})
        info_per_bin = np.zeros_like(delta_N_base)
        info_per_bin[valid] = N_eff * (dN_dMcut[valid]**2) / delta_N_base[valid]
        sorted_indices = np.argsort(info_per_bin)[::-1]
        cum_info = np.cumsum(info_per_bin[sorted_indices])
        tot_info = cum_info[-1]
        if tot_info > 0:
            cutoff_idx = np.searchsorted(cum_info, 0.8 * tot_info)
            optimal_indices = sorted_indices[:cutoff_idx+1]
            opt_tau_min = np.min(tau_bins[optimal_indices])
            opt_tau_max = np.max(tau_bins[optimal_indices])
        else:
            opt_tau_min = np.nan
            opt_tau_max = np.nan
        optimal_tau_info.append({'z': z, 'opt_tau_min': opt_tau_min, 'opt_tau_max': opt_tau_max, 'total_info_Mcut': tot_info})
    df_res = pd.DataFrame(results)
    df_opt = pd.DataFrame(optimal_tau_info)
    plt.rcParams['text.usetex'] = False
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax1 = axes[0]
    ax1.plot(df_res['z'], df_res['sigma_Mcut_marg'], marker='o', linestyle='-', color='red', label='Marginalized')
    ax1.plot(df_res['z'], df_res['sigma_Mcut_unmarg'], marker='s', linestyle='--', color='blue', label='Unmarginalized')
    ax1.set_yscale('log')
    ax1.set_xlabel('Redshift z')
    ax1.set_ylabel('1-sigma Uncertainty on M_cut [M_sun]')
    ax1.set_title('Fisher Forecast: Sensitivity to M_cut')
    ax1.legend()
    ax1.grid(True, which='both', ls='--', alpha=0.5)
    ax2 = axes[1]
    z_opt = 10.0
    d_base = next(d for d in grid_data if d['z'] == z_opt and d['f_cool'] == 1.0 and d['M_cut'] == 0.0)
    tau_arr = np.array(d_base['tau_arr'])
    cumul_base = np.array(d_base['cumulvec'])
    delta_N_base = -np.diff(cumul_base)
    tau_bins = (tau_arr[:-1] + tau_arr[1:]) / 2.0
    d_mcut = next(d for d in grid_data if d['z'] == z_opt and d['f_cool'] == 1.0 and d['M_cut'] == 10000.0)
    cumul_mcut = np.array(d_mcut['cumulvec'])
    delta_N_mcut = -np.diff(cumul_mcut)
    dN_dMcut = (delta_N_mcut - delta_N_base) / 10000.0
    valid = delta_N_base > 1e-5
    info_per_bin = np.zeros_like(delta_N_base)
    N_eff_z10 = 10.0 * get_xHI_bar(z_opt)
    info_per_bin[valid] = N_eff_z10 * (dN_dMcut[valid]**2) / delta_N_base[valid]
    ax2.plot(tau_bins, info_per_bin, color='green', lw=2)
    ax2.set_xscale('log')
    ax2.set_xlabel('Optical Depth (tau)')
    ax2.set_ylabel('Fisher Information for M_cut')
    ax2.set_title('Information Content per tau-bin (z=10)')
    ax2.grid(True, which='both', ls='--', alpha=0.5)
    plt.tight_layout()
    timestamp = int(time.time())
    filename = os.path.join('data', 'fisher_forecast_1_' + str(timestamp) + '.png')
    plt.savefig(filename, dpi=300)
    df_res.to_csv(os.path.join('data', 'fisher_forecast_results.csv'), index=False)
    df_opt.to_csv(os.path.join('data', 'optimal_tau_ranges.csv'), index=False)

if __name__ == '__main__':
    compute_fisher_and_optimal_window()