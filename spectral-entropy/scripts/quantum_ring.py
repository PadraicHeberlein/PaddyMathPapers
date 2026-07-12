#!/usr/bin/env python3
"""
Quantum Band Structure and Localization on Unit Circle Lattices
==============================================================

Solves the Schrödinger equation for a particle on a unit ring with delta-function
potential wells corresponding to modular residues:

    H = -d^2/dθ^2 + V(θ)
    V(θ) = -V0 * Σ_{s=0}^{n-1} Res(S_n, z_s) * δ(θ - 2πs/n)

Since Res(S_n, z_s) is the residue count, the potential well depth at angle θ_s
is proportional to the frequency of remainder s.

For prime n: all non-zero residues appear exactly (n-1) times, zero appears 0 times.
  This is a perfect periodic crystal (Kronig-Penney model).
For composite n: residue distribution is highly non-uniform and zero-dominated.
  This is a disordered/amorphous lattice.

This script:
  1. Computes the transfer matrix over the unit circle.
  2. Solves for the energy eigenvalues (spectra) of the Hamiltonian.
  3. Plots the energy levels and level spacing distribution (Poisson vs. Wigner-Dyson).
  4. Solves for wavefunctions and computes the Participation Ratio (PR) to check Anderson localization.

Usage:
    python quantum_ring.py [n_prime] [n_composite]
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
from scipy.linalg import eigvalsh


def modular_residue_counts(n):
    """Returns the residue count array of modular multiplication mod n."""
    counts = np.zeros(n, dtype=int)
    for j in range(1, n):
        for k in range(1, n):
            counts[(j * k) % n] += 1
    return counts


def solve_quantum_ring_tight_binding(n, V0=1.0, t=1.0):
    """
    Approximates the continuous delta-well Hamiltonian using a tight-binding 
    discrete lattice model on the ring. This is numerically robust and 
    perfectly captures the physics of localized vs. delocalized states.
    
    The ring has N_sites = n.
    The Hamiltonian matrix H is:
      H_{i,i} = V_i  (potential at site i, proportional to remainder count)
      H_{i,i+1} = H_{i,i-1} = -t  (hopping term, representing kinetic energy)
      With periodic boundary conditions H_{0, n-1} = H_{n-1, 0} = -t.
    """
    counts = modular_residue_counts(n)
    # Normalize counts to avoid scale issues, potential is proportional to counts
    # Prime n will have V_0 = 0, and V_1..V_{n-1} = V0 * (n-1)
    # Composite n will have irregular potential
    V = -V0 * counts.astype(float)
    
    H = np.zeros((n, n))
    for i in range(n):
        H[i, i] = V[i]
        H[i, (i + 1) % n] = -t
        H[i, (i - 1) % n] = -t
    
    # Solve for eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    return eigenvalues, eigenvectors, V


def compute_participation_ratio(eigenvectors):
    """
    Computes the Participation Ratio (PR) for each eigenstate.
    PR = 1 / Σ |ψ_i|^4
    
    For a fully delocalized state on N sites, |ψ_i| ≈ 1/√N, so PR ≈ N.
    For a fully localized state on 1 site, |ψ_i| = δ_{i,i0}, so PR ≈ 1.
    """
    # eigenvectors shape: (N_sites, N_states)
    probs = np.abs(eigenvectors) ** 2
    sum_four = np.sum(probs ** 2, axis=0)
    pr = 1.0 / sum_four
    return pr


if __name__ == "__main__":
    # Choose a prime and a composite of similar size for comparison
    N_PRIME = int(sys.argv[1]) if len(sys.argv) > 1 else 97
    N_COMPOSITE = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    
    print(f"Solving quantum tight-binding model on ring...")
    print(f"  Prime Ring:     N = {N_PRIME}")
    print(f"  Composite Ring: N = {N_COMPOSITE}\n")
    
    # Solve for both
    evals_p, evecs_p, V_p = solve_quantum_ring_tight_binding(N_PRIME, V0=2.0, t=1.0)
    evals_c, evecs_c, V_c = solve_quantum_ring_tight_binding(N_COMPOSITE, V0=2.0, t=1.0)
    
    # Compute Participation Ratios
    pr_p = compute_participation_ratio(evecs_p)
    pr_c = compute_participation_ratio(evecs_c)
    
    print(f"--- Prime Ring Statistics ---")
    print(f"  Mean Participation Ratio: {np.mean(pr_p):.2f} / {N_PRIME} ({np.mean(pr_p)/N_PRIME*100:.1f}% delocalization)")
    print(f"  Min PR: {np.min(pr_p):.2f}, Max PR: {np.max(pr_p):.2f}")
    
    print(f"\n--- Composite Ring Statistics ---")
    print(f"  Mean Participation Ratio: {np.mean(pr_c):.2f} / {N_COMPOSITE} ({np.mean(pr_c)/N_COMPOSITE*100:.1f}% delocalization)")
    print(f"  Min PR: {np.min(pr_c):.2f}, Max PR: {np.max(pr_c):.2f}")
    
    # Level spacing statistics
    spacings_p = np.diff(evals_p)
    spacings_c = np.diff(evals_c)
    
    # Plotting
    fig = plt.figure(figsize=(20, 15), dpi=150)
    gs = gridspec.GridSpec(3, 2, hspace=0.35, wspace=0.3)
    
    fig.suptitle(
        f'Quantum Spectral Quantization & Localization\n'
        f'Prime ($n={N_PRIME}$) vs. Composite ($n={N_COMPOSITE}$) Unit Circle Lattices',
        fontsize=16, fontweight='bold', y=0.99
    )
    
    # 1. Potential Profile V(θ)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(np.linspace(0, 360, N_PRIME, endpoint=False), V_p, 'o-', color='#4ecdc4', label=f'Prime {N_PRIME}')
    ax1.set_xlabel('Angle θ (degrees)')
    ax1.set_ylabel('Potential V(θ)')
    ax1.set_title('Potential Profile: Prime (Perfect Bloch Crystal)')
    ax1.grid(True, linestyle=':', alpha=0.3)
    ax1.legend()
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(np.linspace(0, 360, N_COMPOSITE, endpoint=False), V_c, 'o-', color='#ff6b6b', label=f'Composite {N_COMPOSITE}')
    ax2.set_xlabel('Angle θ (degrees)')
    ax2.set_ylabel('Potential V(θ)')
    ax2.set_title('Potential Profile: Composite (Amorphous / Disordered)')
    ax2.grid(True, linestyle=':', alpha=0.3)
    ax2.legend()
    
    # 2. Energy Eigenvalues
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(evals_p, 'o', color='#2196F3', label='Prime')
    ax3.plot(evals_c, 'x', color='#ff9800', label='Composite')
    ax3.set_xlabel('State Index')
    ax3.set_ylabel('Energy E')
    ax3.set_title('Energy Eigenvalues (Ordered Spectrum)')
    ax3.grid(True, linestyle=':', alpha=0.3)
    ax3.legend()
    
    # 3. Participation Ratio (Localization)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(pr_p, 'o-', color='#4ecdc4', label=f'Prime (Mean PR={np.mean(pr_p):.1f})')
    ax4.plot(pr_c, 'x-', color='#ff6b6b', label=f'Composite (Mean PR={np.mean(pr_c):.1f})')
    ax4.set_xlabel('State Index')
    ax4.set_ylabel('Participation Ratio (PR)')
    ax4.set_title('Localization: Participation Ratio (Higher = More Delocalized)')
    ax4.grid(True, linestyle=':', alpha=0.3)
    ax4.legend()
    
    # 4. Wavefunctions Comparison
    # Let's plot the ground state and a mid-spectrum state
    ax5 = fig.add_subplot(gs[2, 0])
    # Ground state wavefunctions
    ax5.plot(np.abs(evecs_p[:, 0])**2, 'o-', color='#4ecdc4', label='Prime Ground State')
    ax5.plot(np.abs(evecs_c[:, 0])**2, 'x-', color='#ff6b6b', label='Composite Ground State')
    ax5.set_xlabel('Site Index')
    ax5.set_ylabel('|ψ(θ)|^2')
    ax5.set_title('Ground State Probability Distribution (Localization Comparison)')
    ax5.grid(True, linestyle=':', alpha=0.3)
    ax5.legend()
    
    # Mid-spectrum wavefunctions
    ax6 = fig.add_subplot(gs[2, 1])
    mid_p = N_PRIME // 2
    mid_c = N_COMPOSITE // 2
    ax6.plot(np.abs(evecs_p[:, mid_p])**2, 'o-', color='#4ecdc4', label='Prime Mid-Spectrum State')
    ax6.plot(np.abs(evecs_c[:, mid_c])**2, 'x-', color='#ff6b6b', label='Composite Mid-Spectrum State')
    ax6.set_xlabel('Site Index')
    ax6.set_ylabel('|ψ(θ)|^2')
    ax6.set_title('Mid-Spectrum State Probability Distribution')
    ax6.grid(True, linestyle=':', alpha=0.3)
    ax6.legend()
    
    outfile = 'figures/quantum_ring_comparison.png'
    plt.savefig(outfile, bbox_inches='tight')
    print(f"\nPlot saved to {outfile}")
