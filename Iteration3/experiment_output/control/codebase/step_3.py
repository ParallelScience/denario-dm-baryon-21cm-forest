# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib

matplotlib.rcParams['text.usetex'] = False

def map_Mcut_to_sigma_n0(M_cut):
    return 1e-29 * M_cut

def map_Mcut_to_sigma_n4(M_cut, z=None):
    return 1e-41 * (M_cut / 1e5)

def main():
    data_path = 'data/processed_data_step1.pkl'
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    grid_data = data['grid_data']
    baselines = data['baselines']
    for record in grid_data:
        record['sigma_n0'] = map_Mcut_to_sigma_n0(record['M_cut'])
        record['sigma_n4'] = map_Mcut_to_sigma_n4(record['M_cut'], record['z'])
    zs = sorted(list(set([r['z'] for r in grid_data])))
    sensitivity_results = {'z': zs, 'M_cut_10': [], 'M_cut_20': [], 'sigma_n0_10': [], 'sigma_n0_20': [], 'sigma_n4_10': [], 'sigma_n4_20': []}
    for z in zs:
        n_abs_0 = baselines[z]
        record_1e4 = next((r for r in grid_data if r['z'] == z and r['f_cool'] == 1.0 and r['M_cut'] == 1e4), None)
        n_abs_1e4 = record_1e4['Nabs_total']
        frac_1e4 = (n_abs_0 - n_abs_1e4) / n_abs_0
        m_cut_10 = 1e4 * (0.10 / frac_1e4)
        m_cut_20 = 1e4 * (0.20 / frac_1e4)
        sensitivity_results['M_cut_10'].append(m_cut_10)
        sensitivity_results['M_cut_20'].append(m_cut_20)
        sensitivity_results['sigma_n0_10'].append(map_Mcut_to_sigma_n0(m_cut_10))
        sensitivity_results['sigma_n0_20'].append(map_Mcut_to_sigma_n0(m_cut_20))
        sensitivity_results['sigma_n4_10'].append(map_Mcut_to_sigma_n4(m_cut_10, z))
        sensitivity_results['sigma_n4_20'].append(map_Mcut_to_sigma_n4(m_cut_20, z))
    print("--- Sensitivity Mapping Results ---")
    print("Redshift | M_cut (10%) [M_sun] | M_cut (20%) [M_sun] | sigma_n0 (10%) [cm^2/GeV] | sigma_n0 (20%) [cm^2/GeV] | sigma_n4 (10%) [cm^2/GeV] | sigma_n4 (20%) [cm^2/GeV]")
    print("-" * 155)
    for i, z in enumerate(zs):
        m10 = sensitivity_results['M_cut_10'][i]
        m20 = sensitivity_results['M_cut_20'][i]
        s0_10 = sensitivity_results['sigma_n0_10'][i]
        s0_20 = sensitivity_results['sigma_n0_20'][i]
        s4_10 = sensitivity_results['sigma_n4_10'][i]
        s4_20 = sensitivity_results['sigma_n4_20'][i]
        print(str(z).ljust(8) + " | " + str(round(m10, 2)).ljust(19) + " | " + str(round(m20, 2)).ljust(19) + " | " + "{:.2e}".format(s0_10).ljust(25) + " | " + "{:.2e}".format(s0_20).ljust(25) + " | " + "{:.2e}".format(s4_10).ljust(25) + " | " + "{:.2e}".format(s4_20))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].plot(zs, sensitivity_results['sigma_n0_10'], marker='o', label='10% Suppression')
    axes[0].plot(zs, sensitivity_results['sigma_n0_20'], marker='s', label='20% Suppression')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Redshift z')
    axes[0].set_ylabel('Cross-section sigma_0/m_chi [cm^2/GeV]')
    axes[0].set_title('Sensitivity for Velocity-Independent Scattering (n=0)')
    axes[0].legend()
    axes[0].grid(True, which='both', ls='--', alpha=0.5)
    axes[1].plot(zs, sensitivity_results['sigma_n4_10'], marker='o', label='10% Suppression')
    axes[1].plot(zs, sensitivity_results['sigma_n4_20'], marker='s', label='20% Suppression')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('Redshift z')
    axes[1].set_ylabel('Cross-section sigma_0/m_chi [cm^2/GeV]')
    axes[1].set_title('Sensitivity for Coulomb-like Scattering (n=-4)')
    axes[1].legend()
    axes[1].grid(True, which='both', ls='--', alpha=0.5)
    fig.tight_layout()
    plot_path = 'data/sensitivity_curves_4_' + timestamp + '.png'
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)
    print("\nPlot saved to " + plot_path)
    z_target = 10.0
    records_z10 = [r for r in grid_data if r['z'] == z_target and r['f_cool'] == 1.0]
    records_z10.sort(key=lambda x: x['M_cut'])
    sigma_n0_vals = [r['sigma_n0'] for r in records_z10]
    sigma_n4_vals = [r['sigma_n4'] for r in records_z10]
    n_abs_vals = [r['Nabs_total'] for r in records_z10]
    fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
    sigma_n0_nonzero = [s for s in sigma_n0_vals if s > 0]
    sigma_n4_nonzero = [s for s in sigma_n4_vals if s > 0]
    n_abs_nonzero = [n for s, n in zip(sigma_n0_vals, n_abs_vals) if s > 0]
    cdm_n_abs = baselines[z_target]
    axes2[0].plot(sigma_n0_nonzero, n_abs_nonzero, marker='o', color='b')
    axes2[0].axhline(cdm_n_abs, color='k', linestyle='--', label='CDM Baseline')
    axes2[0].set_xscale('log')
    axes2[0].set_xlabel('Cross-section sigma_0/m_chi [cm^2/GeV]')
    axes2[0].set_ylabel('Total Absorbers N_abs')
    axes2[0].set_title('N_abs vs sigma_0/m_chi (n=0, z=' + str(z_target) + ')')
    axes2[0].legend()
    axes2[0].grid(True, which='both', ls='--', alpha=0.5)
    axes2[1].plot(sigma_n4_nonzero, n_abs_nonzero, marker='o', color='r')
    axes2[1].axhline(cdm_n_abs, color='k', linestyle='--', label='CDM Baseline')
    axes2[1].set_xscale('log')
    axes2[1].set_xlabel('Cross-section sigma_0/m_chi [cm^2/GeV]')
    axes2[1].set_ylabel('Total Absorbers N_abs')
    axes2[1].set_title('N_abs vs sigma_0/m_chi (n=-4, z=' + str(z_target) + ')')
    axes2[1].legend()
    axes2[1].grid(True, which='both', ls='--', alpha=0.5)
    fig2.tight_layout()
    plot2_path = 'data/Nabs_vs_sigma_5_' + timestamp + '.png'
    fig2.savefig(plot2_path, dpi=300)
    plt.close(fig2)
    print("Plot saved to " + plot2_path)
    data['grid_data'] = grid_data
    data['sensitivity_results'] = sensitivity_results
    output_path = 'data/processed_data_step3.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(data, f)
    print("Updated data with cross-sections saved to " + output_path)

if __name__ == '__main__':
    main()