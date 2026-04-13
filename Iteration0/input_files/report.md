

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
        