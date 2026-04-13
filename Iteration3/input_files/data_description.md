
# DM-Baryon Scattering and the 21 cm Forest: A Semianalytic Study

## Scientific Context

Dark matter–baryon scattering is a well-motivated extension of the standard cosmological model. If dark matter (DM) couples to baryons via a velocity-dependent or velocity-independent cross-section (parameterized as σ(v) = σ₀ v^n, with n=0 velocity-independent or n=-4 Coulomb-like), two physical effects modify the 21 cm forest:

1. **Baryon cooling**: DM-baryon heat transfer reduces the IGM kinetic temperature T_k below the adiabatic value T_k^{ad}(z). This is parameterized here by the cooling fraction f_cool = T_k / T_k^{ad} ∈ (0, 1], where f_cool=1 corresponds to CDM (no interaction).

2. **Structure suppression**: DM-baryon scattering suppresses small-scale power in the matter power spectrum, reducing minihalo abundance. This is parameterized by an effective half-mode mass cutoff M_cut [Solar masses], where M_cut=0 is CDM and M_cut > 0 represents a suppression of halos below M_cut following a transfer function T(M) = (1 + (M_cut/M)^1.5)^{-2}.

The 21 cm forest refers to absorption lines in the spectra of high-redshift radio sources caused by intervening neutral hydrogen minihalos and the diffuse IGM during the Epoch of Reionization (z ~ 7–15). Each absorber produces an absorption trough at 21 cm rest frequency with optical depth τ. The key observable is the cumulative number of absorbers N(>τ) per unit redshift and per unit frequency.

**Key literature context**: 
- arXiv:2212.08409 (Shimabukuro et al. 2023): studied DM-baryon *streaming velocity* effect on 21 cm forest — NOTE: this is a kinematic effect different from our interaction cross-section effect.
- arXiv:2505.03148 (Parashari et al. 2026): studied DM-baryon scattering in the *global* 21 cm signal — NOT the 21 cm forest.
- arXiv:2209.01305 (Villanueva-Domingo et al. 2023): HAYASHI code paper, subhalo boosting of 21 cm forest.

**The gap we fill**: No existing paper has computed the 21 cm forest absorption line statistics under DM-baryon interaction cross-sections using the semianalytic framework. This is the first such study.

## Dataset Description

### Computation Tool
Computed using HAYASHI (v1.1.6), a Python semianalytic code for 21 cm forest calculations that integrates halo mass functions over mass and impact parameter. It includes host halo + subhalo contributions. GitHub: https://github.com/PabloVD/HAYASHI

### File Inventory

#### Primary data file (full grid):
- **Path**: `/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json`
- **Format**: JSON list of 180 dictionaries, one per grid point
- **Size**: 180 records
- **Fields per record**:
  - `z` (float): Redshift. Values: [7.0, 8.0, 9.0, 10.0, 12.0, 15.0]
  - `Tk_cdm` (float): Adiabatic IGM temperature in Kelvin (CDM baseline). Values: ~1.16 K (z=7) to ~4.63 K (z=15)
  - `f_cool` (float): Cooling fraction T_k/T_k_CDM. Values: [1.0, 0.5, 0.2, 0.1, 0.05, 0.02]
  - `Tk_dm` (float): Modified IGM temperature T_k_CDM * f_cool [K]
  - `M_cut` (float): Structure suppression cutoff mass [Solar masses]. Values: [0, 1e4, 1e5, 5e5, 1e6]
  - `Nabs_total` (float): Cumulative number of absorbers N(τ > τ_min=0.01) per unit redshift per line of sight [dimensionless]
  - `tau_mean` (float): Mean optical depth of the absorber distribution [dimensionless]
  - `tau_peak` (float): Modal optical depth of the absorber distribution [dimensionless]
  - `cumulvec` (list of 200 floats): N(>τ) cumulative distribution as a function of τ
  - `tau_arr` (list of 200 floats): Corresponding τ values (logarithmically spaced, ~0.001 to ~0.5)

#### CSV summary (for easy analysis):
- **Path**: `/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid_summary.csv`
- **Format**: CSV with columns: z, Tk_cdm, f_cool, Tk_dm, M_cut, Nabs_total, tau_mean, tau_peak
- **Size**: 180 rows + header

#### N(>τ) distributions for z=10, M_cut=0 (pure cooling effect):
- **Path**: `/home/node/work/projects/dm_baryon_21cm_forest/data/Ngtau_z10_Mcut0.npz`
- **Format**: NumPy .npz archive
- **Arrays**: For each cooling fraction value fcool ∈ {1.0, 0.5, 0.2, 0.1, 0.05, 0.02}:
  - `fcool{X}_tau`: τ array (200 values, log-spaced)
  - `fcool{X}_Ngtau`: N(>τ) array (200 values)

### Key Physical Findings from the Dataset

**Finding 1 — Structure suppression is dominant**: At all redshifts z=7–15, M_cut has a large effect on N_abs. Example at z=7: N_abs = 136 (CDM, M_cut=0) vs. 28 (M_cut=10^5 M_sun) vs. 10 (M_cut=10^6 M_sun). This is a factor of 3–14x suppression.

**Finding 2 — Baryon cooling is negligible at z<15**: At z=7–15, reducing f_cool from 1.0 to 0.02 changes N_abs by <1%. This is because the adiabatic T_k is already near the floor (1–5 K), so further cooling has minimal effect on the 21 cm optical depth. The spin temperature coupling saturates in the cold IGM limit.

**Finding 3 — Strong redshift dependence of structure suppression**: The ratio N_abs(M_cut=10^5)/N_abs(CDM) varies from ~20% at z=7 to ~14% at z=15, showing that structure suppression is more prominent at higher z (less structure formed, halos are closer to M_cut).

**Finding 4 — Redshift evolution of baseline N_abs**: N_abs(CDM, M_cut=0) decreases from 136 at z=7 to 13 at z=15, reflecting the declining halo abundance at higher z.

### Physical Mapping to DM-Baryon Parameters

The M_cut parameter maps to physical DM-baryon scattering as follows (approximate, from literature):

For velocity-independent cross-section (n=0):
- M_cut ~ 10^4 M_sun → σ₀/m_χ ~ few × 10^{-25} cm²/GeV (mild scattering)
- M_cut ~ 10^5 M_sun → σ₀/m_χ ~ 10^{-24} cm²/GeV (moderate scattering)
- M_cut ~ 10^6 M_sun → σ₀/m_χ ~ 10^{-23} cm²/GeV (strong scattering)

For Coulomb-like (n=-4), the mapping is more redshift-dependent due to the velocity-weighting.

The cooling fraction f_cool maps to:
- f_cool = 0.5 → σ₀/m_χ ~ 10^{-24} cm²/GeV (for light DM, m_χ ~ 0.1 GeV)
- f_cool = 0.1 → σ₀/m_χ ~ 10^{-23} cm²/GeV

## Analysis Tasks

The analysis should:

1. **Visualize the 21 cm forest signal**: Plot N(>τ) curves for different (z, f_cool, M_cut) combinations. Show how structure suppression and cooling modify the cumulative absorber count.

2. **Quantify the sensitivity**: Compute the fractional change ΔN_abs/N_abs as a function of M_cut and f_cool, for each redshift. Show that structure suppression (M_cut) is the dominant effect, while cooling is subdominant.

3. **Map to DM-baryon interaction parameters**: Using the physical mapping above, compute N_abs as a function of σ₀/m_χ for Coulomb-like and velocity-independent interactions. Derive sensitivity curves showing what cross-sections are detectable given a 10% or 20% change in N_abs (observationally motivated threshold).

4. **Fisher forecast for SKA sensitivity**: Using a simplified Fisher analysis, estimate the sensitivity of SKA observations of N_abs (expected ~100 absorbers at z~7 for CDM) to M_cut and the corresponding DM-baryon cross-section. Assume Poisson noise: σ(N_abs) = sqrt(N_obs) where N_obs is the observed number, with N_sightlines ~ 10 background radio sources observable with SKA.

5. **Compare with existing constraints**: Compare the sensitivity forecasts from the 21 cm forest with existing constraints on DM-baryon scattering from: CMB (Xu et al. 2018: σ₀ < 10^{-22} cm² for m_χ = 1 GeV for n=0), global 21 cm (EDGES/SARAS3: limits at ~10^{-21} cm² level), and Lyman-α forest.

6. **Assess the novelty of structure suppression vs. cooling channels**: Quantitatively show that the 21 cm forest is unique in probing the structure suppression channel of DM-baryon scattering (complementary to the thermal channel probed by the global signal).

7. **Redshift dependence**: Analyze how the constraints evolve with z, identifying the optimal redshift for constraining DM-baryon scattering (should be z ~ 10 where N_abs is intermediate but sensitivity to M_cut is high).

## Notes for the Analyst

- Load the CSV with: `pd.read_csv('/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid_summary.csv')`
- Load the full JSON with: `json.load(open('/home/node/work/projects/dm_baryon_21cm_forest/data/hayashi_grid.json'))`
- Load N(>τ) distributions with: `np.load('/home/node/work/projects/dm_baryon_21cm_forest/data/Ngtau_z10_Mcut0.npz')`
- The `Nabs_total` column is already integrated over τ > 0.01.
- The CDM baseline corresponds to f_cool=1.0, M_cut=0.
- All HAYASHI computations include host halo + subhalo contributions (the subhalo boost from arXiv:2209.01305).
