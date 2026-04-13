# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def cross_section_mapping():
    data_dir = 'data/'
    M_cuts = [0, 1e4, 1e5, 5e5, 1e6]
    z_ref = 10.0
    print('--- DM-Baryon Cross-Section Mapping (m_chi = 1 GeV) ---')
    print('Reference redshift for n=-4: z = ' + str(z_ref))
    print('M_cut [M_sun]   | sigma_0/m_chi (n=0) [cm^2/GeV] | sigma_0/m_chi (n=-4) [cm^2/GeV]')
    print('-' * 80)
    mapping_data = []
    for Mcut in M_cuts:
        sigma_n0 = 1e-29 * Mcut
        if Mcut > 0:
            sigma_n4 = 1e-41 * (Mcut / 1e5) * ((1 + z_ref) / 11.0)**4
        else:
            sigma_n4 = 0.0
        print(str(Mcut) + ' | ' + str(sigma_n0) + ' | ' + str(sigma_n4))
        mapping_data.append({'M_cut': Mcut, 'sigma_n0': sigma_n0, 'sigma_n4': sigma_n4})
    df_mcut = pd.read_csv(os.path.join(data_dir, 'sensitivity_mcut.csv'), index_col=0)
    zs = df_mcut.index.values
    mcut_10pct = []
    mcut_20pct = []
    col_10k = [c for c in df_mcut.columns if '10000' in c][0]
    for z in zs:
        val_10k = abs(df_mcut.loc[z, col_10k])
        m_10 = 10000.0 * (0.10 / val_10k)**(2.0/3.0)
        m_20 = 10000.0 * (0.20 / val_10k)**(2.0/3.0)
        mcut_10pct.append(m_10)
        mcut_20pct.append(m_20)
    mcut_10pct = np.array(mcut_10pct)
    mcut_20pct = np.array(mcut_20pct)
    sigma_n0_10pct = 1e-29 * mcut_10pct
    sigma_n0_20pct = 1e-29 * mcut_20pct
    fisher_data = np.load(os.path.join(data_dir, 'fisher_forecast_results.npz'))
    fisher_zs = fisher_data['zs']
    fisher_sigma_Mcut = fisher_data['sigma_Mcut_z']
    sigma_n0_fisher = 1e-29 * fisher_sigma_Mcut
    print('\n--- Sensitivity Curves Data (n=0) ---')
    print('z     | 10% change [cm^2/GeV] | 20% change [cm^2/GeV] | Fisher 1-sigma [cm^2/GeV]')
    print('-' * 85)
    for i, z in enumerate(zs):
        idx = np.where(fisher_zs == z)[0][0]
        print(str(z) + ' | ' + str(sigma_n0_10pct[i]) + ' | ' + str(sigma_n0_20pct[i]) + ' | ' + str(sigma_n0_fisher[idx]))
    print('\n--- Comparison with Existing Constraints (n=0) ---')
    print('21 cm Forest (Fisher 1-sigma at z=7): ~' + str(sigma_n0_fisher[0]) + ' cm^2/GeV')
    print('Lyman-alpha Forest: ~1e-24 cm^2/GeV')
    print('CMB (Xu et al. 2018): < 1e-22 cm^2/GeV')
    print('Global 21 cm (EDGES/SARAS3): ~1e-21 cm^2/GeV')
    plt.rcParams['text.usetex'] = False
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(zs, sigma_n0_10pct, 'b--', linewidth=2, label='21 cm Forest (10% change in N_abs)')
    ax.plot(zs, sigma_n0_20pct, 'b-.', linewidth=2, label='21 cm Forest (20% change in N_abs)')
    ax.plot(fisher_zs, sigma_n0_fisher, 'r-', linewidth=2, marker='o', label='21 cm Forest (Fisher 1-sigma, N_obs=10)')
    ax.axhline(1e-22, color='k', linestyle='-', linewidth=1.5, label='CMB (Xu et al. 2018)')
    ax.fill_between(zs, 1e-22, 1e-18, color='k', alpha=0.15)
    ax.axhline(1e-21, color='g', linestyle='-', linewidth=1.5, label='Global 21 cm (EDGES/SARAS3)')
    ax.fill_between(zs, 1e-21, 1e-18, color='g', alpha=0.15)
    ax.axhline(1e-24, color='purple', linestyle='-', linewidth=1.5, label='Lyman-alpha Forest')
    ax.fill_between(zs, 1e-24, 1e-18, color='purple', alpha=0.15)
    ax.set_yscale('log')
    ax.set_xlim(min(zs), max(zs))
    ax.set_ylim(1e-27, 1e-20)
    ax.set_xlabel('Redshift z', fontsize=14)
    ax.set_ylabel('DM-Baryon Cross-Section sigma_0/m_chi [cm^2/GeV]', fontsize=14)
    ax.set_title('Sensitivity of 21 cm Forest to DM-Baryon Scattering (n=0)', fontsize=15)
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(loc='lower right', fontsize=11)
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = os.path.join(data_dir, 'cross_section_constraints_4_' + timestamp + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('\nComparative constraints plot saved to ' + plot_filename)
    plt.close()
    np.savez(os.path.join(data_dir, 'mapped_cross_sections.npz'), zs=zs, mcut_10pct=mcut_10pct, mcut_20pct=mcut_20pct, sigma_n0_10pct=sigma_n0_10pct, sigma_n0_20pct=sigma_n0_20pct, fisher_zs=fisher_zs, sigma_n0_fisher=sigma_n0_fisher)
    print('Mapped cross-section data saved to data/mapped_cross_sections.npz')

if __name__ == '__main__':
    cross_section_mapping()