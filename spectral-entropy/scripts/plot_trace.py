import numpy as np
import matplotlib.pyplot as plt

def calculate_submatrix_trace_entropy(n):
    if n <= 1:
        return 0, 0
        
    # 1. Compute the submatrix dimension s = floor(sqrt(n)) + 1
    s = int(np.floor(np.sqrt(n))) + 1
    
    # 2. Extract the trace elements from the 1 to s slice of the original matrix
    diagonal_elements = [(i * i) % n for i in range(1, s + 1)]
    
    # 3. Calculate empirical frequencies of unique remainders
    unique, counts = np.unique(diagonal_elements, return_counts=True)
    probabilities = counts / len(diagonal_elements)
    
    # 4. Compute Shannon entropy in bits (base 2)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    entropy = max(0.0, entropy)
    
    # 5. Compute the theoretical uniform maximum capacity for a sequence of length s
    max_theoretical = np.log2(s)
    
    return entropy, max_theoretical

def get_primes_up_to(limit):
    primes = []
    for num in range(2, limit + 1):
        if all(num % i != 0 for i in range(2, int(np.sqrt(num)) + 1)):
            primes.append(num)
    return primes

# --- Configuration & Calculations ---
max_limit = 500
n_values = np.arange(2, max_limit + 1)
primes_set = set(get_primes_up_to(max_limit))

sub_trace_entropies = []
max_theoreti_list = []
false_positive_n = []
false_positive_y = []

# Evaluate every number to look for false positives
for n in n_values:
    entropy, max_theoretical = calculate_submatrix_trace_entropy(n)
    sub_trace_entropies.append(entropy)
    max_theoreti_list.append(max_theoretical)
    
    # Classification Test: Does actual entropy equal maximum entropy?
    is_max_entropy = np.isclose(entropy, max_theoretical)
    is_composite = n not in primes_set
    
    # If a composite fakes maximum entropy, it's a False Positive
    if is_max_entropy and is_composite:
        false_positive_n.append(n)
        false_positive_y.append(entropy)

# Extract standalone prime arrays for clear plotting markers
primes_list = sorted(list(primes_set))
prime_entropies = [calculate_submatrix_trace_entropy(p)[0] for p in primes_list]

# --- Print Diagnostics to Terminal ---
total_composites = len(n_values) - len(primes_list)
print(f"Total composites evaluated: {total_composites}")
print(f"False Positives found: {len(false_positive_n)} out of {total_composites}")
print(f"False Positive Numbers: {false_positive_n[:15]}... (and more)")

# --- Visualization Layout ---
plt.figure(figsize=(14, 7), dpi=150)

# 1. Plot the continuous trace background
plt.plot(n_values, sub_trace_entropies, label="Actual Submatrix Trace Entropy", 
         color="royalblue", alpha=0.4, linewidth=1, zorder=1)

# 2. Plot the theoretical limit line
plt.plot(n_values, max_theoreti_list, label="Theoretical Submatrix Maximum: log2(s)", 
         color="crimson", linestyle="--", alpha=0.6, linewidth=1.5, zorder=2)

# 3. Scatter plot for the True Primes
plt.scatter(primes_list, prime_entropies, color="darkorchid", zorder=4, s=20, alpha=0.9, label="True Prime Numbers")

# 4. OVERLAY: Scatter plot for False Positives (Composites hitting the max line)
plt.scatter(false_positive_n, false_positive_y, color="darkorange", zorder=3, s=40, marker="x", alpha=0.8, label="False Positives (Composites)")

# Graph styling adjustments
plt.title("Submatrix Trace Entropy Primality Test: True Primes vs False Positives (n=2 to 500)", fontsize=12, pad=15)
plt.xlabel("Integer Value (n)", fontsize=12)
plt.ylabel("Entropy (Bits)", fontsize=12)
plt.xlim(2, max_limit + 10)
plt.grid(True, linestyle=":", alpha=0.5)
plt.legend(loc="lower right", fontsize=11)

# Save the canvas
plt.savefig("submatrix_trace_entropy_false_positives.png", bbox_inches='tight')
print("Plot successfully rendered and saved to submatrix_trace_entropy_false_positives.png")

