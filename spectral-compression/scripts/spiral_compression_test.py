#!/usr/bin/env python3
import sys
import numpy as np
import matplotlib.pyplot as plt
import os

def s_curve_axis(s):
    """S-curve axis in 3D."""
    x = 0.5 * np.sin(np.pi * s)
    y = 0.2 * np.cos(2 * np.pi * s) - 0.2
    z = 3.0 * s
    return np.array([x, y, z])

def bishop_frame_discrete(gamma_fn, s):
    """
    Computes the Bishop Frame (Parallel Transport Frame) using discrete parallel transport.
    """
    pts = gamma_fn(s)
    N_pts = len(s)
    
    T = np.zeros_like(pts)
    N = np.zeros_like(pts)
    B = np.zeros_like(pts)
    
    # Compute tangents using central differences
    h = 1e-4
    for i in range(N_pts):
        v = (gamma_fn(s[i] + h) - gamma_fn(s[i] - h)) / (2 * h)
        T[:, i] = v / np.linalg.norm(v)
        
    # Initial Normal: pick arbitrary vector perpendicular to T[:, 0]
    t0 = T[:, 0]
    n0 = np.array([1.0, 0.0, 0.0])
    if np.abs(np.dot(t0, n0)) > 0.9:
        n0 = np.array([0.0, 1.0, 0.0])
    n0 = n0 - np.dot(t0, n0) * t0
    n0 = n0 / np.linalg.norm(n0)
    
    N[:, 0] = n0
    B[:, 0] = np.cross(t0, n0)
    
    # Parallel transport
    for i in range(1, N_pts):
        t1 = T[:, i-1]
        t2 = T[:, i]
        n1 = N[:, i-1]
        
        cross_t = np.cross(t1, t2)
        dot_t = np.dot(t1, t2)
        
        # If tangents are parallel, no rotation needed
        if np.linalg.norm(cross_t) < 1e-8:
            n2 = n1
        else:
            axis = cross_t / np.linalg.norm(cross_t)
            angle = np.arccos(np.clip(dot_t, -1.0, 1.0))
            
            # Rodrigues' rotation formula for n1
            n2 = n1 * np.cos(angle) + np.cross(axis, n1) * np.sin(angle) + axis * np.dot(axis, n1) * (1 - np.cos(angle))
            
        # Orthogonalize just in case of numerical drift
        n2 = n2 - np.dot(t2, n2) * t2
        n2 = n2 / np.linalg.norm(n2)
        
        N[:, i] = n2
        B[:, i] = np.cross(t2, n2)
        
    return T, N, B

def surface_radius(s, theta):
    """A complex radius function depending on both longitudinal and azimuthal angles."""
    # Base vase shape + ripples + ridges
    base = 0.6 + 0.2 * np.sin(np.pi * s)
    ridges = 0.05 * np.cos(5 * theta)
    ripples = 0.02 * np.sin(20 * np.pi * s)
    return base + ridges + ripples

def generate_surface(N_s=100, N_theta=100):
    s = np.linspace(0, 1, N_s)
    theta = np.linspace(0, 2*np.pi, N_theta)
    
    axis_points = s_curve_axis(s)
    T, N, B = bishop_frame_discrete(s_curve_axis, s)
    
    X = np.zeros((N_s, N_theta))
    Y = np.zeros((N_s, N_theta))
    Z = np.zeros((N_s, N_theta))
    
    for i in range(N_s):
        p = axis_points[:, i]
        n_vec = N[:, i]
        b_vec = B[:, i]
        for j in range(N_theta):
            th = theta[j]
            r = surface_radius(s[i], th)
            pt = p + r * (np.cos(th) * n_vec + np.sin(th) * b_vec)
            X[i, j] = pt[0]
            Y[i, j] = pt[1]
            Z[i, j] = pt[2]
            
    return X, Y, Z

def main():
    print("Generating 3D reference surface...")
    X, Y, Z = generate_surface(200, 200)
    
    # 1. Forward Transform (Sampling the Spiral)
    N_WINDINGS = 60
    N_SAMPLES = 8192
    
    print(f"Extracting 1D spiral signal with {N_WINDINGS} windings...")
    t = np.linspace(0, 1, N_SAMPLES)
    theta_path = 2 * np.pi * N_WINDINGS * t
    r_path = surface_radius(t, theta_path)
    
    # 2. Spectral Compression
    print("Performing Spectral Compression...")
    fft_coeffs = np.fft.rfft(r_path)
    mags = np.abs(fft_coeffs)
    
    ratios = [0.01, 0.05, 0.10, 0.20]
    compressed_signals = {}
    
    for ratio in ratios:
        n_keep = int(len(fft_coeffs) * ratio)
        threshold = np.sort(mags)[-n_keep]
        
        mask = mags >= threshold
        coeffs_compressed = fft_coeffs * mask
        r_comp = np.fft.irfft(coeffs_compressed, n=N_SAMPLES)
        compressed_signals[ratio] = r_comp
        
        # Calculate error on 1D signal
        rmse_1d = np.sqrt(np.mean((r_comp - r_path)**2))
        print(f"Retention: {ratio*100:4.1f}% | RMSE 1D: {rmse_1d:.4f} | Coeffs kept: {n_keep}/{len(fft_coeffs)}")

    # 3. Inverse Transform (Reconstruction) for Visualization
    plot_ratio = 0.05 # Visualize the 5% retention
    r_comp_plot = compressed_signals[plot_ratio]
    
    # Get moving frame along the path
    axis_p = s_curve_axis(t)
    T, N, B = bishop_frame_discrete(s_curve_axis, t)
    
    X_recon = np.zeros(N_SAMPLES)
    Y_recon = np.zeros(N_SAMPLES)
    Z_recon = np.zeros(N_SAMPLES)
    
    X_orig = np.zeros(N_SAMPLES)
    Y_orig = np.zeros(N_SAMPLES)
    Z_orig = np.zeros(N_SAMPLES)
    
    errors = np.zeros(N_SAMPLES)
    
    for i in range(N_SAMPLES):
        p = axis_p[:, i]
        th = theta_path[i]
        n_vec = N[:, i]
        b_vec = B[:, i]
        
        # Reconstructed point
        pt_recon = p + r_comp_plot[i] * (np.cos(th) * n_vec + np.sin(th) * b_vec)
        X_recon[i], Y_recon[i], Z_recon[i] = pt_recon
        
        # Original point
        pt_orig = p + r_path[i] * (np.cos(th) * n_vec + np.sin(th) * b_vec)
        X_orig[i], Y_orig[i], Z_orig[i] = pt_orig
        
        errors[i] = np.linalg.norm(pt_recon - pt_orig)

    print(f"3D Reconstruction Error at {plot_ratio*100}% retention: Mean={np.mean(errors):.4f}, Max={np.max(errors):.4f}")

    # 4. Visualization
    print("Generating visualizations...")
    fig = plt.figure(figsize=(18, 6), dpi=150)
    
    # Panel 1: Original Surface
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9, edgecolor='none')
    ax1.set_title("Original 3D Surface\n(Ribbed Vase on Curved Axis)", fontsize=12)
    ax1.axis('off')
    
    # Panel 2: 1D Signal & Compression
    ax2 = fig.add_subplot(132)
    # Plot a small segment to see the difference clearly
    segment = slice(1000, 1500)
    ax2.plot(t[segment], r_path[segment], 'k-', alpha=0.5, label='Original $r(t)$', linewidth=2)
    ax2.plot(t[segment], r_comp_plot[segment], 'r--', label=f'Compressed $r_{{comp}}(t)$ ({plot_ratio*100}%)', linewidth=1.5)
    ax2.set_title("1D Spiral Signal Segment", fontsize=12)
    ax2.set_xlabel("t")
    ax2.set_ylabel("Radius")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Reconstructed Surface Scatter with Error Heatmap
    ax3 = fig.add_subplot(133, projection='3d')
    sc = ax3.scatter(X_recon, Y_recon, Z_recon, c=errors, cmap='inferno', s=1, alpha=0.8)
    plt.colorbar(sc, ax=ax3, label='Reconstruction Error (Euclidean Dist)', shrink=0.5)
    ax3.set_title(f"Reconstructed Surface\n({plot_ratio*100}% Coefficients Kept)", fontsize=12)
    ax3.axis('off')
    
    plt.tight_layout()
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/spiral_compression_test.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Saved figure to {outfile}")

if __name__ == "__main__":
    main()
