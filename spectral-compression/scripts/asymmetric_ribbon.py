#!/usr/bin/env python3
"""
Asymmetric 2D Ribbon / Planar Generalized Cylinder Visualization
================================================================

Visualizes a 2D ribbon defined by:
  - An axis curve g(s)
  - Left boundary f(s) = g(s) - r_L(s) * N(s)
  - Right boundary h(s) = g(s) + r_R(s) * N(s)
where N(s) is the unit normal to the axis curve g(s).
Draws normal vectors and perpendicular symbols to match the user's sketch.

Saves the diagnostic plot to figures/asymmetric_ribbon.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

def axis_curve(s):
    """A smooth, curved axis g(s)."""
    x = s
    y = 0.3 * np.sin(np.pi * s)
    return np.column_stack((x, y))

def compute_tangents_normals(g):
    """Computes unit tangents and normals along a discrete 2D curve."""
    # Central differences for interior, forward/backward for ends
    dg = np.zeros_like(g)
    dg[1:-1] = (g[2:] - g[:-2]) / 2.0
    dg[0] = g[1] - g[0]
    dg[-1] = g[-1] - g[-2]
    
    speeds = np.linalg.norm(dg, axis=1, keepdims=True)
    T = dg / speeds
    # Normal is (-T_y, T_x)
    N = np.column_stack((-T[:, 1], T[:, 0]))
    return T, N

if __name__ == "__main__":
    n_pts = 200
    s_vals = np.linspace(0.0, 1.0, n_pts)
    
    # 1. Compute axis curve g(s)
    g = axis_curve(s_vals)
    T, N = compute_tangents_normals(g)
    
    # 2. Define asymmetric radius functions
    # Left radius (corresponds to c_t, c_i, c_s in the sketch)
    r_L = 0.15 + 0.05 * np.cos(2 * np.pi * s_vals) + 0.03 * np.sin(4 * np.pi * s_vals)
    # Right radius (corresponds to b, a in the sketch)
    r_R = 0.12 - 0.04 * s_vals + 0.02 * np.sin(3 * np.pi * s_vals)
    
    # 3. Compute boundary curves f(s) and h(s)
    f = g - N * r_L[:, np.newaxis] # Left boundary
    h = g + N * r_R[:, np.newaxis] # Right boundary
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    
    # Draw curves
    ax.plot(g[:, 0], g[:, 1], 'k--', linewidth=2, label="Axis Curve g(s)")
    ax.plot(f[:, 0], f[:, 1], '#2196f3', linewidth=2.5, label="Left Boundary f(s) = g(s) - r_L(s) N(s)")
    ax.plot(h[:, 0], h[:, 1], '#ff9800', linewidth=2.5, label="Right Boundary h(s) = g(s) + r_R(s) N(s)")
    
    # Draw normal segments and perpendicular markers at specific points
    sample_indices = [35, 100, 165]
    colors = ['#e91e63', '#9c27b0', '#009688']
    
    for idx, sample_idx in enumerate(sample_indices):
        p_g = g[sample_idx]
        p_f = f[sample_idx]
        p_h = h[sample_idx]
        vec_N = N[sample_idx]
        vec_T = T[sample_idx]
        
        # Draw normals to left and right
        ax.plot([p_g[0], p_f[0]], [p_g[1], p_f[1]], color=colors[idx], linestyle='-', linewidth=1.5, marker='o')
        ax.plot([p_g[0], p_h[0]], [p_g[1], p_h[1]], color=colors[idx], linestyle='-', linewidth=1.5, marker='o')
        
        # Add labels
        if idx == 0:
            ax.text((p_g[0]+p_f[0])/2 - 0.05, (p_g[1]+p_f[1])/2 + 0.02, r"$c_t$", color=colors[idx], fontsize=12, fontweight='bold')
            ax.text((p_g[0]+p_h[0])/2 + 0.02, (p_g[1]+p_h[1])/2 - 0.02, r"$b$", color=colors[idx], fontsize=12, fontweight='bold')
        elif idx == 1:
            ax.text((p_g[0]+p_f[0])/2 - 0.05, (p_g[1]+p_f[1])/2 + 0.02, r"$c_i$", color=colors[idx], fontsize=12, fontweight='bold')
        elif idx == 2:
            ax.text((p_g[0]+p_f[0])/2 - 0.05, (p_g[1]+p_f[1])/2 - 0.03, r"$c_s$", color=colors[idx], fontsize=12, fontweight='bold')
            ax.text((p_g[0]+p_h[0])/2 + 0.02, (p_g[1]+p_h[1])/2 - 0.02, r"$a$", color=colors[idx], fontsize=12, fontweight='bold')
            
        # Draw perpendicular symbols at p_g
        # A small square aligned with T and N
        eps = 0.015
        # For left normal (-N)
        sq_l = np.array([
            p_g + eps * vec_T,
            p_g + eps * vec_T - eps * vec_N,
            p_g - eps * vec_N
        ])
        ax.plot(sq_l[:, 0], sq_l[:, 1], color='gray', linewidth=1)
        
        # For right normal (+N)
        sq_r = np.array([
            p_g + eps * vec_T,
            p_g + eps * vec_T + eps * vec_N,
            p_g + eps * vec_N
        ])
        ax.plot(sq_r[:, 0], sq_r[:, 1], color='gray', linewidth=1)
        
    ax.set_aspect('equal')
    ax.set_xlabel("X", fontsize=12)
    ax.set_ylabel("Y", fontsize=12)
    ax.set_title("Planar Asymmetric Ribbon (2D Planar Generalized Cylinder)", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.5)
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/asymmetric_ribbon.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
