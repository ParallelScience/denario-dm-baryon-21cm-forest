# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib

matplotlib.rcParams['text.usetex'] = False

def main():
    data_dir = 'data/'
    data_path = os.path.join(data_dir, 'processed_data_step3.pkl')
    if not os.path.exists(data_path):
        data_path = os.path.join(data_dir, 'processed_data_step1.pkl')
        
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
        
    grid_data = data['grid_data']
    zs = sorted(list(set([r['z'] for r in grid_data])))
    
    fisher_results = {}
    
    print('--- Fisher Forecast Setup ---')
    print('Parameters: theta = {M_cut, f_cool [proxy for J_21], x_HI}')
    print('Priors: sigma(f_cool) = 0.2, sigma(x_HI) = 0.1')
    print('Source density: N_los(z) = 10 * ((1+z)/8)^(-2.5)')
    print('--------------------------------------------------\n')
    
    for z in zs:
        r_cdm = next((r for r in grid_data if r['z'] == z and r['M_cut'] == 0.0 and r['f_cool'] == 1.0), None)
        r_mcut = next((r for r in grid_data if r['z'] == z and r['M_cut'] == 10000.0 and r['f_cool'] == 1.0), None)
        r_fcool = next((r for r in grid_data if r['z'] == z and r['M_cut'] == 0.0 and r['f_cool'] == 0.5), None)
        
        if not r_cdm or not r_mcut or not r_fcool:
            print('Missing data for redshift ' + str(z) + ', skipping.')
            continue
            
        c_cdm = np.array(r_cdm['cumulvec'])
        c_mcut = np.array(r_mcut['cumulvec'])
        c_fcool = np.array(r_fcool['cumulvec'])
        
        dN_cdm = np.maximum(c_cdm[:-1] - c_cdm[1:], 0)
        dN_mcut = np.maximum(c_mcut[:-1] - c_mcut[1:], 0)
        dN_fcool = np.maximum(c_fcool[:-1] - c_fcool[1:], 0)
        
        alpha = 2.5
        N_los = 10.0 * ((1.0 + z) / 8.0)**(-alpha)
        x_HI = 1.0
        
        n_i = N_los * x_HI * dN_cdm
        
        dn_dMcut = N_los * x_HI * (dN_mcut - dN_cdm) / 10000.0
        dn_dfcool = N_los * x_HI * (dN_fcool - dN_cdm) / (0.5 - 1.0)
        dn_dxHI = N_los * dN_cdm
        
        F = np.zeros((3, 3))
        for i in range(len(n_i)):
            if n_i[i] > 1e-10:
                derivs = np.array([dn_dMcut[i], dn_dfcool[i], dn_dxHI[i]])
                F += np.outer(derivs, derivs) / n_i[i]
                
        F[1, 1] += 1.0 / (0.2**2)
        F[2, 2] += 1.0 / (0.1**2)
        
        try:
            C = np.linalg.inv(F)
            sigma_Mcut = np.sqrt(max(C[0, 0], 0))
        except np.linalg.LinAlgError:
            C = np.full((3, 3), np.nan)
            sigma_Mcut = np.nan
            
        fisher_results[z] = {
            'N_los': N_los,
            'F': F,
            'C': C,
            'sigma_Mcut': sigma_Mcut
        }
        
        print('Redshift z = ' + str(z))
        print('N_los(z) = ' + str(round(N_los, 2)))
        print('Fisher Matrix F:')
        print(np.array2string(F, precision=4, suppress_small=True))
        print('Covariance Matrix C = F^-1:')
        print(np.array2string(C, precision=4, suppress_small=True))
        print('Marginalized 1-sigma uncertainty on M_cut: ' + str(round(sigma_Mcut, 2)) + ' M_sun\n')
        
    best_z = None
    min_sigma = float('inf')
    for z in fisher_results:
        if fisher_results[z]['sigma_Mcut'] < min_sigma:
            min_sigma = fisher_results[z]['sigma_Mcut']
            best_z = z
            
    print('--- Optimal Observational Window ---')
    print('Optimal redshift for constraining M_cut: z = ' + str(best_z) + ' with sigma(M_cut) = ' + str(round(min_sigma, 2)) + ' M_sun\n')
    
    zs_plot = sorted(list(fisher_results.keys()))
    sigma_mcut_plot = [fisher_results[z]['sigma_Mcut'] for z in zs_plot]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(zs_plot, sigma_mcut_plot, marker='o', linestyle='-', color='b', linewidth=2, markersize=8)
    ax.set_xlabel('Redshift z')
    ax.set_ylabel('Marginalized 1-sigma Uncertainty sigma(M_cut) [M_sun]')
    ax.set_title('Fisher Forecast: Sensitivity to M_cut vs Redshift')
    ax.grid(True, which='both', ls='--', alpha=0.7)
    
    if best_z is not None:
        ax.annotate('Optimal Window\nz=' + str(best_z) + ', sigma=' + str(int(min_sigma)), 
                    xy=(best_z, min_sigma), xytext=(best_z, min_sigma * 1.2),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                    ha='center')
                    
    fig.tight_layout()
    plot_path = os.path.join(data_dir, 'fisher_sigma_Mcut_vs_z_1_' + timestamp + '.png')
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)
    print('Plot saved to ' + plot_path)
    
    data['fisher_results'] = fisher_results
    output_path = os.path.join(data_dir, 'processed_data_step4.pkl')
    with open(output_path, 'wb') as f:
        pickle.dump(data, f)
    print('Fisher forecast results saved to ' + output_path)

if __name__ == '__main__':
    main()