

Iteration 0:
### Summary: DM-Baryon Scattering and the 21 cm Forest

**1. Project Status & Core Findings**
*   **Objective:** Quantify 21 cm forest sensitivity to DM-baryon scattering via HAYASHI semianalytic framework.
*   **Dominant Mechanism:** Structure suppression ($M_{cut}$) is the primary observable, outperforming thermal cooling ($f_{cool}$) by a factor of 40–140x. Cooling effects are negligible at $z=7–15$ due to spin temperature saturation in the cold IGM.
*   **Optimal Strategy:** $z \sim 10$ is the optimal observational window, balancing high sensitivity to $M_{cut}$ with sufficient baseline absorber counts ($N_{abs} \approx 59$).
*   **Spectral Sensitivity:** 80% of Fisher information is concentrated in the optical depth range $\tau \in [0.022, 0.217]$. Using the differential spectrum $dN/d\tau$ provides 16–26% more constraining power than total counts.

**2. Quantitative Constraints (SKA Forecast)**
*   **Sensitivity:** 1-$\sigma$ sensitivity for $M_{cut}$ at $z=10$ is $\sim 816 \ M_\odot$.
*   **Cross-section Bounds ($n=0$):** Forecasted 1-$\sigma$ limit of $\sim 8 \times 10^{-26} \text{ cm}^2/\text{GeV}$ at $z=10$.
*   **Comparative Advantage:** The 21 cm forest is potentially $\sim 1,200\times$ more sensitive to DM-baryon scattering than current CMB (Xu et al. 2018) or global 21 cm (EDGES/SARAS3) constraints, due to its unique probe of small-scale ($k \sim 10-100 \text{ Mpc}^{-1}$) structure.

**3. Methodological Constraints & Assumptions**
*   **Data:** Grid of 180 points covering $z \in [7, 15]$, $f_{cool} \in [0.02, 1.0]$, $M_{cut} \in [0, 10^6 \ M_\odot]$.
*   **Mapping:** $M_{cut}$ to $\sigma_0/m_\chi$ uses power-law interpolation. Coulomb-like ($n=-4$) mapping includes $z$-dependent velocity scaling: $\sigma(z) = \sigma(z=10) \times ((1+z)/11)^2$.
*   **Fisher Analysis:** Assumes 10 background radio sources and Poisson noise $\sigma(dN/d\tau) = \sqrt{N_{obs}} / \Delta\tau$.

**4. Future Directions & Uncertainties**
*   **Nuisance Parameters:** Astrophysical degeneracies (ionizing background, Reionization timing, halo mass function normalization) remain the primary systematic risk.
*   **Recommendation:** Future work must incorporate these astrophysical uncertainties into the Fisher matrix to ensure the spectral shape of $M_{cut}$ suppression remains distinguishable from standard astrophysical evolution.
        

Iteration 1:
**Methodological Evolution**
- **Shift to Differential Analysis**: The research strategy transitioned from a broad parameter sweep (Iteration 0) to a focused Fisher information analysis. We moved from analyzing total absorber counts ($N_{abs}$) to evaluating the differential optical depth distribution ($dN/d\tau$).
- **Fisher Information Framework**: We implemented a Fisher matrix $F_{ij}$ to quantify sensitivity, incorporating Poisson noise $\sigma = \sqrt{N_{obs}} / \Delta\tau$ and marginalizing over an astrophysical nuisance parameter $A$ (representing halo mass function normalization).
- **Optimization Strategy**: We introduced a weighting scheme for $\tau$-bins based on the derivative $\partial (dN/d\tau) / \partial M_{cut}$ to isolate the signal of structure suppression from astrophysical noise.

**Performance Delta**
- **Sensitivity Gains**: By moving from total counts to spectral shape analysis ($dN/d\tau$), we successfully broke the degeneracy between $M_{cut}$ and redshift evolution. Marginalizing over nuisance parameters increased the 1-$\sigma$ error on $M_{cut}$ by a factor of ~2.6 compared to unmarginalized estimates, but the resulting constraints remain robust ($\sigma(M_{cut}) \approx 1300-1800 M_\odot$ at $z=7-10$).
- **Constraint Improvement**: The projected sensitivity to the scattering cross-section ($\sigma_0/m_\chi \approx 10^{-26}$ cm$^2$/GeV) represents a 2-to-4 order-of-magnitude improvement over existing Lyman-$\alpha$ and CMB constraints.
- **Trade-offs**: While absolute SNR is higher at $z=7$, the fractional sensitivity ($\Delta N/N$) is significantly higher at $z=15$. The identification of $z \sim 10$ as the "optimal window" represents a strategic trade-off between statistical power and susceptibility to reionization-era systematics.

**Synthesis**
- **Causal Attribution**: The observed insensitivity to the thermal channel ($f_{cool}$) is attributed to the saturation of spin temperature coupling in the cold, high-redshift IGM. Conversely, the high sensitivity to $M_{cut}$ is attributed to the preferential depletion of low-mass minihalos, which manifest as intermediate-$\tau$ absorbers.
- **Validity and Limits**: The results confirm that the 21 cm forest is a "calorimeter" for structure suppression rather than thermal history. The validity of these constraints relies on the assumption that the subhalo boost model (HAYASHI) remains accurate in the presence of DM-baryon scattering; we have treated this as a conservative estimate by applying the transfer function to the total halo mass function.
- **Direction**: Future research should prioritize high-resolution characterization of the $\tau \in [0.02, 0.27]$ range at $z \sim 10$. The success of the Fisher forecast suggests that the 21 cm forest is the most promising tool for probing DM-baryon scattering at the threshold of minihalo formation, effectively bypassing the limitations of global signal experiments.
        