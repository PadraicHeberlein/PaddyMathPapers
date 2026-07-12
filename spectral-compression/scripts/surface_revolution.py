#!/usr/bin/env python3
"""
3D Spiral Transform and Surface Reconstruction Tool
===================================================

Generates a generalized surface of revolution (e.g. a vase), winds a 3D spiral
path along the surface, extracts the 1D radius signal, compresses it in the
Fourier domain, and reconstructs the 3D surface from the compressed signal.

Saves a publication-quality diagnostic figure to figures/spiral_transform_reconstruction.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def generate_vase_surface(N_s=100, N_theta=100):
    """Generates a standard vase-like surface of revolution."""
    s = np.linspace(0, 1, N_s)
    theta = np.linspace(0, 2*np.pi, N_theta)
    
    # Radius profile: a base radius with sinusoidal variations
    r_s = 1.0 + 0.3 * np.sin(2 * np.pi * s) + 0.1 * np.cos(6 * np.pi * s)
    
    # Grid coordinates
    S, Theta = np.meshgrid(s, theta)
    R_S = 1.0 + 0.3 * np.sin(2 * np.pi * S) + 0.1 * np.cos(6 * np.pi * S)
    
    X = R_S * np.cos(Theta)
    Y = R_S * np.sin(Theta)
    Z = S * 3.0 # Scale height for display
    
    return S, Theta, X, Y, Z, s, r_s

def sample_spiral_path(s_range, n_windings=20, n_samples=1000):
    """Samples points along a helical spiral path wound around the vase."""
    t = np.linspace(0, 1, n_samples)
    
    # Path coordinates
    s_path = t * (s_range[1] - s_range[0]) + s_range[0]
    theta_path = 2 * np.pi * n_windings * t
    
    # Radius along path
    r_path = 1.0 + 0.3 * np.sin(2 * np.pi * s_path) + 0.1 * np.cos(6 * np.pi * s_path)
    
    # 3D points
    x_path = r_path * np.cos(theta_path)
    y_path = r_path * np.sin(theta_path)
    z_path = s_path * 3.0
    
    return t, s_path, theta_path, r_path, x_path, y_path, z_path

def compress_signal(signal, keep_fraction=0.05):
    """Compresses a 1D signal using FFT by keeping the top fraction of coefficients."""
    n = len(signal)
    fft_coeffs = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n)
    
    # Determine threshold
    magnitudes = np.abs(fft_coeffs)
    sorted_mags = np.sort(magnitudes)
    cutoff_idx = int((1 - keep_fraction) * len(magnitudes))
    threshold = sorted_mags[cutoff_idx]
    
    # Zero out small coefficients
    fft_compressed = fft_coeffs.copy()
    fft_compressed[magnitudes < threshold] = 0.0
    
    # Reconstruct
    reconstructed = np.fft.irfft(fft_compressed, n)
    return reconstructed, fft_coeffs, fft_compressed

if __name__ == "__main__":
    print("Generating 3D surface geometry...")
    S, Theta, X, Y, Z, s, r_s = generate_vase_surface()
    
    # Winding parameters
    N_WINDINGS = 15
    N_SAMPLES = 1024
    KEEP_FRACTION = 0.03 # Keep only top 3% of coefficients
    
    print(f"Sampling spiral path (windings={N_WINDINGS}, samples={N_SAMPLES})...")
    t, s_p, theta_p, r_p, x_p, y_p, z_p = sample_spiral_path((0, 1), n_windings=N_WINDINGS, n_samples=N_SAMPLES)
    
    print(f"Compressing radius signal (keeping {KEEP_FRACTION*100:.1f}% coefficients)...")
    r_recon, coeffs, coeffs_comp = compress_signal(r_p, keep_fraction=KEEP_FRACTION)
    
    # Reconstruct 3D path from compressed radius
    x_recon = r_recon * np.cos(theta_p)
    y_recon = r_recon * np.sin(theta_p)
    z_recon = s_p * 3.0
    
    # Reconstruct the continuous 3D surface from the compressed path radius
    # By mapping the 1D compressed signal back to 2D using the spiral winding mapping
    # Since r_recon is sampled along theta_p = 2*pi*W*t, we can interpolate it for any (s, theta)
    r_surface_recon = np.zeros_like(S)
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            # Find the parameter t corresponding to this S[i,j]
            # Since S[i,j] is s, and s = t, t = S[i,j]
            t_val = S[i,j]
            # Interpolate r_recon at t_val
            r_surface_recon[i,j] = np.interp(t_val, t, r_recon)
            
    X_recon = r_surface_recon * np.cos(Theta)
    Y_recon = r_surface_recon * np.sin(Theta)
    Z_recon = S * 3.0
    
    print("Plotting results...")
    fig = plt.figure(figsize=(24, 10), dpi=150)
    
    # Panel 1: Original Surface and Spiral Path
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.3, edgecolor='none')
    ax1.plot3D(x_p, y_p, z_p, color='red', linewidth=2.5, label='Spiral Path')
    ax1.set_title("Original Surface with Spiral Path", fontsize=14, fontweight='bold')
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_zlabel("Z (Height)")
    ax1.legend()
    
    # Panel 2: 1D Radius Signal Compression
    ax2 = fig.add_subplot(132)
    ax2.plot(t, r_p, label="Original Radius r(t)", color='#2196F3', linewidth=2)
    ax2.plot(t, r_recon, label=f"Compressed ({KEEP_FRACTION*100:.0f}% modes)", color='#ff9800', linestyle='--', linewidth=2)
    ax2.set_xlabel("Spiral Parameter t", fontsize=12)
    ax2.set_ylabel("Radius", fontsize=12)
    ax2.set_title("1D Spiral Radius Signal & Fourier Approximation", fontsize=14, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend()
    
    # Panel 3: Reconstructed Surface
    ax3 = fig.add_subplot(133, projection='3d')
    ax3.plot_surface(X_recon, Y_recon, Z_recon, cmap='plasma', alpha=0.5, edgecolor='none')
    ax3.plot3D(x_recon, y_recon, z_recon, color='blue', linewidth=1.5, label='Reconstructed Path')
    ax3.set_title("Reconstructed Surface from Compressed Signal", fontsize=14, fontweight='bold')
    ax3.set_xlabel("X")
    ax3.set_ylabel("Y")
    ax3.set_zlabel("Z (Height)")
    ax3.legend()
    
    # Create directory if it doesn't exist
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/spiral_transform_reconstruction.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
