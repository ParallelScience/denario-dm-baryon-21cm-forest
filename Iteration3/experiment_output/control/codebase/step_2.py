# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib

matplotlib.rcParams['text.usetex'] = False

def compute_kl_divergence(p, q):
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    p = np.maximum(p, 0)
    q = np.maximum(q, 0)
    p_sum = np.sum(p)
    q_sum = np.sum(q)
    if p_sum == 0 or q_sum == 0:
        return np.nan
    p_norm = p / p_sum
    q_norm = q / q_sum
    epsilon = 1e-12
    p_safe = np.where(p_norm > epsilon, p_norm, epsilon)
    q_safe = np.where(q_norm > epsilon, q_norm, epsilon)
    return np.sum(p_safe * np.log(p_safe / q_safe))

def main():
    data_path = 'data/processed_data_step1.pkl'
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    grid_data = data['grid_data']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    z_target = 10.0
    records_z10_mcut = [r for r in grid_data if r['z'] == z_target and r['f_cool'] == 1.0]
    records_z10_mcut.sort(key=lambda x: x['M_cut'])
    m_cuts = [r['M_cut'] for r in records_z10_mcut]
    tau_arr = np.array(records_z10_mcut[0]['tau_arr'])
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for r in records_z10_mcut:
        label = 'CDM' if r['M_cut'] == 0 else 'M_cut=' + str(r['M_cut'])
        axes[0].plot(tau_arr, r['cumulvec'], label=label)
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Optical Depth tau')
    axes[0].set_ylabel('Cumulative Absorbers N(>tau)')
    axes[0].set_title('Varying M_cut (z=' + str(z_target) + ', f_cool=1.0)')
    axes[0].legend()
    axes[0].grid(True, which='both', ls='--', alpha=0.5)
    records_z10_fcool = [r for r in grid_data if r['z'] == z_target and r['M_cut'] == 0.0]
    records_z10_fcool.sort(key=lambda x: x['f_cool'], reverse=True)
    for r in records_z10_fcool:
        label = 'f_cool=' + str(r['f_cool'])
        axes[1].plot(tau_arr, r['cumulvec'], label=label)
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('Optical Depth tau')
    axes[1].set_ylabel('Cumulative Absorbers N(>tau)')
    axes[1].set_title('Varying f_cool (z=' + str(z_target) + ', M_cut=0)')
    axes[1].legend()
    axes[1].grid(True, which='both', ls='--', alpha=0.5)
    m_cuts_nonzero = [m for m in m_cuts if m > 0]
    cumulvecs_nonzero = np.array([r['cumulvec'] for r in records_z10_mcut if r['M_cut'] > 0])
    if len(m_cuts_nonzero) > 1:
        dN_dM = np.gradient(cumulvecs_nonzero, m_cuts_nonzero, axis=0)
        for i, m in enumerate(m_cuts_nonzero):
            axes[2].plot(tau_arr, dN_dM[i], label='M_cut=' + str(m))
    axes[2].set_xscale('log')
    axes[2].set_xlabel('Optical Depth tau')
    axes[2].set_ylabel('Derivative dN(>tau) / dM_cut')
    axes[2].set_title('Sensitivity to M_cut (z=' + str(z_target) + ')')
    axes[2].legend()
    axes[2].grid(True, which='both', ls='--', alpha=0.5)
    fig.tight_layout()
    plot1_path = 'data/N_tau_and_derivative_1_' + timestamp + '.png'
    fig.savefig(plot1_path, dpi=300)
    plt.close(fig)
    print('Plot saved to ' + plot1_path)
    zs = sorted(list(set([r['z'] for r in grid_data])))
    m_cuts_nonzero_all = sorted(list(set([r['M_cut'] for r in grid_data if r['M_cut'] > 0])))
    kl_divs = {m: [] for m in m_cuts_nonzero_all}
    for z in zs:
        cdm_record = next((r for r in grid_data if r['z'] == z and r['f_cool'] == 1.0 and r['M_cut'] == 0.0), None)
        if cdm_record is None:
            for m in m_cuts_nonzero_all:
                kl_divs[m].append(np.nan)
            continue
        p = np.array(cdm_record['dN_dtau'])
        for m in m_cuts_nonzero_all:
            m_record = next((r for r in grid_data if r['z'] == z and r['f_cool'] == 1.0 and r['M_cut'] == m), None)
            if m_record is None:
                kl_divs[m].append(np.nan)
            else:
                q = np.array(m_record['dN_dtau'])
                kl = compute_kl_divergence(p, q)
                kl_divs[m].append(kl)
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    for m in m_cuts_nonzero_all:
        ax2.plot(zs, kl_divs[m], marker='o', label='M_cut=' + str(m))
    ax2.set_xlabel('Redshift z')
    ax2.set_ylabel('KL Divergence D_KL(CDM || M_cut)')
    ax2.set_title('Distinguishability of Structure Suppression from CDM')
    ax2.legend()
    ax2.grid(True, ls='--', alpha=0.5)
    fig2.tight_layout()
    plot2_path = 'data/KL_divergence_2_' + timestamp + '.png'
    fig2.savefig(plot2_path, dpi=300)
    plt.close(fig2)
    print('Plot saved to ' + plot2_path)
    m_cuts_all = sorted(list(set([r['M_cut'] for r in grid_data])))
    frac_change_matrix = np.zeros((len(zs), len(m_cuts_all)))
    for i, z in enumerate(zs):
        for j, m in enumerate(m_cuts_all):
            record = next((r for r in grid_data if r['z'] == z and r['f_cool'] == 1.0 and r['M_cut'] == m), None)
            if record is not None:
                frac_change_matrix[i, j] = record['frac_change_Nabs']
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    cax = ax3.imshow(frac_change_matrix, aspect='auto', cmap='viridis', origin='lower')
    ax3.set_xticks(np.arange(len(m_cuts_all)))
    ax3.set_xticklabels([str(m) for m in m_cuts_all])
    ax3.set_yticks(np.arange(len(zs)))
    ax3.set_yticklabels([str(z) for z in zs])
    ax3.set_xlabel('M_cut [M_sun]')
    ax3.set_ylabel('Redshift z')
    ax3.set_title('Fractional Change in N_abs relative to CDM (f_cool=1.0)')
    cbar = fig3.colorbar(cax)
    cbar.set_label('Delta N_abs / N_abs_CDM')
    for i in range(len(zs)):
        for j in range(len(m_cuts_all)):
            val = frac_change_matrix[i, j]
            text_color = 'white' if val < -0.5 else 'black'
            ax3.text(j, i, str(round(val, 2)), ha='center', va='center', color=text_color)
    fig3.tight_layout()
    plot3_path = 'data/frac_change_heatmap_3_' + timestamp + '.png'
    fig3.savefig(plot3_path, dpi=300)
    plt.close(fig3)
    print('Plot saved to ' + plot3_path)
    print('\n--- Key Statistics for Researcher ---')
    print('KL Divergence D_KL(CDM || M_cut) across redshifts:')
    header = 'Redshift | ' + ' | '.join(['M_cut=' + str(m) for m in m_cuts_nonzero_all])
    print(header)
    print('-' * len(header))
    for i, z in enumerate(zs):
        row = str(z).ljust(8) + ' | '
        row += ' | '.join([str(round(kl_divs[m][i], 4)).ljust(12) for m in m_cuts_nonzero_all])
        print(row)
    print('\nFractional Change in N_abs (Delta N / N_CDM) across redshifts:')
    header2 = 'Redshift | ' + ' | '.join(['M_cut=' + str(m) for m in m_cuts_all])
    print(header2)
    print('-' * len(header2))
    for i, z in enumerate(zs):
        row = str(z).ljust(8) + ' | '
        row += ' | '.join([str(round(frac_change_matrix[i, j], 4)).ljust(12) for j in range(len(m_cuts_all))])
        print(row)

if __name__ == '__main__':
    main()