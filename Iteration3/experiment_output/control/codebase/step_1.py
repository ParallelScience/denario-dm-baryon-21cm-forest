# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import numpy as np
import pandas as pd
import pickle
import os

def main():
    json_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    csv_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid_summary.csv'
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
    df_summary = pd.read_csv(csv_path)
    for record in grid_data:
        tau_arr = np.array(record['tau_arr'])
        cumulvec = np.array(record['cumulvec'])
        dN_dtau = -np.gradient(cumulvec, tau_arr)
        record['dN_dtau'] = dN_dtau.tolist()
    baselines = {}
    for record in grid_data:
        if record['f_cool'] == 1.0 and record['M_cut'] == 0.0:
            baselines[record['z']] = record['Nabs_total']
    for record in grid_data:
        z = record['z']
        n_abs = record['Nabs_total']
        n_abs_cdm = baselines[z]
        frac_change = (n_abs - n_abs_cdm) / n_abs_cdm if n_abs_cdm > 0 else 0
        record['frac_change_Nabs'] = frac_change
    sensitivity_S = {}
    m_cut_values_nonzero = [1e4, 1e5, 5e5, 1e6]
    for z in baselines.keys():
        n_abs_vals = []
        for m in m_cut_values_nonzero:
            for r in grid_data:
                if r['z'] == z and r['f_cool'] == 1.0 and r['M_cut'] == m:
                    n_abs_vals.append(r['Nabs_total'])
                    break
        ln_m = np.log(m_cut_values_nonzero)
        ln_n = np.log(np.maximum(n_abs_vals, 1e-10))
        S_vals = np.gradient(ln_n, ln_m)
        sensitivity_S[z] = {'M_cut': m_cut_values_nonzero, 'S': S_vals.tolist()}
    print('--- Baseline N_abs (CDM: f_cool=1.0, M_cut=0) ---')
    for z in sorted(baselines.keys()):
        print('Redshift ' + str(z) + ': N_abs = ' + str(round(baselines[z], 2)))
    print('\n--- Maximum Fractional Change Analysis ---')
    max_cooling_change = {}
    for z in baselines.keys():
        changes = []
        for r in grid_data:
            if r['z'] == z and r['M_cut'] == 0.0:
                changes.append(abs(r['frac_change_Nabs']))
        max_cooling_change[z] = max(changes)
    max_suppression_change = {}
    for z in baselines.keys():
        changes = []
        for r in grid_data:
            if r['z'] == z and r['f_cool'] == 1.0:
                changes.append(abs(r['frac_change_Nabs']))
        max_suppression_change[z] = max(changes)
    print('Redshift   | Max |Delta N/N| (Cooling) | Max |Delta N/N| (Suppression)')
    print('-' * 70)
    for z in sorted(baselines.keys()):
        print(str(z).ljust(10) + ' | ' + str(round(max_cooling_change[z], 6)).ljust(25) + ' | ' + str(round(max_suppression_change[z], 6)))
    print('\n--- Structural Sensitivity Index S = d ln N_abs / d ln M_cut (at f_cool=1.0) ---')
    for z in sorted(sensitivity_S.keys()):
        print('Redshift ' + str(z) + ':')
        for m, s in zip(sensitivity_S[z]['M_cut'], sensitivity_S[z]['S']):
            print('  M_cut = ' + str(m) + ' M_sun -> S = ' + str(round(s, 4)))
    output_path = 'data/processed_data_step1.pkl'
    processed_data = {'grid_data': grid_data, 'baselines': baselines, 'sensitivity_S': sensitivity_S, 'max_cooling_change': max_cooling_change, 'max_suppression_change': max_suppression_change}
    with open(output_path, 'wb') as f:
        pickle.dump(processed_data, f)
    print('\nProcessed data saved to ' + output_path)

if __name__ == '__main__':
    main()