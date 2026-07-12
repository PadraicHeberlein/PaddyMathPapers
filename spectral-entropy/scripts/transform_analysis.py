#!/usr/bin/env python3
"""
transform_analysis.py
=====================

Investigates:
1. S_n(0) = - \sum_{j,k} e^{-2\pi i (jk \bmod n)/n}
2. Laurent expansion of S_n(z) at z = \infty:
   S_n(z) = \sum_{m=0}^\infty C_m(n) z^{-(m+1)}
   where C_m(n) = \sum_{j,k=1}^{n-1} e^{2\pi i m (jk \bmod n)/n}
3. The relationship between C_m(n) and Ramanujan sums or character sums.
"""

import numpy as np
from math import gcd

def ramanujan_sum(q, n):
    """
    Computes Ramanujan's sum c_q(n) = \sum_{1 <= a <= q, gcd(a,q)=1} e^{2\pi i a n / q}.
    Using Kluyver's formula: c_q(n) = \sum_{d | gcd(n,q)} d * \mu(q/d)
    """
    # Simple direct computation
    ans = 0.0
    for a in range(1, q + 1):
        if gcd(a, q) == 1:
            ans += np.exp(2j * np.pi * a * n / q)
    return ans

def evaluate_S_n_0(n):
    """
    S_n(0) = \sum_{j=1}^{n-1} \sum_{k=1}^{n-1} -e^{-2\pi i (jk \bmod n)/n}
    """
    ans = 0.0
    for j in range(1, n):
        for k in range(1, n):
            ans += -np.exp(-2j * np.pi * ((j * k) % n) / n)
    return np.round(ans.real, 10) + np.round(ans.imag, 10)*1j

def get_coefficients_C_m(n, max_m=10):
    """
    C_m(n) = \sum_{j=1}^{n-1} \sum_{k=1}^{n-1} e^{2\pi i m (jk \bmod n)/n}
    """
    coeffs = []
    for m in range(max_m):
        val = 0.0
        for j in range(1, n):
            for k in range(1, n):
                val += np.exp(2j * np.pi * m * ((j * k) % n) / n)
        coeffs.append(np.round(val.real, 10) + np.round(val.imag, 10)*1j)
    return coeffs

if __name__ == "__main__":
    print(f"{'='*60}")
    print("Evaluating S_n(0) for small values of n")
    print(f"{'='*60}")
    print(f" {'n':>4}   {'S_n(0)':>20}   {'Is Prime?':>10}")
    print("-" * 45)
    for n in range(2, 25):
        val = evaluate_S_n_0(n)
        is_p = "Prime" if all(n % d != 0 for d in range(2, int(np.sqrt(n))+1)) else "Composite"
        print(f" {n:>4}   {str(val):>20}   {is_p:>10}")

    print("\n" + f"{'='*60}")
    print("Evaluating Coefficients C_m(n) for n = 5 (Prime)")
    print(f"{'='*60}")
    coeffs_5 = get_coefficients_C_m(5, 12)
    for m, c in enumerate(coeffs_5):
        print(f"  C_{m}(5) = {c}")

    print("\n" + f"{'='*60}")
    print("Evaluating Coefficients C_m(n) for n = 6 (Composite)")
    print(f"{'='*60}")
    coeffs_6 = get_coefficients_C_m(6, 12)
    for m, c in enumerate(coeffs_6):
        print(f"  C_{m}(6) = {c}")

    print("\n" + f"{'='*60}")
    print("Comparing C_m(n) with number-theoretic values")
    print(f"{'='*60}")
    # Let's see: C_m(n) is the sum over all 1 <= j,k <= n-1 of e^{2\pi i m (jk)/n}
    # For a fixed j, \sum_{k=1}^{n-1} e^{2\pi i (j m) k / n} is:
    # Let g = gcd(j m, n).
    # If n | j m, the sum is n - 1.
    # Otherwise, it is -1.
    # Let's prove this!
    # \sum_{k=0}^{n-1} e^{2\pi i (jm) k / n} is n if n | jm, else 0.
    # Since we sum k from 1 to n-1 (omitting k=0), the sum is:
    # n - 1  if n | jm
    # -1     if n ∤ jm
    #
    # Therefore:
    # C_m(n) = \sum_{j=1}^{n-1} [ (n - 1) if n | jm else -1 ]
    # Let K_m = count of j in {1, ..., n-1} such that n | jm.
    # Then C_m(n) = K_m * (n - 1) + (n - 1 - K_m) * (-1)
    #             = K_m * n - (n - 1)
    # Since n | jm is equivalent to (n / gcd(m, n)) | j,
    # the number of such j in {1, ..., n-1} is exactly gcd(m, n) - 1.
    # So K_m = gcd(m, n) - 1.
    # Therefore, C_m(n) = (gcd(m, n) - 1) * n - n + 1
    #                   = n * gcd(m, n) - 2n + 1.
    # Let's check this formula!
    for n in [5, 6, 7, 8, 9, 10]:
        print(f"\nTesting formula C_m(n) = n * gcd(m, n) - 2n + 1 for n = {n}")
        coeffs = get_coefficients_C_m(n, 6)
        for m in range(6):
            formula_val = n * gcd(m, n) - 2 * n + 1
            print(f"  m = {m}: Empirical C_m = {coeffs[m].real:.0f}, Formula = {formula_val}")
