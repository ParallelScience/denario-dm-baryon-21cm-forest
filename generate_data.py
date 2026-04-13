"""
Dataset generator: 21 cm forest observables under DM-baryon scattering
Using HAYASHI semianalytic framework

DM-baryon scattering has two effects:
1. Baryon cooling: T_k is reduced below the adiabatic value
2. Structure suppression: small-scale P(k) is suppressed -> fewer minihalos

We parameterize both effects over a grid and compute HAYASHI observables.
"""

import numpy as np
import os, sys, warnings, json, csv
warnings.filterwarnings('ignore')

sys.path.insert(0, '/opt/denario-venv/lib/python3.12/site-packages')

from hayashi.forest import Forest
from hayashi.cosmo import Tk_ad
from hayashi.lss import dndlnM_CDM

OUTPUT_DIR = "/home/node/work/projects/dm_baryon_21cm_forest/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================
# Grid parameters
# =============================================
redshifts     = [7.0, 8.0, 9.0, 10.0, 12.0, 15.0]
cooling_fracs = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02]   # T_k_DM / T_k_CDM
m_cut_list    = [0.0, 1e4, 1e5, 5e5, 1e6]            # M_cut in Solar masses

print("Starting HAYASHI grid computation...")
print(f"Grid: {len(redshifts)} z x {len(cooling_fracs)} f_cool x {len(m_cut_list)} M_cut")
print(f"Total: {len(redshifts)*len(cooling_fracs)*len(m_cut_list)} configurations\n")

results = []

for z in redshifts:
    Tk_cdm = float(Tk_ad(z))
    print(f"--- z={z:.1f}, Tk_CDM={Tk_cdm:.4f} K ---")

    for f_cool in cooling_fracs:
        Tk_dm = Tk_cdm * f_cool

        for M_cut in m_cut_list:
            try:
                if M_cut == 0.0:
                    forest = Forest(z, Tk_dm)
                else:
                    beta, gamma = 1.5, 2.0
                    Mc = float(M_cut)
                    def make_hmf(Mc_val):
                        def hmf_dm(M, zv):
                            supp = (1.0 + (Mc_val / M)**beta)**(-gamma)
                            return dndlnM_CDM(M, zv) * supp
                        return hmf_dm
                    forest = Forest(z, Tk_dm, dndlnM=make_hmf(Mc))

                # num_absorbers returns:
                # cumulvec[tt] = N(tau > tauvec[tt]), shape (200,)
                # dercumulvec  = d(cumulvec)/d(log tau), shape (199,) = cumulvec differences
                cumulvec, dercumulvec = forest.num_absorbers()
                tau_vec = forest.tauvec  # shape (200,)

                # N_abs total = cumulative count above tau_min
                tau_min = 0.01
                idx_min = np.searchsorted(tau_vec, tau_min)
                Nabs_total = float(cumulvec[idx_min]) if idx_min < len(cumulvec) else 0.0

                # Mean and peak tau from differential distribution
                # Use tau_vec[:-1] as x-axis for dercumulvec (size 199)
                tau_mid = tau_vec[:-1]
                dN = dercumulvec  # dN/d(log tau), can be negative; physical meaning is slope
                # For absorber distribution, use abs of dN (each bin contributes)
                dN_pos = np.maximum(-dN, 0.0)  # increasing Nabs as tau decreases -> dN/dtau > 0 in |dN|

                if np.any(dN_pos > 0):
                    norm = np.sum(dN_pos) + 1e-30
                    tau_mean = float(np.sum(tau_mid * dN_pos) / norm)
                    tau_peak = float(tau_mid[np.argmax(dN_pos)])
                else:
                    tau_mean = tau_peak = 0.0

                results.append({
                    'z': z, 'Tk_cdm': Tk_cdm, 'f_cool': f_cool,
                    'Tk_dm': Tk_dm, 'M_cut': M_cut,
                    'Nabs_total': Nabs_total, 'tau_mean': tau_mean, 'tau_peak': tau_peak,
                    'cumulvec': cumulvec.tolist(), 'tau_arr': tau_vec.tolist(),
                })
                print(f"  f_cool={f_cool:.2f} M_cut={M_cut:.0e}: Nabs={Nabs_total:.3f}, tau_mean={tau_mean:.4f}")

            except Exception as e:
                import traceback
                print(f"  ERROR f_cool={f_cool} M_cut={M_cut}: {e}")
                traceback.print_exc()
                results.append({
                    'z': z, 'Tk_cdm': Tk_cdm, 'f_cool': f_cool,
                    'Tk_dm': Tk_cdm*f_cool, 'M_cut': M_cut,
                    'Nabs_total': float('nan'), 'tau_mean': float('nan'), 'tau_peak': float('nan'),
                    'cumulvec': [], 'tau_arr': [],
                })

# Save full JSON
output_path = f"{OUTPUT_DIR}/hayashi_grid.json"
with open(output_path, 'w') as fp:
    json.dump(results, fp)
print(f"\nSaved {len(results)} points to {output_path}")

# CSV summary
csv_path = f"{OUTPUT_DIR}/hayashi_grid_summary.csv"
with open(csv_path, 'w', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=['z','Tk_cdm','f_cool','Tk_dm','M_cut','Nabs_total','tau_mean','tau_peak'])
    w.writeheader()
    for r in results:
        w.writerow({k: r[k] for k in ['z','Tk_cdm','f_cool','Tk_dm','M_cut','Nabs_total','tau_mean','tau_peak']})
print(f"Saved CSV to {csv_path}")

# Cumulative N(tau) arrays for z=10, M_cut=0 (pure cooling)
arrs = {}
for r in results:
    if r['z'] == 10.0 and r['M_cut'] == 0.0 and r['tau_arr']:
        key = f"fcool{r['f_cool']}"
        arrs[key+'_tau']    = np.array(r['tau_arr'])
        arrs[key+'_Ngtau']  = np.array(r['cumulvec'])
npz_path = f"{OUTPUT_DIR}/Ngtau_z10_Mcut0.npz"
if arrs:
    np.savez(npz_path, **arrs)
    print(f"Saved N(>tau) distributions to {npz_path}")

print("\nDone!")
