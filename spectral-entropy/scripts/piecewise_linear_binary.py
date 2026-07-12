#!/usr/bin/env python3
"""
Piecewise-Linear Binary Encoding and Fourier Reconstruction
============================================================

Encodes a binary string as a continuous piecewise-linear slope-modulated curve:
  y'(x) = +1 for '1'
  y'(x) = -1 for '0'

Computes the Fourier coefficients of the resulting curve, shows the rate of
decay (which is O(1/k^2) due to continuity of y(x) but discontinuity of y'(x)),
and reconstructs the curve from the top K coefficients to illustrate the
reconstruction error vs coefficient count.

Saves the diagnostic plot to figures/piecewise_linear_encoding.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

def binary_to_piecewise_linear(bitstring, points_per_bit=100):
    """
    Converts a binary string to a piecewise-linear curve.
    Each '1' has slope +1, each '0' has slope -1.
    """
    n_bits = len(bitstring)
    n_samples = n_bits * points_per_bit
    x = np.linspace(0, n_bits, n_samples)
    y = np.zeros(n_samples)
    
    current_y = 0.0
    for idx, bit in enumerate(bitstring):
        slope = 1.0 if bit == '1' else -1.0
        # Fill the segment
        start_idx = idx * points_per_bit
        end_idx = (idx + 1) * points_per_bit
        segment_x = np.linspace(0, 1, points_per_bit)
        y[start_idx:end_idx] = current_y + slope * segment_x
        current_y += slope
        
    return x, y

def fourier_reconstruction(y, keep_modes=5):
    """
    Reconstructs the 1D signal using the first keep_modes Fourier coefficients.
    """
    n = len(y)
    fft_coeffs = np.fft.rfft(y)
    
    # Keep only the first keep_modes coefficients, zero out the rest
    fft_compressed = np.zeros_like(fft_coeffs)
    fft_compressed[:keep_modes] = fft_coeffs[:keep_modes]
    
    y_recon = np.fft.irfft(fft_compressed, n)
    return y_recon, fft_coeffs

if __name__ == "__main__":
    # Test bitstring: Alternating and uniform patterns
    BITSTRING = "11001010111001"
    print(f"Encoding bitstring: '{BITSTRING}'")
    
    x, y = binary_to_piecewise_linear(BITSTRING)
    
    # Perform reconstructions with different number of modes
    modes_to_test = [3, 8, 15, 30]
    reconstructions = {}
    for k in modes_to_test:
        y_rec, coeffs = fourier_reconstruction(y, keep_modes=k)
        reconstructions[k] = y_rec
        
    # Also get all coefficients to plot the decay
    _, fft_all = fourier_reconstruction(y, keep_modes=len(y)//2)
    mags = np.abs(fft_all)
    
    print("Plotting figures...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), dpi=150)
    
    # Top Panel: Piecewise-Linear Curve and Reconstructions
    ax1.plot(x, y, label="Original Slope-Encoded Curve", color='black', linewidth=2.5)
    colors = ['#ff6b6b', '#4ecdc4', '#ff9800', '#2196F3']
    for idx, k in enumerate(modes_to_test):
        ax1.plot(x, reconstructions[k], label=f"Fourier Reconstruction (K={k} modes)", 
                 color=colors[idx], linestyle='--', alpha=0.9, linewidth=1.5)
        
    # Annotate the bits above the segments
    n_bits = len(BITSTRING)
    for idx, bit in enumerate(BITSTRING):
        ax1.axvline(x=idx, color='gray', linestyle=':', alpha=0.4)
        ax1.text(idx + 0.5, np.max(y) + 0.2, bit, fontsize=12, fontweight='bold', 
                 ha='center', va='bottom', color='darkgreen' if bit == '1' else 'darkred')
    ax1.axvline(x=n_bits, color='gray', linestyle=':', alpha=0.4)
    
    ax1.set_xlabel("Bit Index / Continuous Coordinate x", fontsize=12)
    ax1.set_ylabel("Amplitude y(x)", fontsize=12)
    ax1.set_title(f"Sinusoidal/Fourier Curve Encoding of Bitstring: {BITSTRING}", fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left')
    
    # Bottom Panel: Fourier Coefficient Decay
    ax2.loglog(np.arange(1, len(mags) + 1), mags, 'o-', color='#ab47bc', label="Empirical Fourier Coefficients")
    # Reference decay line O(1/k^2)
    ref_k = np.arange(1, len(mags) + 1)
    ref_decay = mags[0] / (ref_k ** 2)
    ax2.loglog(ref_k, ref_decay, 'r--', label="Theoretical Decay O(1/k^2)")
    
    ax2.set_xlabel("Fourier Mode Index k", fontsize=12)
    ax2.set_ylabel("Coefficient Magnitude |c_k|", fontsize=12)
    ax2.set_title("Fourier Coefficient Decay (Rate of Information Dispersal)", fontsize=14, fontweight='bold')
    ax2.grid(True, which="both", linestyle=':', alpha=0.5)
    ax2.legend()
    
    # Create directory if it doesn't exist
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/piecewise_linear_encoding.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
