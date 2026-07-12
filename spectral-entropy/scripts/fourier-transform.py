import numpy as np
import matplotlib.pyplot as plt

def get_primes_up_to(limit):
    """Generates a list of all prime numbers up to a specified limit."""
    primes = []
    for num in range(2, limit + 1):
        if all(num % i != 0 for i in range(2, int(np.sqrt(num)) + 1)):
            primes.append(num)
    return primes

# 1. Establish a massive, high-density domain vector from x = 2 to 1000
# 50,000 points ensures incredibly sharp frequency lines in the FFT
max_limit = 1000
x = np.linspace(2.0, float(max_limit), 50000)
primes = get_primes_up_to(max_limit)

# 2. Reconstruct the continuous potential energy landscape g(x) up to 1000
g_x = np.ones_like(x)
for p in primes:
    g_x *= (1.0 - np.exp(-0.5 * (x - p)**2))

# 3. Compute the exact continuous derivative g'(x) via localized gradients
dx = x[1] - x[0]
g_prime = np.gradient(g_x, dx)

# 4. Execute the Fast Fourier Transform (FFT) on the expanded derivative signal
fft_values = np.fft.fft(g_prime)
frequencies = np.fft.fftfreq(len(x), d=dx)

# 5. Isolate positive frequencies and focus on the structural resonance spectrum
# Standardizing the cutoff at 3.0 cycles/unit highlights the primary interference modes
spectrum_mask = (frequencies >= 0) & (frequencies <= 3.0)
plot_freqs = frequencies[spectrum_mask]
plot_magnitude = np.abs(fft_values[spectrum_mask])

# 6. Configure the visualization canvas
plt.figure(figsize=(14, 6), dpi=150)
plt.plot(plot_freqs, plot_magnitude, color='darkgreen', linewidth=1.2, 
         label=r'$\mathcal{F}\{g\'(x)\}$ (Spectral Magnitude)')

# Style configurations for a wide-horizon graph
plt.title(f"Fourier Transform of the Entropy Gap Derivative $g'(x)$ from $x=2$ to {max_limit}", fontsize=13, pad=15)
plt.xlabel("Frequency (Cycles per Unit Interval)", fontsize=11)
plt.ylabel("Spectral Amplitude / Magnitude", fontsize=11)
plt.grid(True, linestyle=':', alpha=0.4)
plt.xlim(0, 3.0)
plt.legend(loc='upper right', fontsize=10)

# Save and render the plot image
plt.tight_layout()
plt.savefig('g_prime_fourier_transform_1000.png', bbox_inches='tight')
print("Fourier Transform successfully calculated and saved to g_prime_fourier_transform_1000.png")

