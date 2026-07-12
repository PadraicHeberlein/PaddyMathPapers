#!/usr/bin/env python3
"""
FFT Period and Phase Detection for Binary Sequences
===================================================

Performs spectral period detection on binary strings by mapping {0, 1} to {-1, +1}
and computing the Power Spectral Density (PSD). Detects the dominant period and
optimal phase shift, comparing the results against the block entropy sweep.

Saves the diagnostic plot to figures/fft_period_detection.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_period_fft(bitstring):
    """
    Maps bitstring to {-1, +1}, performs FFT, and extracts dominant frequency
    and corresponding period and phase.
    """
    # Map to bipolar
    signal = np.array([1.0 if b == '1' else -1.0 for b in bitstring])
    n = len(signal)
    
    # Compute FFT
    fft_vals = np.fft.rfft(signal - np.mean(signal)) # Subtract mean to remove DC component
    psd = np.abs(fft_vals) ** 2
    freqs = np.fft.rfftfreq(n)
    
    # Exclude DC frequency (index 0)
    peak_idx = np.argmax(psd[1:]) + 1
    peak_freq = freqs[peak_idx]
    
    # Period (in bits)
    detected_period = 1.0 / peak_freq if peak_freq > 0 else float('inf')
    
    # Phase shift to optimize alignment
    phase = np.angle(fft_vals[peak_idx])
    optimal_shift = int(np.round(phase * detected_period / (2 * np.pi))) % int(np.round(detected_period))
    
    return freqs, psd, detected_period, optimal_shift, peak_idx

if __name__ == "__main__":
    # Test case: Period-3 sequence
    BITSTRING = "001" * 100
    print("Analyzing period-3 sequence...")
    
    freqs, psd, period, shift, peak_idx = detect_period_fft(BITSTRING)
    print(f"  Detected Peak Frequency: {freqs[peak_idx]:.4f}")
    print(f"  Detected Period:         {period:.2f} bits (Expected: 3.00)")
    print(f"  Detected Optimal Shift:  {shift} (Expected: 0)")
    
    print("Plotting FFT Power Spectral Density...")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    
    ax.plot(freqs, psd, color='#673ab7', linewidth=2.5, label="Power Spectral Density")
    ax.axvline(x=freqs[peak_idx], color='#ff5722', linestyle='--', linewidth=2, 
               label=f"Dominant Peak (f = {freqs[peak_idx]:.3f}, T = {period:.1f} bits)")
    
    ax.set_xlabel("Frequency (cycles per bit)", fontsize=12)
    ax.set_ylabel("Power Spectral Density", fontsize=12)
    ax.set_title("Spectral Period Detection via FFT Power Spectrum", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(fontsize=11)
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/fft_period_detection.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
