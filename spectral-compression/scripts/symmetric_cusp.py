#!/usr/bin/env python3
"""
Symmetric 2D Ribbon Cusp Demonstration
======================================

Demonstrates how a symmetric offset r_L(s) = r_R(s) = r(s) around a curved axis g(s)
produces a smooth outer boundary f(s) on the convex side, but a sharp cusp/indentation
on the concave side h(s) when the offset r(s) approaches the local radius of curvature 1/kappa.

Saves the plot to figures/symmetric_cusp.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

def axis_curve(s):
    # A curve that bends to the left (concave to the right)
    # Let's make it a parabola-like shape: x = -1.2 * (y - 0.5)^2
    y = s
    x = -0.8 * (s - 0.5)**2
    return np.column_stack((x, y))

def compute_tangents_normals(g):
    dg = np.zeros_like(g)
    dg[1:-1] = (g[2:] - g[:-2]) / 2.0
    dg[0] = g[1] - g[0]
    dg[-1] = g[-1] - g[-2]
    
    speeds = np.linalg.norm(dg, axis=1, keepdims=True)
    T = dg / speeds
    # Normal pointing to the right (concave side of our curve)
    N = np.column_stack((T[:, 1], -T[:, 0]))
    return T, N

if __name__ == "__main__":
    n_pts = 300
    s_vals = np.linspace(0.0, 1.0, n_pts)
    
    g = axis_curve(s_vals)
    T, N = compute_tangents_normals(g)
    
    # Let's compute curvature kappa = |dT/ds| / |dg/ds|
    # For a simple parabola x = -0.8*(y-0.5)^2, the curvature is highest in the middle (s=0.5)
    # Let's choose a symmetric radius function r(s) that is constant or slowly varying
    # r(s) = 0.28
    r = 0.28 * np.ones_like(s_vals)
    
    # Left boundary (convex side, normal points away from center of curvature)
    f = g - N * r[:, np.newaxis]
    # Right boundary (concave side, normal points towards center of curvature)
    h = g + N * r[:, np.newaxis]
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    
    ax.plot(g[:, 0], g[:, 1], 'k--', linewidth=2, label="Axis Curve g(s)")
    ax.plot(f[:, 0], f[:, 1], '#2196f3', linewidth=2.5, label="Left Boundary f(s) (Convex side)")
    ax.plot(h[:, 0], h[:, 1], '#ff9800', linewidth=2.5, label="Right Boundary h(s) (Concave side)")
    
    # Draw normal lines at top, middle, bottom
    sample_indices = [30, 150, 270]
    labels_L = [r"$c_1$", r"$c_i$", r"$c_5$"]
    labels_R = [r"$b$", r"$c_i$", r"$a$"]
    colors = ['#e91e63', '#9c27b0', '#009688']
    
    for idx, sample_idx in enumerate(sample_indices):
        p_g = g[sample_idx]
        p_f = f[sample_idx]
        p_h = h[sample_idx]
        vec_N = N[sample_idx]
        vec_T = T[sample_idx]
        
        # Draw normals
        ax.plot([p_g[0], p_f[0]], [p_g[1], p_f[1]], color=colors[idx], linestyle='-', linewidth=1.5, marker='o')
        ax.plot([p_g[0], p_h[0]], [p_g[1], p_h[1]], color=colors[idx], linestyle='-', linewidth=1.5, marker='o')
        
        # Labels
        ax.text((p_g[0]+p_f[0])/2 - 0.05, (p_g[1]+p_f[1])/2 + 0.01, labels_L[idx], color=colors[idx], fontsize=12, fontweight='bold')
        ax.text((p_g[0]+p_h[0])/2 + 0.02, (p_g[1]+p_h[1])/2 - 0.01, labels_R[idx], color=colors[idx], fontsize=12, fontweight='bold')
        
        # Perpendicular marker
        eps = 0.015
        sq_l = np.array([
            p_g + eps * vec_T,
            p_g + eps * vec_T - eps * vec_N,
            p_g - eps * vec_N
        ])
        ax.plot(sq_l[:, 0], sq_l[:, 1], color='gray', linewidth=1)
        
        sq_r = np.array([
            p_g + eps * vec_T,
            p_g + eps * vec_T + eps * vec_N,
            p_g + eps * vec_N
        ])
        ax.plot(sq_r[:, 0], sq_r[:, 1], color='gray', linewidth=1)
        
    ax.set_aspect('equal')
    ax.set_xlabel("X", fontsize=12)
    ax.set_ylabel("Y", fontsize=12)
    ax.set_title("Symmetric Ribbon around Curved Axis (Cusp Development)", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.5)
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/symmetric_cusp.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
