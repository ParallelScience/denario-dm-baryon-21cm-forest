# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

def sci_fmt(val):
    if val == 0:
        return "0.00e+00"
    exponent = int(np.floor(np.log10(abs(val))))
    mantissa = val / (10**exponent)
    return str(round(mantissa, 2)) + "e" + str(exponent)

def generate_exclusion_contours():
    data_dir = "data/"
    fisher_file = os.path.join(data_dir, "fisher_forecast_results.csv")
    if not os.path.exists(fisher_file):
        print("Error: " + fisher_file + " not found.")
        return
    df = pd.read_csv(fisher_file)
    def map_n0(mcut):
        return 1e-29 * mcut
    def map_n4(mcut, z):
        return 1e-45 * mcut * ((1.0 + z) / 11.0)**(-4)
    results = []
    for _, row in df.iterrows():
        z = row['z']
        sigma_mcut_1sig = row['sigma_Mcut_marg']
        sigma_mcut_2sig = 2.0 * sigma_mcut_1sig
        n0_1sig = map_n0(sigma_mcut_1sig)
        n0_2sig = map_n0(sigma_mcut_2sig)
        n4_1sig = map_n4(sigma_mcut_1sig, z)
        n4_2sig = map_n4(sigma_mcut_2sig, z)
        results.append({'z': z, 'Mcut_1sig': sigma_mcut_1sig, 'Mcut_2sig': sigma_mcut_2sig, 'n0_1sig': n0_1sig, 'n0_2sig': n0_2sig, 'n4_1sig': n4_1sig, 'n4_2sig': n4_2sig})
    df_mapped = pd.DataFrame(results)
    df_mapped.to_csv(os.path.join(data_dir, "mapped_cross_sections.csv"), index=False)
    print("--- Mapped Cross-Sections (1-sigma and 2-sigma) ---")
    for _, row in df_mapped.iterrows():
        print("z = " + str(row['z']) + ":")
        print("  M_cut 1-sigma = " + str(round(row['Mcut_1sig'], 2)) + " M_sun, 2-sigma = " + str(round(row['Mcut_2sig'], 2)) + " M_sun")
        print("  n=0 : 1-sigma = " + sci_fmt(row['n0_1sig']) + " cm^2/GeV, 2-sigma = " + sci_fmt(row['n0_2sig']) + " cm^2/GeV")
        print("  n=-4: 1-sigma = " + sci_fmt(row['n4_1sig']) + " cm^2/GeV, 2-sigma = " + sci_fmt(row['n4_2sig']) + " cm^2/GeV")
    opt_row = df_mapped[df_mapped['z'] == 10.0].iloc[0]
    plt.rcParams['text.usetex'] = False
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    m_chi = np.logspace(-3, 2, 100)
    ax1 = axes[0]
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim(1e-3, 1e2)
    ax1.set_ylim(1e-27, 1e-19)
    ax1.set_xlabel('Dark Matter Mass m_chi [GeV]')
    ax1.set_ylabel('Cross-section / Mass sigma_0/m_chi [cm^2/GeV]')
    ax1.set_title('Exclusion Contours (n=0, Velocity-Independent)')
    ax1.fill_between(m_chi, 1e-22, 1e-19, color='gray', alpha=0.3, label='CMB (Xu et al. 2018)')
    ax1.fill_between(m_chi, 1e-21, 1e-19, color='blue', alpha=0.2, label='Global 21 cm (EDGES/SARAS3)')
    ax1.fill_between(m_chi, 1e-23, 1e-19, color='green', alpha=0.2, label='Lyman-alpha Forest')
    ax1.axhline(opt_row['n0_1sig'], color='red', linestyle='-', linewidth=2, label='21 cm Forest 1-sigma (z=10)')
    ax1.axhline(opt_row['n0_2sig'], color='red', linestyle='--', linewidth=2, label='21 cm Forest 2-sigma (z=10)')
    ax1.legend(loc='lower right')
    ax1.grid(True, which='both', ls='--', alpha=0.5)
    ax2 = axes[1]
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlim(1e-3, 1e2)
    ax2.set_ylim(1e-44, 1e-38)
    ax2.set_xlabel('Dark Matter Mass m_chi [GeV]')
    ax2.set_ylabel('Cross-section / Mass sigma_0/m_chi [cm^2/GeV]')
    ax2.set_title('Exclusion Contours (n=-4, Coulomb-like)')
    ax2.fill_between(m_chi, 1e-41, 1e-38, color='gray', alpha=0.3, label='CMB')
    ax2.fill_between(m_chi, 1e-40, 1e-38, color='blue', alpha=0.2, label='Global 21 cm')
    ax2.axhline(opt_row['n4_1sig'], color='red', linestyle='-', linewidth=2, label='21 cm Forest 1-sigma (z=10)')
    ax2.axhline(opt_row['n4_2sig'], color='red', linestyle='--', linewidth=2, label='21 cm Forest 2-sigma (z=10)')
    ax2.legend(loc='lower right')
    ax2.grid(True, which='both', ls='--', alpha=0.5)
    plt.tight_layout()
    timestamp = int(time.time())
    filename = os.path.join(data_dir, "exclusion_contours_" + str(timestamp) + ".png")
    plt.savefig(filename, dpi=300)
    print("\nPlot saved to " + filename)

if __name__ == '__main__':
    generate_exclusion_contours()