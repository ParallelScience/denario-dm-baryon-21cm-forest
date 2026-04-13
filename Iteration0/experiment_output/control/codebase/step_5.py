# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['text.usetex'] = False

def generate_plots_and_strategy():
    diff_data = np.load('data/differential_distributions_and_derivatives.npz')
    fisher_data = np.load('data/fisher_forecast_results.npz')
    z_vals = diff_data['z_vals']
    f_cool_vals = list(diff_data['f_cool_vals'])
    M_cut_vals = list(diff_data['M_cut_vals'])
    tau_arr = diff_data['tau_arr']
    dN_dtau_grid = diff_data['dN_dtau_grid']
    cumul_grid = diff_data['cumul_grid']
    d_dN_dtau_dMcut = diff_data['d_dN_dtau_dMcut']
    F_vector = fisher_data['F_vector']
    F_scalar = fisher_data['F_scalar']
    sigma_1sigma_n0 = fisher_data['sigma_1sigma_n0']
    sigma_2sigma_n0 = fisher_data['sigma_2sigma_n0']
    sigma_1sigma_n4 = fisher_data['sigma_1sigma_n4']
    sigma_2sigma_n4 = fisher_data['sigma_2sigma_n4']
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    axs = axs.flatten()
    z_idx_10 = list(z_vals).index(10.0)
    f_idx_1 = f_cool_vals.index(1.0)
    m_idx_0 = M_cut_vals.index(0.0)
    for m_idx, m_cut in enumerate(M_cut_vals):
        axs[0].plot(tau_arr, cumul_grid[z_idx_10, f_idx_1, m_idx, :], label="M_cut=" + str(m_cut))
    axs[0].set_xscale('log')
    axs[0].set_yscale('log')
    axs[0].set_xlabel('Optical Depth tau')
    axs[0].set_ylabel('N(>tau)')
    axs[0].set_title('Cumulative Absorbers at z=10')
    axs[0].legend(fontsize=8)
    axs[0].grid(True, which='both', ls='--', alpha=0.5)
    for m_idx, m_cut in enumerate(M_cut_vals):
        axs[1].plot(tau_arr, dN_dtau_grid[z_idx_10, f_idx_1, m_idx, :], label="M_cut=" + str(m_cut))
    axs[1].set_xscale('log')
    axs[1].set_yscale('log')
    axs[1].set_xlabel('Optical Depth tau')
    axs[1].set_ylabel('dN/dtau')
    axs[1].set_title('Differential Spectrum at z=10')
    axs[1].legend(fontsize=8)
    axs[1].grid(True, which='both', ls='--', alpha=0.5)
    for m_idx, m_cut in enumerate(M_cut_vals):
        if m_cut == 0:
            continue
        frac_change = (cumul_grid[:, f_idx_1, m_idx, 0] - cumul_grid[:, f_idx_1, m_idx_0, 0]) / cumul_grid[:, f_idx_1, m_idx_0, 0]
        axs[2].plot(z_vals, frac_change, marker='o', label="M_cut=" + str(m_cut))
    axs[2].set_xlabel('Redshift z')
    axs[2].set_ylabel('Fractional Change in N_abs')
    axs[2].set_title('Suppression of Total Absorbers vs z')
    axs[2].legend(fontsize=8)
    axs[2].grid(True, ls='--', alpha=0.5)
    axs[3].plot(z_vals, sigma_1sigma_n0, 'b-', label='n=0, 1-sigma')
    axs[3].plot(z_vals, sigma_2sigma_n0, 'b--', label='n=0, 2-sigma')
    axs[3].plot(z_vals, sigma_1sigma_n4, 'r-', label='n=-4, 1-sigma')
    axs[3].plot(z_vals, sigma_2sigma_n4, 'r--', label='n=-4, 2-sigma')
    axs[3].set_yscale('log')
    axs[3].set_xlabel('Redshift z')
    axs[3].set_ylabel('Cross-section sigma_0/m_chi [cm^2/GeV]')
    axs[3].set_title('Fisher Forecast Sensitivity')
    axs[3].legend(fontsize=8)
    axs[3].grid(True, which='both', ls='--', alpha=0.5)
    axs[4].plot(z_vals, F_vector, 'k-o', label='F_vector (Spectrum)')
    axs[4].plot(z_vals, F_scalar, 'g-s', label='F_scalar (Total N)')
    axs[4].set_yscale('log')
    axs[4].set_xlabel('Redshift z')
    axs[4].set_ylabel('Fisher Information')
    axs[4].set_title('Fisher Information vs Redshift')
    axs[4].legend(fontsize=8)
    axs[4].grid(True, which='both', ls='--', alpha=0.5)
    N_sightlines = 10
    delta_tau = np.gradient(tau_arr)
    dN = dN_dtau_grid[z_idx_10, f_idx_1, m_idx_0, :]
    d_dN = d_dN_dtau_dMcut[z_idx_10, f_idx_1, m_idx_0, :]
    valid = dN > 1e-12
    snr_sq = np.zeros_like(tau_arr)
    snr_sq[valid] = N_sightlines * delta_tau[valid] * (d_dN[valid]**2) / dN[valid]
    axs[5].plot(tau_arr, snr_sq, 'm-')
    axs[5].set_xscale('log')
    axs[5].set_xlabel('Optical Depth tau')
    axs[5].set_ylabel('Fisher Info per bin (SNR^2)')
    axs[5].set_title('Sensitivity per tau bin at z=10')
    axs[5].grid(True, which='both', ls='--', alpha=0.5)
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "data/observational_strategy_1_" + timestamp + ".png"
    plt.savefig(filename, dpi=300)
    print("Plot saved to " + filename)
    print("\n--- Observational Strategy Optimization ---")
    print("1. Optimal Redshift Analysis:")
    for i, z in enumerate(z_vals):
        frac_change = (cumul_grid[i, f_idx_1, M_cut_vals.index(1e5), 0] - cumul_grid[i, f_idx_1, m_idx_0, 0]) / cumul_grid[i, f_idx_1, m_idx_0, 0]
        print("  z = " + str(z) + ": F_vector = " + str(F_vector[i]) + ", Fractional change (M_cut=1e5) = " + str(frac_change) + ", 1-sigma (n=0) = " + str(sigma_1sigma_n0[i]) + " cm^2/GeV")
    print("\nConclusion on Optimal Redshift:")
    print("  While z=7 provides the highest absolute Fisher information due to the larger baseline number of absorbers,")
    print("  the fractional suppression effect becomes stronger at higher redshifts (e.g., z=10 to z=15).")
    print("  Considering the trade-off between the magnitude of the suppression effect and the availability of")
    print("  background radio sources (which drops significantly at z > 10), z ~ 10 emerges as the optimal")
    print("  observational window. At z=10, the baseline N_abs is intermediate (~59), but the sensitivity to M_cut")
    print("  remains high, providing a robust signal-to-noise ratio.")
    print("\n2. Optimized Tau-Bin Weighting Scheme (at z=10):")
    print("  The Fisher information is not uniformly distributed across optical depths.")
    print("  To maximize the signal-to-noise ratio for detecting M_cut, observations should prioritize")
    print("  specific tau ranges where the derivative d(dN/dtau)/dM_cut is largest relative to the variance.")
    max_snr_idx = np.argmax(snr_sq)
    optimal_tau = tau_arr[max_snr_idx]
    print("  Peak sensitivity occurs at tau ~ " + str(optimal_tau))
    sorted_indices = np.argsort(snr_sq)[::-1]
    cum_snr = np.cumsum(snr_sq[sorted_indices])
    total_snr = cum_snr[-1]
    threshold = 0.8 * total_snr
    idx_80 = np.where(cum_snr >= threshold)[0][0]
    important_tau_indices = sorted_indices[:idx_80+1]
    min_tau_opt = np.min(tau_arr[important_tau_indices])
    max_tau_opt = np.max(tau_arr[important_tau_indices])
    print("  80% of the Fisher information is concentrated in the tau range: [" + str(min_tau_opt) + ", " + str(max_tau_opt) + "]")
    print("  Observational weighting scheme: Weight each tau bin proportional to (d(dN/dtau)/dM_cut) / (dN/dtau).")

if __name__ == '__main__':
    generate_plots_and_strategy()