# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import json
import numpy as np
import os

def validate_and_summarize_data(csv_path, json_path, output_path):
    df_summary = pd.read_csv(csv_path)
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
    print("--- CDM Baseline Values (f_cool=1.0, M_cut=0) ---")
    cdm_baseline = df_summary[(df_summary['f_cool'] == 1.0) & (df_summary['M_cut'] == 0.0)].copy()
    cdm_baseline = cdm_baseline.sort_values('z')
    for _, row in cdm_baseline.iterrows():
        print("z = " + str(row['z']) + ", Tk_cdm = " + str(row['Tk_cdm']) + " K, Nabs_total = " + str(row['Nabs_total']))
    print("\n--- Verifying cumulvec arrays ---")
    all_monotonic = True
    tau_min_all = []
    tau_max_all = []
    for record in grid_data:
        cumulvec = np.array(record['cumulvec'])
        tau_arr = np.array(record['tau_arr'])
        if not np.all(np.diff(cumulvec) <= 0):
            all_monotonic = False
        tau_min_all.append(tau_arr.min())
        tau_max_all.append(tau_arr.max())
    if all_monotonic:
        print("All cumulvec arrays are monotonically decreasing.")
    else:
        print("WARNING: Not all cumulvec arrays are monotonically decreasing.")
    print("Tau range across all records: min ~ " + str(np.min(tau_min_all)) + ", max ~ " + str(np.max(tau_max_all)))
    df_summary.to_csv(output_path, index=False)
    print("\nValidated full grid summary saved to " + output_path)

if __name__ == '__main__':
    csv_file = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid_summary.csv'
    json_file = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    out_file = 'data/validated_hayashi_grid_summary.csv'
    validate_and_summarize_data(csv_file, json_file, out_file)