# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import os

def analyze_sensitivity():
    json_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
    z_vals = sorted(list(set([r['z'] for r in grid_data])))
    f_cool_vals = sorted(list(set([r['f_cool'] for r in grid_data])))
    M_cut_vals = sorted(list(set([r['M_cut'] for r in grid_data])))
    tau_arr = np.array(grid_data[0]['tau_arr'])
    dN_dtau_grid = np.zeros((len(z_vals), len(f_cool_vals), len(M_cut_vals), len(tau_arr)))
    cumul_grid = np.zeros((len(z_vals), len(f_cool_vals), len(M_cut_vals), len(tau_arr)))
    for r in grid_data:
        z_idx = z_vals.index(r['z'])
        f_idx = f_cool_vals.index(r['f_cool'])
        m_idx = M_cut_vals.index(r['M_cut'])
        tau = np.array(r['tau_arr'])
        cumul = np.array(r['cumulvec'])
        dN_dtau = -np.gradient(cumul, tau)
        dN_dtau_grid[z_idx, f_idx, m_idx, :] = dN_dtau
        cumul_grid[z_idx, f_idx, m_idx, :] = cumul
    d_dN_dtau_dfcool = np.gradient(dN_dtau_grid, np.array(f_cool_vals), axis=1)
    d_dN_dtau_dMcut = np.gradient(dN_dtau_grid, np.array(M_cut_vals), axis=2)
    range_Mcut = max(M_cut_vals) - min(M_cut_vals)
    range_fcool = max(f_cool_vals) - min(f_cool_vals)
    print("--- Sensitivity Analysis: Dominance of Structure Suppression ---")
    print("Parameter ranges: Delta M_cut = " + str(range_Mcut) + " M_sun, Delta f_cool = " + str(range_fcool))
    for i, z in enumerate(z_vals):
        max_deriv_Mcut_tau = np.max(np.abs(d_dN_dtau_dMcut[i]), axis=(0, 1))
        max_deriv_fcool_tau = np.max(np.abs(d_dN_dtau_dfcool[i]), axis=(0, 1))
        valid = max_deriv_fcool_tau > 1e-15
        ratio_raw = np.zeros_like(max_deriv_Mcut_tau)
        ratio_var = np.zeros_like(max_deriv_Mcut_tau)
        ratio_raw[valid] = max_deriv_Mcut_tau[valid] / max_deriv_fcool_tau[valid]
        ratio_var[valid] = (max_deriv_Mcut_tau[valid] * range_Mcut) / (max_deriv_fcool_tau[valid] * range_fcool)
        global_max_Mcut = np.max(max_deriv_Mcut_tau)
        global_max_fcool = np.max(max_deriv_fcool_tau)
        global_var_ratio = (global_max_Mcut * range_Mcut) / (global_max_fcool * range_fcool) if global_max_fcool > 0 else np.inf
        print("\nRedshift z = " + str(z))
        print("  Global Max |d(dN/dtau)/dM_cut|: " + str(global_max_Mcut) + " M_sun^-1")
        print("  Global Max |d(dN/dtau)/df_cool|: " + str(global_max_fcool))
        print("  Ratio of Global Max Variations (Effect Size): " + str(global_var_ratio))
        if np.any(valid):
            print("  Across all tau bins (where d/df_cool != 0):")
            print("    Min Variation Ratio: " + str(np.min(ratio_var[valid])))
            print("    Mean Variation Ratio: " + str(np.mean(ratio_var[valid])))
            print("    Max Variation Ratio: " + str(np.max(ratio_var[valid])))
        else:
            print("  Derivatives w.r.t f_cool are zero across all tau bins.")
    out_path = 'data/differential_distributions_and_derivatives.npz'
    np.savez(out_path, z_vals=z_vals, f_cool_vals=f_cool_vals, M_cut_vals=M_cut_vals, tau_arr=tau_arr, dN_dtau_grid=dN_dtau_grid, cumul_grid=cumul_grid, d_dN_dtau_dfcool=d_dN_dtau_dfcool, d_dN_dtau_dMcut=d_dN_dtau_dMcut)
    print("\nSaved differential distributions and derivatives to " + out_path)

if __name__ == '__main__':
    analyze_sensitivity()