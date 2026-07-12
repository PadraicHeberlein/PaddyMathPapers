#!/usr/bin/env python3
"""
Entropy Deficit Separation Analysis
====================================

Key question: Does the minimum composite Δ(n) shrink toward zero as N grows?

If min Δ stays bounded away from zero → S(x) is fundamentally sound at any scale.
If min Δ → 0                         → β must grow with N, limiting the method.

This script:
  1. Computes Δ(n) for all n up to N_MAX
  2. Tracks the 10 smallest composite deficits at each scale
  3. Plots min Δ vs N to reveal the asymptotic behavior
  4. Analyzes whether the hardest composites share structure (prime powers, semiprimes, etc.)

Usage:
    python delta_analysis.py [N_max]        (default: 2000)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
import time
from math import gcd, isqrt

# ---------------------------------------------------------------------------
# 1. Entropy computation (same as continuous_entropy.py)
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
    """Δ(n) = |H(n) - log₂(n-1)|. Zero iff n is prime."""
    if n <= 2:
        return 0.0 if n == 2 else 1.0
    H = modular_multiplication_entropy(n)
    H_target = np.log2(n - 1)
    return abs(H - H_target)


# ---------------------------------------------------------------------------
# 2. Factorization utilities (for classifying composites)
# ---------------------------------------------------------------------------

def is_prime(n):
    """Trial division primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def classify_composite(n):
    """Classify a composite number by its factorization structure."""
    if is_prime(n):
        return "prime"

    # Check prime power
    for p in range(2, isqrt(n) + 1):
        if n % p == 0:
            k = 0
            m = n
            while m % p == 0:
                m //= p
                k += 1
            if m == 1:
                return f"p^{k} ({p}^{k})"
            # Count distinct prime factors
            factors = [p]
            temp = m
            for q in range(p + 1, isqrt(temp) + 2):
                if temp % q == 0:
                    factors.append(q)
                    while temp % q == 0:
                        temp //= q
            if temp > 1:
                factors.append(temp)

            if len(factors) == 2 and k == 1:
                other = n // p
                if is_prime(other):
                    return f"semiprime ({p}×{other})"
            return f"{len(factors)}-factor composite"
    return "composite"


# ---------------------------------------------------------------------------
# 3. Main analysis
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    print(f"Computing entropy deficit for n = 2 to {N_MAX} ...")
    print(f"(This requires O(n²) work per integer — be patient for large N)\n")

    ns = np.arange(2, N_MAX + 1)
    deltas = np.zeros(len(ns))
    is_comp = np.zeros(len(ns), dtype=bool)

    t0 = time.time()
    for idx, n in enumerate(ns):
        deltas[idx] = entropy_deficit(n)
        is_comp[idx] = not is_prime(n)
        # Progress
        if (n % 200 == 0) or n == N_MAX:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            eta = (len(ns) - idx - 1) / rate
            print(f"  n = {n:5d}  |  elapsed: {elapsed:6.1f}s  |  rate: {rate:.1f} n/s  |  ETA: {eta:.0f}s")

    total_time = time.time() - t0
    print(f"\nTotal computation time: {total_time:.1f}s\n")

    # --- Composite deficits only ---
    comp_ns = ns[is_comp]
    comp_deltas = deltas[is_comp]

    # --- Track min Δ at each scale ---
    scales = list(range(10, N_MAX + 1, 1))
    min_deltas = []
    min_n_at_scale = []

    for N in scales:
        mask = comp_ns <= N
        if not np.any(mask):
            min_deltas.append(np.nan)
            min_n_at_scale.append(0)
            continue
        idx_min = np.argmin(comp_deltas[mask])
        min_deltas.append(comp_deltas[mask][idx_min])
        min_n_at_scale.append(comp_ns[mask][idx_min])

    min_deltas = np.array(min_deltas)
    min_n_at_scale = np.array(min_n_at_scale)

    # --- Top 20 smallest composite deficits ---
    sorted_idx = np.argsort(comp_deltas)[:20]
    print("=" * 75)
    print(f"  20 SMALLEST COMPOSITE DEFICITS  (n ≤ {N_MAX})")
    print("=" * 75)
    print(f"  {'Rank':>4}  {'n':>6}  {'Δ(n)':>14}  {'w (β=500k)':>12}  {'Type'}")
    print("-" * 75)
    for rank, idx in enumerate(sorted_idx, 1):
        n = comp_ns[idx]
        d = comp_deltas[idx]
        w = np.exp(-500000 * d**2)
        ctype = classify_composite(int(n))
        print(f"  {rank:>4}  {n:>6}  {d:>14.8f}  {w:>12.2e}  {ctype}")

    # --- Check: does min Δ(n) · √n stay bounded? ---
    print(f"\n{'=' * 75}")
    print(f"  SCALING BEHAVIOR OF MIN Δ")
    print(f"{'=' * 75}")
    checkpoints = [50, 100, 200, 500, 1000, 1500, 2000]
    checkpoints = [c for c in checkpoints if c <= N_MAX]
    print(f"  {'N':>6}  {'min Δ':>14}  {'hardest n':>10}  {'Δ·√n':>10}  {'Δ·n':>10}  {'Type'}")
    print("-" * 75)
    for N in checkpoints:
        mask = comp_ns <= N
        if not np.any(mask):
            continue
        idx_min = np.argmin(comp_deltas[mask])
        d = comp_deltas[mask][idx_min]
        n = comp_ns[mask][idx_min]
        ctype = classify_composite(int(n))
        print(f"  {N:>6}  {d:>14.8f}  {n:>10}  {d * np.sqrt(n):>10.4f}  {d * n:>10.4f}  {ctype}")

    # --- Visualization ---
    fig = plt.figure(figsize=(18, 14), dpi=150)
    gs = gridspec.GridSpec(3, 2, hspace=0.35, wspace=0.3)
    fig.suptitle(
        f'Entropy Deficit Separation Analysis  ($n = 2$ to ${N_MAX}$)\n'
        'Does min $\\Delta$(composite) stay bounded away from zero?',
        fontsize=14, fontweight='bold', y=0.995
    )

    # Panel 1: All composite deltas (scatter)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.scatter(comp_ns, comp_deltas, s=2, alpha=0.4, color='#ff6b6b', zorder=3)
    ax1.set_xlabel('$n$ (composite)', fontsize=10)
    ax1.set_ylabel('$\\Delta(n)$', fontsize=10)
    ax1.set_title('Entropy deficit $\\Delta(n) = |H(n) - \\log_2(n-1)|$ for all composites',
                  fontsize=11, pad=8)
    ax1.grid(True, linestyle=':', alpha=0.3)
    # Highlight the 10 smallest
    for idx in sorted_idx[:10]:
        n = comp_ns[idx]
        d = comp_deltas[idx]
        ax1.annotate(f'{int(n)}', (n, d), fontsize=6, color='#e91e63',
                    textcoords="offset points", xytext=(3, 3))
        ax1.scatter([n], [d], s=30, color='#e91e63', zorder=5, edgecolors='black', linewidths=0.5)

    # Panel 2: Min Δ vs N (the key plot)
    ax2 = fig.add_subplot(gs[1, 0])
    valid = ~np.isnan(min_deltas)
    ax2.plot(np.array(scales)[valid], min_deltas[valid], color='#2196F3', linewidth=1.2)
    ax2.set_xlabel('$N$ (upper bound)', fontsize=10)
    ax2.set_ylabel('min $\\Delta$(composite $\\leq N$)', fontsize=10)
    ax2.set_title('Minimum composite deficit vs. scale', fontsize=11, pad=8)
    ax2.grid(True, linestyle=':', alpha=0.3)
    ax2.set_yscale('log')

    # Panel 3: Δ · √n scaling
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.scatter(comp_ns, comp_deltas * np.sqrt(comp_ns), s=2, alpha=0.4,
                color='#4ecdc4', zorder=3)
    ax3.set_xlabel('$n$ (composite)', fontsize=10)
    ax3.set_ylabel('$\\Delta(n) \\cdot \\sqrt{n}$', fontsize=10)
    ax3.set_title('Scaled deficit $\\Delta(n) \\cdot \\sqrt{n}$ — bounded below?',
                  fontsize=11, pad=8)
    ax3.grid(True, linestyle=':', alpha=0.3)

    # Panel 4: Histogram of log(Δ)
    ax4 = fig.add_subplot(gs[2, 0])
    log_deltas = np.log10(comp_deltas[comp_deltas > 0])
    ax4.hist(log_deltas, bins=80, color='#ff9800', alpha=0.7, edgecolor='#e65100', linewidth=0.5)
    ax4.set_xlabel('$\\log_{10} \\Delta(n)$', fontsize=10)
    ax4.set_ylabel('Count', fontsize=10)
    ax4.set_title('Distribution of $\\log_{10} \\Delta$ for composites', fontsize=11, pad=8)
    ax4.grid(True, linestyle=':', alpha=0.3)

    # Panel 5: Δ by composite type
    ax5 = fig.add_subplot(gs[2, 1])
    # Classify composites into categories
    categories = {'Prime power': [], 'Semiprime': [], 'Other': []}
    for idx in range(len(comp_ns)):
        n = int(comp_ns[idx])
        d = comp_deltas[idx]
        ct = classify_composite(n)
        if ct.startswith('p^'):
            categories['Prime power'].append((n, d))
        elif ct.startswith('semiprime'):
            categories['Semiprime'].append((n, d))
        else:
            categories['Other'].append((n, d))

    colors = {'Prime power': '#e91e63', 'Semiprime': '#9c27b0', 'Other': '#bdbdbd'}
    for label, data in categories.items():
        if data:
            xs, ys = zip(*data)
            ax5.scatter(xs, ys, s=4 if label == 'Other' else 12,
                       alpha=0.3 if label == 'Other' else 0.7,
                       color=colors[label], label=f'{label} ({len(data)})', zorder=3 if label == 'Other' else 5)
    ax5.set_xlabel('$n$ (composite)', fontsize=10)
    ax5.set_ylabel('$\\Delta(n)$', fontsize=10)
    ax5.set_title('Deficit by composite type', fontsize=11, pad=8)
    ax5.legend(fontsize=8, loc='upper right')
    ax5.grid(True, linestyle=':', alpha=0.3)

    outfile = f'delta_analysis_{N_MAX}.png'
    plt.savefig(outfile, bbox_inches='tight')
    print(f"\nPlot saved to {outfile}")
