# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def compute_sensitivity_and_degeneracy():
    data_dir = '/home/node/work/projects/dm_baryon_21cm_forest/data/'
    df = pd.read_csv(os.path.join(data_dir, 'hayashi_grid_summary.csv'))
    with open(os.path.join(data_dir, 'hayashi_grid.json'), 'r') as f:
        grid_data = json.load(f)
    baselines = df[(df['f_cool'] == 1.0) & (df['M_cut'] == 0.0)].set_index('z')['Nabs_total']
    df['Delta_Nabs_frac'] = df.apply(lambda row: (row['Nabs_total'] - baselines[row['z']]) / baselines[row['z']], axis=1)
    df_mcut = df[df['f_cool'] == 1.0].pivot(index='z', columns='M_cut', values='Delta_Nabs_frac')
    df_fcool = df[df['M_cut'] == 0.0].pivot(index='z', columns='f_cool', values='Delta_Nabs_frac')
    print('--- Fractional Sensitivity to M_cut (f_cool=1.0) ---')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_mcut)
    print('\n--- Fractional Sensitivity to f_cool (M_cut=0.0) ---')
    print(df_fcool)
    df_mcut.to_csv('data/sensitivity_mcut.csv')
    df_fcool.to_csv('data/sensitivity_fcool.csv')
    vectors = {}
    for record in grid_data:
        if record['f_cool'] == 1.0:
            z = record['z']
            mcut = record['M_cut']
            tau_arr = np.array(record['tau_arr'])
            cumulvec = np.array(record['cumulvec'])
            dN_dtau = -np.gradient(cumulvec, tau_arr)
            norm = np.linalg.norm(dN_dtau)
            if norm > 0:
                v = dN_dtau / norm
            else:
                v = np.zeros_like(dN_dtau)
            vectors[(z, mcut)] = v
    keys = sorted(vectors.keys())
    n = len(keys)
    sim_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            sim_matrix[i, j] = np.dot(vectors[keys[i]], vectors[keys[j]])
    idx = ['z=' + str(k[0]) + ',M=' + str(k[1]) for k in keys]
    df_sim = pd.DataFrame(sim_matrix, index=idx, columns=idx)
    print('\n--- Shape Similarity (Cosine) to quantify degeneracy between M_cut and z ---')
    mcuts = sorted(list(set([k[1] for k in keys])))
    zs = sorted(list(set([k[0] for k in keys])))
    deg_matrix_7 = np.zeros((len(mcuts), len(zs)))
    for i, m in enumerate(mcuts):
        for j, z in enumerate(zs):
            deg_matrix_7[i, j] = np.dot(vectors[(7.0, m)], vectors[(z, 0.0)])
    df_deg_7 = pd.DataFrame(deg_matrix_7, index=['M_cut=' + str(m) for m in mcuts], columns=['z=' + str(z) for z in zs])
    print('Comparing (z=7, M_cut) against (z, M_cut=0):')
    print(df_deg_7)
    deg_matrix_10 = np.zeros((len(mcuts), len(zs)))
    for i, m in enumerate(mcuts):
        for j, z in enumerate(zs):
            deg_matrix_10[i, j] = np.dot(vectors[(10.0, m)], vectors[(z, 0.0)])
    df_deg_10 = pd.DataFrame(deg_matrix_10, index=['M_cut=' + str(m) for m in mcuts], columns=['z=' + str(z) for z in zs])
    print('\nComparing (z=10, M_cut) against (z, M_cut=0):')
    print(df_deg_10)
    df_sim.to_csv('data/shape_similarity_matrix.csv')
    print('\nSensitivity matrices and similarity matrix saved to data/')
    plt.rcParams['text.usetex'] = False
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sns.heatmap(df_mcut, annot=True, fmt='.3f', cmap='coolwarm', ax=axes[0], cbar_kws={'label': 'Delta N_abs / N_abs'})
    axes[0].set_title('Fractional Sensitivity to M_cut (f_cool=1.0)')
    axes[0].set_xlabel('M_cut [M_sun]')
    axes[0].set_ylabel('Redshift z')
    sns.heatmap(df_fcool, annot=True, fmt='.4f', cmap='coolwarm', ax=axes[1], cbar_kws={'label': 'Delta N_abs / N_abs'})
    axes[1].set_title('Fractional Sensitivity to f_cool (M_cut=0)')
    axes[1].set_xlabel('f_cool')
    axes[1].set_ylabel('Redshift z')
    plt.tight_layout()
    plot_filename = 'data/fractional_sensitivity_heatmap_1_' + timestamp + '.png'
    plt.savefig(plot_filename, dpi=300)
    print('Heatmap saved to ' + plot_filename)
    plt.close()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df_deg_7, annot=True, fmt='.4f', cmap='viridis', ax=ax, cbar_kws={'label': 'Cosine Similarity'})
    ax.set_title('Shape Similarity: (z=7, M_cut) vs (z, M_cut=0)')
    ax.set_xlabel('Baseline at Redshift z')
    ax.set_ylabel('M_cut at z=7 [M_sun]')
    plt.tight_layout()
    plot_filename2 = 'data/shape_similarity_degeneracy_2_' + timestamp + '.png'
    plt.savefig(plot_filename2, dpi=300)
    print('Shape similarity plot saved to ' + plot_filename2)
    plt.close()

if __name__ == '__main__':
    compute_sensitivity_and_degeneracy()