#!/usr/bin/env python3
"""
Next-Prime Finder via Gradient Ascent on the Entropy Signal
=============================================================

Implements the momentum-driven gradient ascent algorithm from Section 6 of
"On the Spectral Entropy of Modular Multiplication":

    v_{k+1} = μ · v_k  +  γ · S'(x_k)
    x_{k+1} = x_k      +  v_{k+1}

where S(x) = Σ_n w(n) · exp(-α(x-n)²)  is the continuous entropy signal
whose peaks sit exactly at the primes.

Given a known prime p, the algorithm:
  1. Builds S(x) on a window [p-2, p+W] using entropy deficits Δ(n)
     computed directly from modular multiplication tables (no sieve).
  2. Launches a particle at x₀ = p + 0.5 with initial velocity v₀ > 0.
  3. Tracks the momentum-augmented trajectory until it settles on the
     next local maximum of S(x), which corresponds to the next prime.
  4. If the particle exits the window without converging, the window is
     expanded and the computation is retried.

Usage:
    python3 next_prime.py <prime>                  # find the next prime
    python3 next_prime.py <prime> --verbose         # show trajectory details
    python3 next_prime.py <prime> --plot             # save trajectory plot

Example:
    $ python3 next_prime.py 97
    Next prime after 97 is: 101
"""

import numpy as np
import sys
import argparse

# ──────────────────────────────────────────────────────────────────────────────
# 1. Entropy deficit Δ(n) — computed from scratch, no prime list
# ──────────────────────────────────────────────────────────────────────────────

def modular_multiplication_entropy(n):
    """Shannon entropy of the flattened (n-1)×(n-1) multiplication table mod n."""
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
    """Δ(n) = |H(n) - log₂(n-1)|.  Zero iff n is prime."""
    if n <= 1:
        return 1.0
    if n == 2:
        return 0.0
    H = modular_multiplication_entropy(n)
    H_target = np.log2(n - 1)
    return abs(H - H_target)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Continuous entropy signal S(x) and its analytic derivative S'(x)
# ──────────────────────────────────────────────────────────────────────────────

def build_signal(ns, deltas, beta, alpha):
    """
    Return callable (S, S') for the continuous entropy signal.

    S(x)  = Σ_n  w(n) · exp(-α(x - n)²)
    S'(x) = Σ_n  w(n) · [-2α(x - n)] · exp(-α(x - n)²)

    where w(n) = exp(-β · Δ(n)²).
    """
    ns_f = ns.astype(float)
    w = np.exp(-beta * deltas ** 2)

    def S(x):
        diff = x - ns_f
        g = np.exp(-alpha * diff ** 2)
        return np.sum(w * g)

    def dS(x):
        diff = x - ns_f
        g = np.exp(-alpha * diff ** 2)
        return np.sum(w * (-2.0 * alpha * diff) * g)

    return S, dS


# ──────────────────────────────────────────────────────────────────────────────
# 3. Momentum-driven gradient ascent (Section 6 of the paper)
# ──────────────────────────────────────────────────────────────────────────────

def gradient_ascent_next_prime(
    p,
    beta=500_000.0,
    alpha=12.0,
    gamma=0.05,       # learning rate (gradient coupling)
    mu=0.6,           # momentum decay
    max_steps=10000,
    tol=1e-6,         # convergence tolerance on |v|
    verbose=False,
):
    """
    Starting from a known prime p, find the next prime via momentum-augmented
    gradient ascent on the continuous entropy signal S(x).

    The algorithm uses two convergence strategies:
      (a) Peak crossing detection: when S'(x) changes sign from positive
          to negative near an integer n > p with S(n) > 0.5, snap to n.
      (b) Velocity convergence: |v| < tol while S(x) > 0.5.

    To traverse composite deserts where S(x) ≈ 0 and S'(x) ≈ 0, a minimum
    drift velocity v_min ensures the particle always creeps forward until
    it encounters the ascending slope of the next prime peak.

    Returns
    -------
    next_p : int
        The next prime after p.
    trajectory : list of (step, x, v, S_val)
        Full trajectory of the particle.
    """
    # Minimum drift velocity through composite deserts.
    # This is the "momentum from the preceding prime peak" described in
    # Section 6.2 — when the gradient vanishes, accumulated inertia
    # carries the particle forward.
    v_min = 0.05

    # Adaptive window: start with a generous estimate.
    # Bertrand's postulate guarantees a prime in (p, 2p).
    window_margin = max(30, int(np.sqrt(p) * 4))

    while True:
        lo = max(2, p - 2)
        hi = p + window_margin

        # Build the discrete deficits for the window
        ns = np.arange(lo, hi + 1)
        if verbose:
            print(f"  Building S(x) on [{lo}, {hi}] ({len(ns)} integers) ...")

        deltas = np.array([entropy_deficit(int(n)) for n in ns])
        S, dS = build_signal(ns, deltas, beta, alpha)

        # Launch particle past the trough of the current prime's bump.
        # With α=12, the Gaussian bump decays to ~5% at distance 0.5.
        # For small primes (p < 10), use a smaller offset so we don't
        # overshoot closely spaced primes (e.g. 2 → 3, 3 → 5).
        launch_offset = 0.5 if p < 10 else 1.5
        x = float(p) + launch_offset
        v = v_min
        trajectory = []
        prev_ds_sign = None  # for zero-crossing detection

        converged = False
        found_prime = None

        for step in range(max_steps):
            s_val = S(x)
            ds_val = dS(x)
            trajectory.append((step, x, v, s_val))

            # --- Check for descending zero-crossing of S'(x) near an integer ---
            # This catches the particle climbing up and then crossing over
            # the peak of the next prime.
            cur_ds_sign = 1 if ds_val > 0 else -1
            if prev_ds_sign is not None and prev_ds_sign > 0 and cur_ds_sign <= 0:
                # We just crossed a peak.  Is it a prime peak?
                nearest = int(round(x))
                if nearest > p and nearest >= 2:
                    peak_val = S(float(nearest))
                    if peak_val > 0.5:
                        # Verify it is genuinely a local max
                        d_left = dS(float(nearest) - 0.05)
                        d_right = dS(float(nearest) + 0.05)
                        if d_left > 0 and d_right < 0:
                            found_prime = nearest
                            x = float(nearest)
                            converged = True
                            break
            prev_ds_sign = cur_ds_sign

            # --- Momentum update (Eq. from Section 6.2) ---
            v = mu * v + gamma * ds_val

            # Enforce minimum forward drift through dead zones.
            # When S(x) < 0.1 (composite desert), the gradient is
            # negligible, so we maintain inertial coasting.
            if v < v_min and s_val < 0.3:
                v = v_min

            x = x + v

            # --- Velocity convergence check ---
            if abs(v) < tol and s_val > 0.5:
                nearest = int(round(x))
                if nearest > p:
                    found_prime = nearest
                    converged = True
                    break

            # --- Safety: particle escaped the window ---
            if x > hi - 1:
                break

            # --- Safety: particle stuck or going backwards ---
            if x < float(p):
                x = float(p) + launch_offset
                v = v_min

        if converged and found_prime is not None:
            # Validate: verify Δ(found_prime) = 0
            d = entropy_deficit(found_prime)
            if d < 1e-10:
                if verbose:
                    print(f"  Converged at step {step}: x = {x:.6f} → {found_prime}")
                    print(f"  Δ({found_prime}) = {d:.2e}  ✓")
                return found_prime, trajectory
            else:
                # Rare: converged on a composite with near-zero deficit.
                if verbose:
                    print(f"  False convergence at {found_prime} "
                          f"(Δ = {d:.6f}), expanding ...")
                window_margin = int(window_margin * 1.5)
                continue

        # Did not converge — expand the window
        if verbose:
            print(f"  No convergence in [{lo}, {hi}], expanding window ...")
        window_margin = int(window_margin * 1.5)

        if window_margin > 2 * p + 50:
            raise RuntimeError(
                f"Window exceeded Bertrand bound. This should not happen. "
                f"Last position: x = {x:.4f}, v = {v:.6f}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 4. Trajectory visualization
# ──────────────────────────────────────────────────────────────────────────────

def plot_trajectory(p, next_p, trajectory, beta, alpha):
    """Save a plot of the gradient ascent trajectory overlaid on S(x)."""
    import matplotlib.pyplot as plt

    lo = max(2, p - 2)
    hi = next_p + 5
    ns = np.arange(lo, hi + 1)
    deltas = np.array([entropy_deficit(int(n)) for n in ns])
    S_func, dS_func = build_signal(ns, deltas, beta, alpha)

    xs = np.linspace(lo, hi, 3000)
    S_vals = np.array([S_func(xi) for xi in xs])
    dS_vals = np.array([dS_func(xi) for xi in xs])

    traj_x = [t[1] for t in trajectory]
    traj_S = [t[3] for t in trajectory]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                                         gridspec_kw={'height_ratios': [2, 1, 1]})
    fig.suptitle(
        f'Gradient Ascent: Finding Next Prime after {p}\n'
        f'Result: {next_p}  ({len(trajectory)} steps)',
        fontsize=14, fontweight='bold'
    )

    # Panel 1: S(x) + trajectory
    ax1.plot(xs, S_vals, color='#2196F3', linewidth=1.5, label='$S(x)$')
    ax1.plot(traj_x, traj_S, 'o-', color='#ff6b6b', markersize=3,
             linewidth=0.8, alpha=0.7, label='Particle trajectory')
    ax1.axvline(p, color='#4ecdc4', linestyle='--', alpha=0.5, label=f'Start: {p}')
    ax1.axvline(next_p, color='#00e676', linestyle='--', alpha=0.5,
                label=f'Found: {next_p}')
    ax1.set_ylabel('$S(x)$', fontsize=12)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, linestyle=':', alpha=0.3)

    # Panel 2: S'(x)
    ax2.plot(xs, dS_vals, color='#e91e63', linewidth=1.0, label="$S'(x)$")
    ax2.axhline(0, color='black', linestyle='--', alpha=0.4)
    ax2.set_ylabel("$S'(x)$", fontsize=12)
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(True, linestyle=':', alpha=0.3)

    # Panel 3: velocity
    traj_v = [t[2] for t in trajectory]
    ax3.plot(traj_x, traj_v, 's-', color='#9c27b0', markersize=2,
             linewidth=0.8, alpha=0.8)
    ax3.axhline(0, color='black', linestyle='--', alpha=0.4)
    ax3.set_xlabel('$x$', fontsize=12)
    ax3.set_ylabel('Velocity $v$', fontsize=12)
    ax3.grid(True, linestyle=':', alpha=0.3)

    outfile = f'gradient_ascent_{p}_to_{next_p}.png'
    plt.savefig(outfile, bbox_inches='tight', dpi=150)
    print(f"Plot saved to {outfile}")
    plt.close()


# ──────────────────────────────────────────────────────────────────────────────
# 5. Batch validation mode
# ──────────────────────────────────────────────────────────────────────────────

def validate_range(N_max, **kwargs):
    """Run the gradient ascent on every prime up to N_max and check correctness."""
    from math import isqrt

    def trial_division_primes(N):
        primes = []
        for n in range(2, N + 1):
            if n < 4:
                primes.append(n)
                continue
            is_p = True
            for d in range(2, isqrt(n) + 1):
                if n % d == 0:
                    is_p = False
                    break
            if is_p:
                primes.append(n)
        return primes

    primes = trial_division_primes(N_max)
    successes = 0
    failures = []

    for i in range(len(primes) - 1):
        p = primes[i]
        expected = primes[i + 1]
        try:
            found, _ = gradient_ascent_next_prime(p, **kwargs)
            if found == expected:
                successes += 1
                status = "✓"
            else:
                failures.append((p, expected, found))
                status = f"✗ (got {found})"
        except Exception as e:
            failures.append((p, expected, str(e)))
            status = f"✗ ({e})"
        print(f"  {p:>5} → {expected:>5}  {status}")

    total = len(primes) - 1
    print(f"\n{'='*50}")
    print(f"  Results: {successes}/{total} correct")
    if failures:
        print(f"  Failures: {failures}")
    print(f"{'='*50}")
    return successes, total, failures


# ──────────────────────────────────────────────────────────────────────────────
# 6. CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the next prime after a given prime using gradient "
                    "ascent on the continuous entropy signal S(x)."
    )
    parser.add_argument("prime", type=int,
                        help="A known prime number to start from.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print trajectory details.")
    parser.add_argument("--plot", action="store_true",
                        help="Save a visualization of the trajectory.")
    parser.add_argument("--validate", type=int, metavar="N",
                        help="Batch-validate on all primes up to N.")
    parser.add_argument("--gamma", type=float, default=0.05,
                        help="Learning rate (default: 0.05)")
    parser.add_argument("--mu", type=float, default=0.6,
                        help="Momentum decay coefficient (default: 0.6)")
    parser.add_argument("--beta", type=float, default=500_000.0,
                        help="Contrast amplification β (default: 500000)")
    parser.add_argument("--alpha", type=float, default=12.0,
                        help="Gaussian bump width α (default: 12)")
    args = parser.parse_args()

    p = args.prime

    if args.validate:
        print(f"Validating gradient ascent on all primes up to {args.validate} ...")
        validate_range(
            args.validate,
            beta=args.beta, alpha=args.alpha,
            gamma=args.gamma, mu=args.mu,
            verbose=args.verbose,
        )
        sys.exit(0)

    # Quick sanity check: is the input actually prime?
    d0 = entropy_deficit(p)
    if d0 > 1e-10:
        print(f"⚠  Warning: {p} does not appear to be prime (Δ({p}) = {d0:.6f}).")
        print(f"   The algorithm expects a prime as input.")
        sys.exit(1)

    print(f"Finding next prime after {p} via gradient ascent on S(x) ...")
    print(f"  Parameters: β = {args.beta:.0f}, α = {args.alpha}, "
          f"γ = {args.gamma}, μ = {args.mu}")

    next_p, trajectory = gradient_ascent_next_prime(
        p,
        beta=args.beta,
        alpha=args.alpha,
        gamma=args.gamma,
        mu=args.mu,
        verbose=args.verbose,
    )

    print(f"\n{'='*50}")
    print(f"  Next prime after {p} is: {next_p}")
    print(f"  Prime gap: {next_p - p}")
    print(f"  Trajectory length: {len(trajectory)} steps")
    print(f"{'='*50}")

    if args.plot:
        plot_trajectory(p, next_p, trajectory, args.beta, args.alpha)
