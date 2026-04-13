# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import numpy as np
from scipy.interpolate import interp1d

def map_parameters():
    data_path = 'data/differential_distributions_and_derivatives.npz'
    if not os.path.exists(data_path):
        print('Error: ' + data_path + ' not found.')
        return
    data = np.load(data_path)
    z_vals = data['z_vals']
    f_cool_vals = data['f_cool_vals']
    M_cut_vals = data['M_cut_vals']
    M_cut_points = np.array([1e4, 1e5, 1e6])
    sigma_M_cut_points = np.array([3e-25, 1e-24, 1e-23])
    log_M_cut = np.log10(M_cut_points)
    log_sigma_M_cut = np.log10(sigma_M_cut_points)
    interp_M_cut = interp1d(log_M_cut, log_sigma_M_cut, fill_value='extrapolate')
    def map_M_cut_to_sigma(M_cut):
        if M_cut == 0:
            return 0.0
        return float(10**interp_M_cut(np.log10(M_cut)))
    f_cool_points = np.array([0.1, 0.5])
    sigma_f_cool_points = np.array([1e-23, 1e-24])
    log_f_cool = np.log10(f_cool_points)
    log_sigma_f_cool = np.log10(sigma_f_cool_points)
    interp_f_cool = interp1d(log_f_cool, log_sigma_f_cool, fill_value='extrapolate')
    def map_f_cool_to_sigma(f_cool):
        if f_cool == 1.0:
            return 0.0
        return float(10**interp_f_cool(np.log10(f_cool)))
    sigma_M_cut_n0 = np.array([map_M_cut_to_sigma(m) for m in M_cut_vals])
    sigma_f_cool_n0 = np.array([map_f_cool_to_sigma(f) for f in f_cool_vals])
    print('--- Parameter Mapping to Cross-Section (sigma_0/m_chi) ---')
    print('Units: cm^2/GeV')
    print('\nMapping for M_cut (n=0):')
    for m, sig in zip(M_cut_vals, sigma_M_cut_n0):
        print('  M_cut = ' + str(m) + ' M_sun -> sigma_0/m_chi = ' + str(sig))
    print('\nMapping for f_cool (n=0):')
    for f, sig in zip(f_cool_vals, sigma_f_cool_n0):
        print('  f_cool = ' + str(f) + ' -> sigma_0/m_chi = ' + str(sig))
    print('\n--- Redshift Dependence for n=-4 (Coulomb-like) ---')
    print('Scaling relation: sigma_0/m_chi (n=-4) = sigma_0/m_chi (n=0) * ((1+z)/(1+10))^2')
    sigma_M_cut_n4_grid = np.zeros((len(z_vals), len(M_cut_vals)))
    for i, z in enumerate(z_vals):
        scaling = ((1 + z) / 11.0)**2
        sigma_M_cut_n4_grid[i, :] = sigma_M_cut_n0 * scaling
        print('  z = ' + str(z) + ' -> scaling factor = ' + str(scaling))
    out_path = 'data/mapped_cross_sections.npz'
    np.savez(out_path, z_vals=z_vals, M_cut_vals=M_cut_vals, f_cool_vals=f_cool_vals, sigma_M_cut_n0=sigma_M_cut_n0, sigma_f_cool_n0=sigma_f_cool_n0, sigma_M_cut_n4_grid=sigma_M_cut_n4_grid)
    print('\nSaved mapped cross-section data to ' + out_path)

if __name__ == '__main__':
    map_parameters()