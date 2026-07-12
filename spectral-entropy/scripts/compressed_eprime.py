#!/usr/bin/env python3
"""
Compressed Algebraic Primality Test
====================================

Validates primality by randomly sampling rows of the modular multiplication
table and checking whether each row is a permutation of {1, ..., n-1}.

A row indexed by 'a' is a permutation iff gcd(a, n) = 1.  For primes,
every a in {1, ..., n-1} satisfies this; for composites, a fraction of
rows will fail.  By sampling k random rows, the probability of a false
positive (composite passing as prime) is at most (1 - 1/p)^k where p is
the smallest prime factor of n.

This is O(k log n) time and O(1) space.

Usage:
    python compressed_eprime.py <integer_n> [k]
"""

import random
import sys
from math import gcd


def compressed_algebraic_prime_test(n, k=15):
    """
    Validates primality by checking if randomly sampled rows
    of the modular multiplication table are permutations.

    A row 'a' is a permutation of {1, ..., n-1} iff gcd(a, n) = 1.
    For prime n, this holds for all a in {1, ..., n-1}.
    For composite n, at least one a will have gcd(a, n) > 1.

    Parameters
    ----------
    n : int
        The integer to test.
    k : int
        Number of random rows to sample (default: 15).

    Returns
    -------
    bool
        True if n is probably prime, False if definitely composite.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    for _ in range(k):
        a = random.randint(2, n - 2)
        if gcd(a, n) != 1:
            return False  # Found a zero divisor → composite

    return True


# --- Terminal Execution ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compressed_eprime.py <integer_n> [k]")
        sys.exit(1)

    test_n = int(sys.argv[1])
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    is_prime = compressed_algebraic_prime_test(test_n, k)

    print(f"\nEvaluating integer: {test_n}")
    print(f"Compressed Matrix Test Result: {'PRIME' if is_prime else 'COMPOSITE'}")
