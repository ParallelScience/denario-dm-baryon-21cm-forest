# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import json

def compute_sensitivity_and_nuisance():
    data_dir = 'data/'
    csv_path = os.path.join(data_dir, 'hayashi_grid_summary.csv')
    json_path = os.path.join(data_dir, 'hayashi_grid.json')
    
    df = pd.read_csv(csv_path)
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
        
    print('=====================================================================')
    print('1. FRACTIONAL CHANGE IN N_abs (Delta N_abs / N_abs)')
    print('=====================================================================')
    
    results_mcut = []
    results_fcool = []
    
    for z in sorted(df['z'].unique()):
        baseline = df[(df['z'] == z) & (df['f_cool'] == 1.0) & (df['M_cut'] == 0.0)].iloc[0]['Nabs_total']
        
        for mcut in sorted(df['M_cut'].unique()):
            if mcut == 0.0: continue
            row = df[(df['z'] == z) & (df['f_cool'] == 1.0) & (df['M_cut'] == mcut)]
            if not row.empty:
                nabs = row.iloc[0]['Nabs_total']
                frac = (nabs - baseline) / baseline
                results_mcut.append({'z': z, 'M_cut': mcut, 'Nabs': nabs, 'frac_change': frac})
                
        for fcool in sorted(df['f_cool'].unique(), reverse=True):
            if fcool == 1.0: continue
            row = df[(df['z'] == z) & (df['f_cool'] == fcool) & (df['M_cut'] == 0.0)]
            if not row.empty:
                nabs = row.iloc[0]['Nabs_total']
                frac = (nabs - baseline) / baseline
                results_fcool.append({'z': z, 'f_cool': fcool, 'Nabs': nabs, 'frac_change': frac})
                
    df_mcut = pd.DataFrame(results_mcut)
    df_fcool = pd.DataFrame(results_fcool)
    
    print('\n--- Structure Suppression (M_cut) Effect [f_cool=1.0] ---')
    for z in sorted(df_mcut['z'].unique()):
        print('z = ' + str(z) + ':')
        sub = df_mcut[df_mcut['z'] == z]
        for _, row in sub.iterrows():
            print('  M_cut = ' + str(row['M_cut']) + ' M_sun -> Delta N/N = ' + str(round(row['frac_change'], 4)) + ' (N_abs = ' + str(round(row['Nabs'], 2)) + ')')
            
    print('\n--- Baryon Cooling (f_cool) Effect [M_cut=0] ---')
    for z in sorted(df_fcool['z'].unique()):
        print('z = ' + str(z) + ':')
        sub = df_fcool[df_fcool['z'] == z]
        for _, row in sub.iterrows():
            print('  f_cool = ' + str(row['f_cool']) + ' -> Delta N/N = ' + str(round(row['frac_change'], 4)) + ' (N_abs = ' + str(round(row['Nabs'], 2)) + ')')
            
    df_mcut.to_csv(os.path.join(data_dir, 'sensitivity_mcut.csv'), index=False)
    df_fcool.to_csv(os.path.join(data_dir, 'sensitivity_fcool.csv'), index=False)
    print('\nSaved fractional change data to data/sensitivity_mcut.csv and data/sensitivity_fcool.csv')
    
    print('\n=====================================================================')
    print('2. ASTROPHYSICAL NUISANCE MODELING & FISHER FORECAST')
    print('=====================================================================')
    
    z_list = sorted(list(set([d['z'] for d in grid_data])))
    fisher_results = []
    
    for z in z_list:
        d_base = next(d for d in grid_data if d['z'] == z and d['f_cool'] == 1.0 and d['M_cut'] == 0.0)
        tau_arr = np.array(d_base['tau_arr'])
        cumul_base = np.array(d_base['cumulvec'])
        delta_N_base = -np.diff(cumul_base)
        
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
                F[i, j] = 10.0 * np.sum((derivatives[i][valid] * derivatives[j][valid]) / delta_N_base[valid])
                
        P = np.zeros((3, 3))
        P[1, 1] = 1.0 / (0.1**2)
        P[2, 2] = 1.0 / (0.1**2)
        
        F_tot = F + P
        
        try:
            Cov = np.linalg.inv(F_tot)
            sigma_Mcut_marg = np.sqrt(Cov[0, 0])
            sigma_Mcut_unmarg = np.sqrt(1.0 / F[0, 0]) if F[0, 0] > 0 else np.inf
            degradation = sigma_Mcut_marg / sigma_Mcut_unmarg if sigma_Mcut_unmarg > 0 else np.inf
        except np.linalg.LinAlgError:
            sigma_Mcut_marg = np.inf
            sigma_Mcut_unmarg = np.inf
            degradation = np.inf
            
        fisher_results.append({'z': z, 'sigma_Mcut_unmarg': sigma_Mcut_unmarg, 'sigma_Mcut_marg': sigma_Mcut_marg, 'degradation_factor': degradation})
        
    df_fisher = pd.DataFrame(fisher_results)
    print('\n--- Degradation of M_cut constraint due to astrophysical degeneracies ---')
    for _, row in df_fisher.iterrows():
        print('z = ' + str(row['z']) + ': Unmarginalized sigma(M_cut) = ' + str(round(row['sigma_Mcut_unmarg'], 2)) + ' M_sun, ' + 'Marginalized sigma(M_cut) = ' + str(round(row['sigma_Mcut_marg'], 2)) + ' M_sun, ' + 'Degradation Factor = ' + str(round(row['degradation_factor'], 2)) + 'x')
              
    df_fisher.to_csv(os.path.join(data_dir, 'nuisance_degradation.csv'), index=False)
    print('\nSaved nuisance degradation results to data/nuisance_degradation.csv')

if __name__ == '__main__':
    compute_sensitivity_and_nuisance()