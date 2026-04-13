# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import json
import matplotlib.pyplot as plt
import numpy as np
import time
import os

def plot_N_tau_curves():
    json_path = '/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'
    with open(json_path, 'r') as f:
        grid_data = json.load(f)
    target_z = 10.0
    panel1_data = [d for d in grid_data if d['z'] == target_z and d['f_cool'] == 1.0]
    panel1_data = sorted(panel1_data, key=lambda x: x['M_cut'])
    panel2_data = [d for d in grid_data if d['z'] == target_z and d['M_cut'] == 0.0]
    panel2_data = sorted(panel2_data, key=lambda x: x['f_cool'], reverse=True)
    plt.rcParams['text.usetex'] = False
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax1 = axes[0]
    for d in panel1_data:
        m_cut = d['M_cut']
        label = "CDM (M_cut=0)" if m_cut == 0 else "M_cut = " + str(m_cut) + " M_sun"
        ax1.plot(d['tau_arr'], d['cumulvec'], label=label)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Optical Depth (tau)')
    ax1.set_ylabel('Cumulative Number of Absorbers N(>tau)')
    ax1.set_title('Effect of Structure Suppression (z=10, f_cool=1.0)')
    ax1.legend()
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax2 = axes[1]
    for d in panel2_data:
        f_cool = d['f_cool']
        label = "CDM (f_cool=1.0)" if f_cool == 1.0 else "f_cool = " + str(f_cool)
        ax2.plot(d['tau_arr'], d['cumulvec'], label=label)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Optical Depth (tau)')
    ax2.set_ylabel('Cumulative Number of Absorbers N(>tau)')
    ax2.set_title('Effect of Baryon Cooling (z=10, M_cut=0)')
    ax2.legend()
    ax2.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    timestamp = int(time.time())
    filename = os.path.join("data", "N_tau_curves_1_" + str(timestamp) + ".png")
    plt.savefig(filename, dpi=300)
    print("Plot saved to " + filename)
    print("\n--- Quantitative Summary of N(>tau=0.01) at z=10 ---")
    print("Panel 1: Effect of Structure Suppression (f_cool=1.0)")
    for d in panel1_data:
        print("M_cut = " + str(d['M_cut']) + " M_sun: N_abs = " + str(d['Nabs_total']))
    print("\nPanel 2: Effect of Baryon Cooling (M_cut=0.0)")
    for d in panel2_data:
        print("f_cool = " + str(d['f_cool']) + ": N_abs = " + str(d['Nabs_total']))

if __name__ == '__main__':
    plot_N_tau_curves()