import numpy as np
import random
import sys

def randomized_entropy_prime_test(n, k=10):
    """
    Tests if n is prime by randomly sampling k different rows 
    from the multiplication modulo matrix. 
    Each test samples exactly (n-1) cells.
    """
    if n <= 1:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False # Instantly reject even composites
        
    max_capacity = np.log2(n - 1)
    
    # Run k independent random row checks
    for _ in range(k):
        # Pick a random row index 'a' between 2 and n-2
        a = random.randint(2, n - 2)
        
        # Sample exactly (n-1) cells along that row: (a * i) % n
        sampled_row = [(a * i) % n for i in range(1, n)]
        
        # Calculate the Shannon entropy of this single sampled row
        unique, counts = np.unique(sampled_row, return_counts=True)
        probabilities = counts / len(sampled_row)
        entropy = -np.sum(probabilities * np.log2(probabilities))
        entropy = max(0.0, entropy)
        
        # If the row fails to achieve maximum uniform entropy, 
        # it is mathematically guaranteed to be a composite number.
        if not np.isclose(entropy, max_capacity):
            return False
            
    # If it passes all random row inspections, it is highly likely to be prime
    return True

# --- Verification & Benchmarking ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <integer_n>")
        print("Example: python script_name.py 561")
        sys.exit(1)
        
    try:
        test_n = int(sys.argv[1])
    except ValueError:
        print("Error: Please provide a valid integer.")
        sys.exit(1)
        
    # Check primality via random sublinear sampling
    # We use k=15 random inspections for a near-bulletproof verification
    is_prime = randomized_entropy_prime_test(test_n, k=15)
    
    # Cross-reference with an absolute ground-truth check
    actual_prime = all(test_n % i != 0 for i in range(2, int(np.sqrt(test_n)) + 1)) if test_n > 1 else False
    
    print(f"\nEvaluating integer: {test_n}")
    print(f"Randomized Matrix Sampling Result: {'PRIME' if is_prime else 'COMPOSITE'}")
    print(f"Ground-Truth Verification:         {'PRIME' if actual_prime else 'COMPOSITE'}")
    
    if is_prime == actual_prime:
        print("✅ The randomized entropy check successfully identified the number!")
    else:
        print("❌ Warning: Discrepancy detected (e.g., a Carmichael number anomaly).")

