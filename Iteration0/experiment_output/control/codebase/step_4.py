# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import numpy as np
from scipy.interpolate import interp1d

def fisher_forecast():
    data_path = 'data/differential_distributions_and_derivatives.npz'
    data = np.load(data_path)
    z_vals = data['z_vals']
    f_cool_vals = list(data['f_cool_vals'])
    M_cut_vals = list(data['M_cut_vals'])
    tau_arr = data['tau_arr']
    dN_dtau_grid = data['dN_dtau_grid']
    cumul_grid = data['cumul_grid']
    d_dN_dtau_dMcut = data['d_dN_dtau_dMcut']
    f_idx = f_cool_vals.index(1.0)
    m_idx = M_cut_vals.index(0.0)
    N_sightlines = 10
    delta_tau = np.gradient(tau_arr)
    F_vector = np.zeros(len(z_vals))
    F_scalar = np.zeros(len(z_vals))
    M_cut_1sigma = np.zeros(len(z_vals))
    M_cut_2sigma = np.zeros(len(z_vals))
    print('--- Fisher Information Forecast for SKA (N_sightlines = 10) ---')
    print('Evaluating at CDM baseline (f_cool=1.0, M_cut=0)\n')
    for i, z in enumerate(z_vals):
        dN = dN_dtau_grid[i, f_idx, m_idx, :]
        d_dN = d_dN_dtau_dMcut[i, f_idx, m_idx, :]
        valid = dN > 1e-12
        F_vec = np.sum(N_sightlines * delta_tau[valid] * (d_dN[valid]**2) / dN[valid])
        F_vector[i] = F_vec
        N_abs = cumul_grid[i, f_idx, m_idx, 0]
        dN_abs_dMcut = (cumul_grid[i, f_idx, m_idx+1, 0] - cumul_grid[i, f_idx, m_idx, 0]) / (M_cut_vals[m_idx+1] - M_cut_vals[m_idx])
        F_scal = N_sightlines * (dN_abs_dMcut**2) / N_abs
        F_scalar[i] = F_scal
        ratio = F_vec / F_scal if F_scal > 0 else np.inf
        sigma_Mcut = 1.0 / np.sqrt(F_vec) if F_vec > 0 else np.inf
        M_cut_1sigma[i] = sigma_Mcut
        M_cut_2sigma[i] = 2 * sigma_Mcut
        print('Redshift z = ' + str(z) + ':')
        print('  F_vector (dN/dtau) = ' + str(F_vec))
        print('  F_scalar (N_abs)   = ' + str(F_scal))
        print('  Ratio (Vector/Scalar) = ' + str(ratio))
        print('  1-sigma M_cut sensitivity = ' + str(M_cut_1sigma[i]) + ' M_sun')
        print('  2-sigma M_cut sensitivity = ' + str(M_cut_2sigma[i]) + ' M_sun\n')
    M_cut_points = np.array([1e4, 1e5, 1e6])
    sigma_M_cut_points = np.array([3e-25, 1e-24, 1e-23])
    log_M_cut = np.log10(M_cut_points)
    log_sigma_M_cut = np.log10(sigma_M_cut_points)
    interp_M_cut = interp1d(log_M_cut, log_sigma_M_cut, fill_value='extrapolate')
    def map_M_cut_to_sigma(M_cut):
        if M_cut <= 0:
            return 0.0
        return float(10**interp_M_cut(np.log10(M_cut)))
    sigma_1sigma_n0 = np.zeros(len(z_vals))
    sigma_2sigma_n0 = np.zeros(len(z_vals))
    sigma_1sigma_n4 = np.zeros(len(z_vals))
    sigma_2sigma_n4 = np.zeros(len(z_vals))
    print('--- Mapped Cross-Section Sensitivities ---')
    for i, z in enumerate(z_vals):
        sig1_n0 = map_M_cut_to_sigma(M_cut_1sigma[i])
        sig2_n0 = map_M_cut_to_sigma(M_cut_2sigma[i])
        scaling = ((1 + z) / 11.0)**2
        sig1_n4 = sig1_n0 * scaling
        sig2_n4 = sig2_n0 * scaling
        sigma_1sigma_n0[i] = sig1_n0
        sigma_2sigma_n0[i] = sig2_n0
        sigma_1sigma_n4[i] = sig1_n4
        sigma_2sigma_n4[i] = sig2_n4
        print('Redshift z = ' + str(z) + ':')
        print('  n=0 (Velocity-independent):')
        print('    1-sigma: ' + str(sig1_n0) + ' cm^2/GeV')
        print('    2-sigma: ' + str(sig2_n0) + ' cm^2/GeV')
        print('  n=-4 (Coulomb-like):')
        print('    1-sigma: ' + str(sig1_n4) + ' cm^2/GeV')
        print('    2-sigma: ' + str(sig2_n4) + ' cm^2/GeV\n')
    out_path = 'data/fisher_forecast_results.npz'
    np.savez(out_path, z_vals=z_vals, F_vector=F_vector, F_scalar=F_scalar, M_cut_1sigma=M_cut_1sigma, M_cut_2sigma=M_cut_2sigma, sigma_1sigma_n0=sigma_1sigma_n0, sigma_2sigma_n0=sigma_2sigma_n0, sigma_1sigma_n4=sigma_1sigma_n4, sigma_2sigma_n4=sigma_2sigma_n4)
    print('Saved Fisher forecast results to ' + out_path)

if __name__ == '__main__':
    fisher_forecast()