#!/usr/bin/env python3
"""
Continuous Entropy Landscape for Prime Detection
=================================================

Core idea (Padraic's original insight):
    The Shannon entropy H(n) of the flattened (n-1)x(n-1) modular multiplication
    table mod n achieves its theoretical maximum log₂(n-1) if and only if n is prime.

This script constructs a non-circular continuous function:

    S(x) = Σ_{n=2}^{N}  w(n) · exp(-α(x-n)²)

    where w(n) = exp(-β · Δ(n)²)  and  Δ(n) = |H(n) - log₂(n-1)|

    Δ(n) = 0 exactly for primes (proven by the entropy theorem).
    Δ(n) > 0 for all composites (zero divisors distort the distribution).

    So w(n) = 1 for primes and w(n) ≈ 0 for composites.
    S(x) is a smooth function with peaks exactly at the primes.

    ** Everything is computed from multiplication tables.  No prime list. **

Usage:
    python continuous_entropy.py [N_max]        (default: 100)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys

# ---------------------------------------------------------------------------
# 1. Compute the entropy deficit Δ(n) = |H(n) - log₂(n-1)|
# ---------------------------------------------------------------------------

def modular_multiplication_entropy(n):
    """Shannon entropy of the flattened (n-1)x(n-1) multiplication table mod n."""
    if n <= 2:
        return 0.0
    total_cells = (n - 1) ** 2
    counts = np.zeros(n, dtype=np.int64)
    for j in range(1, n):
        for k in range(1, n):
            counts[(j * k) % n] += 1
    probs = counts[counts > 0] / total_cells
    return -np.sum(probs * np.log2(probs))


def entropy_deficit(n):
    """
    Δ(n) = |H(n) - log₂(n-1)|.
    Equals 0 iff n is prime.  Strictly positive for all composites.
    """
    if n <= 2:
        return 0.0 if n == 2 else 1.0
    H = modular_multiplication_entropy(n)
    H_target = np.log2(n - 1)
    return abs(H - H_target)


# ---------------------------------------------------------------------------
# 2. Build the continuous entropy signal S(x)
# ---------------------------------------------------------------------------

def entropy_signal(x, ns, deltas, beta, alpha):
    """
    S(x) = Σ_n  w(n) · exp(-α(x-n)²)

    where w(n) = exp(-β · Δ(n)²).

    Primes: Δ=0 → w=1 → full Gaussian bump
    Composites: Δ>0 → w≈0 → suppressed bump
    """
    w = np.exp(-beta * deltas ** 2)  # Weights
    # Vectorized: x is (M,), ns is (K,) → diff is (M, K)
    diff = x[:, np.newaxis] - ns[np.newaxis, :]
    gaussians = np.exp(-alpha * diff ** 2)
    S = np.sum(w[np.newaxis, :] * gaussians, axis=1)
    return S, w


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    BETA  = 500000.0  # Sharpness: exp(-β·Δ²) — even Δ=0.002 → w ≈ 0.14
    ALPHA = 12.0       # Gaussian bump width: exp(-12·0.5²) ≈ 0.05 → tight peaks

    # --- Step 1: Compute Δ(n) for each integer ---
    ns = np.arange(2, N_MAX + 1)
    print(f"Computing entropy deficit for n = 2 to {N_MAX} ...")
    deltas = np.array([entropy_deficit(n) for n in ns])

    # Ground-truth primes (comparison only)
    gt_primes = np.array([n for n in ns
                          if all(n % d != 0 for d in range(2, int(np.sqrt(n)) + 1))])
    print(f"Ground-truth primes: {len(gt_primes)}")

    # Show the closest composite to Δ=0 (hardest case)
    comp_mask_d = ~np.isin(ns, gt_primes)
    if np.any(comp_mask_d):
        min_delta_comp = deltas[comp_mask_d].min()
        hardest = ns[comp_mask_d][np.argmin(deltas[comp_mask_d])]
        print(f"Smallest composite Δ: Δ({hardest}) = {min_delta_comp:.6f}")
        print(f"  → weight w = exp(-{BETA}·{min_delta_comp:.6f}²) = {np.exp(-BETA * min_delta_comp**2):.2e}")

    # --- Step 2: Build continuous signal ---
    x = np.linspace(1.5, N_MAX + 0.5, 12000)
    dx = x[1] - x[0]

    S, w_vals = entropy_signal(x, ns.astype(float), deltas, BETA, ALPHA)

    # Derivative
    dS = np.gradient(S, dx)

    # --- Step 3: Detect primes as peaks of S(x) ---
    threshold = 0.5
    predicted_x = []
    for i in range(1, len(dS)):
        if dS[i - 1] > 0 and dS[i] <= 0 and S[i] > threshold:
            x_cross = x[i - 1] - dS[i - 1] * dx / (dS[i] - dS[i - 1])
            predicted_x.append(x_cross)

    predicted_ints = sorted(set(np.round(predicted_x).astype(int)))
    predicted_ints = [p for p in predicted_ints if 2 <= p <= N_MAX]

    print(f"\nPredicted primes (peaks of S): {predicted_ints}")
    print(f"Ground-truth primes:           {gt_primes.tolist()}")

    pred_set = set(predicted_ints)
    gt_set = set(gt_primes.tolist())
    false_pos = sorted(pred_set - gt_set)
    false_neg = sorted(gt_set - pred_set)

    if pred_set == gt_set:
        print(f"\n✅ Perfect match! All {len(gt_set)} primes detected, zero false positives.")
    else:
        if false_pos:
            print(f"❌ False positives:  {false_pos}")
        if false_neg:
            print(f"❌ False negatives:  {false_neg}")
        print(f"   Precision: {len(pred_set & gt_set)}/{len(pred_set)},  "
              f"Recall: {len(pred_set & gt_set)}/{len(gt_set)}")

    # --- Step 4: Visualization ---
    fig = plt.figure(figsize=(20, 16), dpi=150)
    gs = gridspec.GridSpec(4, 1, height_ratios=[0.8, 0.8, 1.2, 0.8], hspace=0.35)
    fig.suptitle(
        f'Non-Circular Continuous Entropy Landscape  ($n = 2$ to ${N_MAX}$)\n'
        'Derived from modular multiplication entropy — no prime list required',
        fontsize=15, fontweight='bold', y=0.995
    )

    prime_mask = np.isin(ns, gt_primes)
    comp_mask = ~prime_mask

    # ---- Panel 1: Entropy deficit Δ(n) ----
    ax1 = fig.add_subplot(gs[0])
    ax1.bar(ns[comp_mask], deltas[comp_mask], width=0.6, color='#ff6b6b',
            alpha=0.7, label='Composite ($\\Delta > 0$)', zorder=3)
    ax1.bar(ns[prime_mask], deltas[prime_mask], width=0.6, color='#4ecdc4',
            alpha=0.9, label='Prime ($\\Delta = 0$)', zorder=3)
    ax1.set_ylabel('$\\Delta(n) = |H(n) - \\log_2(n\\!-\\!1)|$', fontsize=11)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.3)
    ax1.set_title('Step 1:  Entropy deficit $\\Delta(n)$ — zero at primes, positive at composites',
                  fontsize=12, pad=8)

    # ---- Panel 2: Weights w(n) ----
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.bar(ns[comp_mask], w_vals[comp_mask], width=0.6, color='#ff6b6b',
            alpha=0.7, label='Composite (suppressed)', zorder=3)
    ax2.bar(ns[prime_mask], w_vals[prime_mask], width=0.6, color='#4ecdc4',
            alpha=0.9, label='Prime ($w = 1$)', zorder=3)
    ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.4, linewidth=0.8)
    ax2.set_ylabel('$w(n) = e^{-\\beta \\Delta(n)^2}$', fontsize=11)
    ax2.set_ylim(-0.05, 1.15)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.3)
    ax2.set_title(f'Step 2:  Gaussian weights $w(n) = e^{{-\\beta \\Delta^2}}$  '
                  f'with $\\beta = {int(BETA)}$  —  only primes survive',
                  fontsize=12, pad=8)

    # ---- Panel 3: Continuous signal S(x) ----
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.plot(x, S, color='#2196F3', linewidth=1.2,
             label=r'$S(x) = \sum_n w(n)\, e^{-\alpha(x-n)^2}$')
    ax3.scatter(gt_primes, [S[np.argmin(np.abs(x - p))] for p in gt_primes],
                color='#4ecdc4', s=30, zorder=5, label='Prime peaks')
    ax3.axhline(threshold, color='orange', linestyle=':', alpha=0.5,
                label=f'Detection threshold ({threshold})')
    for p in gt_primes:
        ax3.axvline(p, color='#4ecdc4', linestyle=':', alpha=0.10)
    ax3.set_ylabel('$S(x)$', fontsize=11)
    ax3.legend(loc='upper right', fontsize=10)
    ax3.grid(True, linestyle=':', alpha=0.3)
    ax3.set_title(
        f'Step 3:  Continuous entropy signal  ($\\alpha = {ALPHA}$)  '
        '— peaks at primes, flat elsewhere',
        fontsize=12, pad=8
    )

    # ---- Panel 4: Derivative dS/dx ----
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    ax4.plot(x, dS, color='#e91e63', linewidth=0.8, label=r"$S'(x)$")
    ax4.axhline(0, color='black', linestyle='--', alpha=0.4, linewidth=0.8)
    for px in predicted_x:
        ax4.plot(px, 0, 'o', color='#00897B', markersize=5, markerfacecolor='none',
                 markeredgewidth=1.2, zorder=5)
    ax4.plot([], [], 'o', color='#00897B', markersize=5, markerfacecolor='none',
             markeredgewidth=1.2, label=f'Detected primes ({len(predicted_ints)})')
    ax4.set_xlabel('$x$', fontsize=11)
    ax4.set_ylabel(r"$S'(x)$", fontsize=11)
    ax4.set_xlim(1.5, N_MAX + 0.5)
    tick_step = 2 if N_MAX <= 100 else 5
    ax4.set_xticks(np.arange(2, N_MAX + 1, tick_step))
    ax4.tick_params(axis='x', labelsize=7, rotation=45)
    ax4.legend(loc='upper right', fontsize=10)
    ax4.grid(True, linestyle=':', alpha=0.3)
    ax4.set_title(r"Step 4:  $S'(x)$ — descending zero-crossings above threshold = primes",
                  fontsize=12, pad=8)

    outfile = f'continuous_entropy_{N_MAX}.png'
    plt.savefig(outfile, bbox_inches='tight')
    print(f"\nPlot saved to {outfile}")
