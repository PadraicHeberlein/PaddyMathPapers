# Resolution & Findings: Key Decision Points for Paper 1

This document details the resolution, mathematical proofs, and physical/numerical findings for the three **Key Decision Points** identified in the implementation plan for Paper 1 (*On the Spectral Entropy of Modular Multiplication*). 

---

## 1. Decision Point 1: The Separation Gap & Prime-Square Decay (Phase 3)

### The Question
*Can we derive a closed-form expression for the entropy deficit of composites $\Delta(n)$ (specifically semiprimes $pq$ and prime squares $p^2$), and does the global separation gap between primes ($\Delta(p) = 0$) and composites ($\Delta(n) > 0$) remain bounded away from zero asymptotically?*

### The Findings
1. **Numerical Scale-up ($N=5000$):** We optimized the entropy computation using NumPy vectorization (`delta_analysis_extended.py`). Through $N=5000$, the semiprime $n=10$ ($2 \times 5$) remains the absolute minimum composite deficit:
   $$\delta_{\text{sep}}(5000) = \Delta(10) \approx 0.0019318$$
2. **Prime-Square Deficit Decay:** We proved that the deficit of prime squares $n = p^2$ is not bounded away from zero. Instead, it scales inversely with the prime generator $p$:
   $$\Delta(p^2) \sim \frac{1}{2p} \quad \text{as } p \to \infty$$
   For example, at $p = 67$ ($n = 4489$), we computed $\Delta(p^2) \approx 0.00760$, with the product $\Delta(p^2) \cdot p \approx 0.509$.
3. **Twin-Prime Semiprimes:** For semiprimes of the form $n = p(p+2)$, the deficit also scales down as $\mathcal{O}(1/p)$.

### The Resolution
* **Conjecture 1 is False Asymptotically:** Because $\lim_{p\to\infty} \Delta(p^2) = 0$, the separation gap $\delta_{\text{sep}}(N)$ shrinks to zero as $N \to \infty$. Specifically, for $p > 250$ ($n > 62{,}500$), the prime square deficit $\Delta(p^2)$ falls below the threshold $\Delta(10)$.
* **Linear Scaling of Contrast ($\beta$):** The contrast parameter $\beta$ in the continuous weight function $w(n) = e^{-\beta \Delta(n)^2}$ cannot remain a fixed constant for all $N \to \infty$. To prevent prime squares $p^2$ from creating false-positive peaks, we require:
   $$e^{-\beta \Delta(p^2)^2} < \epsilon_0 \implies e^{-\beta / 4n} < \epsilon_0 \implies \beta > 4n \ln(1/\epsilon_0)$$
   Thus, to maintain perfect prime detection, the contrast parameter must scale linearly with the range: **$\beta \sim \mathcal{O}(N)$**. 
* **Paper Update:** We updated Section 5.4 to replace the speculative conjecture with a formal **Proposition 1 (Prime-Square Deficit Decay)**, documented the $\beta$ scaling law, and added the log-log scaling plot as `figures/separation_gap_5000.png`.

---

## 2. Decision Point 2: Quantum Band Structure & Anderson Localization (Phase 4)

### The Question
*Does a physical particle confined to a unit ring with delta-function potentials proportional to modular residues display wave-state differences that distinguish primes and composites? Does it show Anderson localization or Random Matrix level statistics?*

### The Findings
We implemented a tight-binding lattice Hamiltonian $H$ on $n$ sites, where the diagonal potential at site $i$ is proportional to the modular remainder count $\operatorname{Res}(\mathcal{S}_n(z), z_i)$ and hopping is $t = 1.0$:
* **Prime Lattice ($n=97$):** Because a prime ring forms a finite field, the potential is perfectly uniform on all non-zero sites. This represents a perfect periodic crystal. The eigenstates are extended Bloch-like waves. The mean Participation Ratio (PR) is:
  $$\text{PR}_{\text{mean}} = 64.01 \quad (66.0\% \text{ delocalization})$$
* **Composite Lattice ($n=96$):** The presence of zero divisors and the premature cycling of non-coprime rows introduces extreme potential energy fluctuations (a deep sink of $V_0 = -188$ at $i=0$ and zero potential at coprime sites). This number-theoretic disorder acts as an amorphous lattice, triggering severe **Anderson localization**. The mean Participation Ratio collapses to:
  $$\text{PR}_{\text{mean}} = 2.39 \quad (2.5\% \text{ delocalization})$$
  with a maximum PR of only $5.00$ across all 96 states.

### The Resolution
* **Rigorous Validation:** The quantum section was transformed from speculative analogy to concrete, computed physics. The prime ring is a resonant crystalline structure allowing free-flowing Bloch wave transport, whereas the composite ring is a highly localized, disordered quantum system.
* **Paper Update:** We rewrote Section 8 to present the tight-binding equations, the participation ratio metrics, and the localization findings. We added the comparative spectral plot as `figures/quantum_ring_comparison.png`.

---

## 3. Decision Point 3: Laurent Expansion & Divisors (Phase 5)

### The Question
*Does the Spectral Remainder Transform $\mathcal{S}_n(z)$ contain information beyond a simple histogram count of residues? What is the behavior of the transform at $z = 0$ and $z \to \infty$?*

### The Findings
1. **Topological Invariant at the Origin:** We evaluated $\mathcal{S}_n(0)$ and proved analytically and numerically that:
   $$\mathcal{S}_n(0) = n - 1 \quad \forall n \geq 2$$
   This value depends solely on the size $n$ and is identical for both primes and composites, meaning the origin carries no number-theoretic information.
2. **Laurent Coefficients Formula:** The expansion coefficients around infinity, $C_m(n) = \sum_{j,k} e^{2\pi i m (jk \bmod n)/n}$, simplify to an exact, elegant divisor identity:
   $$C_m(n) = n \cdot \gcd(m, n) - 2n + 1$$
3. **Laurent Primality Criterion:** If $n$ is prime, then $\gcd(m, n) = 1$ for all $1 \le m \le n-1$, giving a constant coefficient $C_m(n) = 1-n$. If $n$ is composite, the coefficients jump to positive values (e.g., $C_d(n) = nd - 2n + 1 \ge 1$) at divisor indexes $d$.

### The Resolution
* **Divisor Bridge:** We established a direct, algebraic link between the transform's asymptotic behavior at infinity and the divisors of $n$. The Laurent coefficients $C_m(n)$ are a linear combination of Ramanujan-type sums over the divisor classes of $\mathbb{Z}/n\mathbb{Z}$.
* **Paper Update:** We added Section 2.4 (**Laurent Expansion at Infinity and Ramanujan-type Sums**) detailing Proposition 2, its proof, the Laurent Primality Criterion, and the evaluation at $z=0$.
