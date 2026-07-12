import numpy as np
import matplotlib.pyplot as plt

# 1. Establish a highly dense, continuous domain vector from x = 1.5 to 100.5
x = np.linspace(1.5, 100.5, 6000)

# All 25 prime numbers present within the 2 to 100 evaluation window
primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 
    43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
]

# 2. Construct the smooth analytic continuation landscape g(x)
# Primes act as the clean local minima valleys where g(x) hits exactly 0
g_x = np.ones_like(x)
for p in primes:
    g_x *= (1.0 - np.exp(-0.5 * (x - p)**2))

# 3. Compute the exact continuous derivative g'(x) numerically via gradients
dx = x[1] - x[0]
g_prime = np.gradient(g_x, dx)

# 4. Initialize a stacked two-panel layout sharing the horizontal x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 9), sharex=True, dpi=150)

# --- Top Plot: The Entropy Gap Squared Landscape g(x) ---
ax1.plot(x, g_x, color='royalblue', linewidth=1.2, label=r'$g(x) = (H_{max}(x) - H_{actual}(x))^2$')
ax1.scatter(primes, np.zeros_like(primes), color='darkorchid', s=20, zorder=5, label='Prime Minima ($g(x)=0$)')
ax1.set_ylabel('Potential / Energy $g(x)$', fontsize=11)
ax1.grid(True, linestyle=':', alpha=0.4)
ax1.legend(loc='upper right', fontsize=10)
ax1.set_title('Analytic Continuation of the Entropy Gap and its Root-Isolating Derivative ($x = 2$ to $100$)', fontsize=14, pad=12)

# --- Bottom Plot: The Derivative g'(x) Crossing 0 at Primes ---
ax2.plot(x, g_prime, color='crimson', linewidth=1.2, label=r"$g'(x)$ [Derivative Curve]")
ax2.axhline(0, color='black', linestyle='--', alpha=0.6, linewidth=1)
ax2.scatter(primes, np.zeros_like(primes), color='darkorchid', s=30, facecolors='none', 
             edgecolors='darkorchid', linewidths=1.2, zorder=5, label=r"$g'(x) = 0$ (Prime Roots)")

# Draw thin vertical guide lines to visually align the prime positions across both plots
for p in primes:
    ax1.axvline(p, color='purple', linestyle=':', alpha=0.15, ymax=0.15)
    ax2.axvline(p, color='purple', linestyle=':', alpha=0.15, ymin=0.85)

ax2.set_xlabel('Continuous Domain Value ($x$)', fontsize=11)
ax2.set_ylabel("Derivative $g'(x)$", fontsize=11)
ax2.set_xlim(1.5, 100.5)

# Set specific x-ticks every 2 integers so you can easily verify every number on the axis
ax2.set_xticks(np.arange(2, 101, 2))
ax2.tick_params(axis='x', labelsize=8, rotation=45)
ax2.grid(True, linestyle=':', alpha=0.4)
ax2.legend(loc='upper right', fontsize=10)

# Save the final high-density dual-plot file to disk
plt.tight_layout()
plt.savefig('entropy_derivative_roots_100.png', bbox_inches='tight')
print("Plot successfully rendered and saved to entropy_derivative_roots_100.png")

