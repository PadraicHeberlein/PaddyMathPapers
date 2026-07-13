#!/usr/bin/env python3
import sys
import numpy as np
import matplotlib.pyplot as plt
import trimesh
import os

def load_and_prep_mesh(filename):
    print(f"Loading mesh: {filename}...")
    mesh = trimesh.load(filename)
    
    # Center the mesh
    bounds = mesh.bounds
    center = (bounds[0] + bounds[1]) / 2.0
    mesh.apply_translation(-center)
    
    # Scale mesh so Z goes from -1 to 1
    bounds = mesh.bounds
    z_span = bounds[1][2] - bounds[0][2]
    scale_factor = 2.0 / z_span
    mesh.apply_scale(scale_factor)
    
    # Ensure it's centered on Z=0
    mesh.apply_translation([0, 0, -mesh.bounds[0][2] - 1.0])
    print(f"Mesh prepped. New bounds: Z min {mesh.bounds[0][2]:.2f}, Z max {mesh.bounds[1][2]:.2f}")
    return mesh

def raycast_spiral(mesh, n_windings=200, n_samples=30000):
    print(f"Casting {n_samples} rays for {n_windings} windings...")
    t = np.linspace(0, 1, n_samples)
    
    # Keep z slightly within bounds to avoid grazing the extreme poles
    z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2]
    margin = 0.05
    z_path = np.linspace(z_min + margin, z_max - margin, n_samples)
    
    theta_path = 2 * np.pi * n_windings * t
    
    ray_origins = np.column_stack((np.zeros(n_samples), np.zeros(n_samples), z_path))
    ray_dirs = np.column_stack((np.cos(theta_path), np.sin(theta_path), np.zeros(n_samples)))
    
    # Trimesh ray intersection
    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=ray_origins,
        ray_directions=ray_dirs,
        multiple_hits=True
    )
    
    r_path = np.full(n_samples, np.nan)
    
    if len(index_ray) > 0:
        # Calculate distance from origin for each hit
        hit_origins = ray_origins[index_ray]
        distances = np.linalg.norm(locations - hit_origins, axis=1)
        
        # For each ray, we might have multiple hits. Keep the max distance (outer hull).
        # We can use np.maximum.at, but distances is 1D. Let's do it manually with a loop or grouping.
        # Since this is a test script, a simple loop over unique ray indices is fine.
        unique_rays = np.unique(index_ray)
        for r_idx in unique_rays:
            mask = (index_ray == r_idx)
            max_dist = np.max(distances[mask])
            r_path[r_idx] = max_dist
            
    # Interpolate missing values (NaNs)
    missing = np.isnan(r_path)
    n_missing = np.sum(missing)
    print(f"Ray misses: {n_missing} / {n_samples} ({(n_missing/n_samples)*100:.1f}%)")
    
    if n_missing > 0 and n_missing < n_samples:
        valid = ~missing
        r_path[missing] = np.interp(np.flatnonzero(missing), np.flatnonzero(valid), r_path[valid])
    elif n_missing == n_samples:
        print("ERROR: All rays missed! Mesh might be off-center or axis is wrong.")
        sys.exit(1)
        
    return t, z_path, theta_path, r_path

def spectral_compression(r_path, ratio=0.10):
    print(f"Compressing 1D signal (retention {ratio*100}%)...")
    fft_coeffs = np.fft.rfft(r_path)
    mags = np.abs(fft_coeffs)
    
    n_keep = max(1, int(len(fft_coeffs) * ratio))
    threshold = np.sort(mags)[-n_keep]
    
    mask = mags >= threshold
    coeffs_compressed = fft_coeffs * mask
    r_comp = np.fft.irfft(coeffs_compressed, n=len(r_path))
    
    rmse = np.sqrt(np.mean((r_comp - r_path)**2))
    print(f"RMSE 1D: {rmse:.4f} | Kept {n_keep}/{len(fft_coeffs)} coefficients")
    
    return r_comp

def main():
    filename = "Head-3.stl"
    if not os.path.exists(filename):
        print(f"ERROR: Could not find {filename}")
        sys.exit(1)
        
    mesh = load_and_prep_mesh(filename)
    
    t, z_path, theta_path, r_path = raycast_spiral(mesh, n_windings=150, n_samples=25000)
    
    # Keep 10% of coefficients
    r_comp = spectral_compression(r_path, ratio=0.10)
    
    # Reconstruct 3D points
    print("Reconstructing compressed 3D point cloud...")
    X = r_comp * np.cos(theta_path)
    Y = r_comp * np.sin(theta_path)
    Z = z_path
    
    # Generate faces using Delaunay triangulation on the parameter space
    print("Generating faces for STL export...")
    from scipy.spatial import Delaunay
    theta_mod = theta_path % (2 * np.pi)
    pts_2d = np.column_stack((theta_mod, z_path))
    tri = Delaunay(pts_2d)
    
    recon_mesh = trimesh.Trimesh(vertices=np.column_stack((X, Y, Z)), faces=tri.simplices)
    # Fix normals and export
    recon_mesh.fix_normals()
    export_path = "Head-3-Reconstructed-10percent.stl"
    recon_mesh.export(export_path)
    print(f"Exported reconstructed mesh to {export_path}")
    
    X_orig = r_path * np.cos(theta_path)
    Y_orig = r_path * np.sin(theta_path)
    Z_orig = z_path
    
    errors = np.linalg.norm(
        np.column_stack((X, Y, Z)) - np.column_stack((X_orig, Y_orig, Z_orig)), 
        axis=1
    )
    
    print(f"3D Euclidean Error: Mean = {np.mean(errors):.4f}, Max = {np.max(errors):.4f}")
    
    print("Plotting results...")
    fig = plt.figure(figsize=(18, 6), dpi=150)
    
    # Plot Original Mesh (we'll just plot a downsampled point cloud to avoid crashing matplotlib)
    ax1 = fig.add_subplot(131, projection='3d')
    pts = mesh.vertices
    if len(pts) > 10000:
        pts = pts[np.random.choice(len(pts), 10000, replace=False)]
    ax1.scatter(pts[:,0], pts[:,1], pts[:,2], s=1, c='gray', alpha=0.5)
    ax1.set_title("Original 3D Head Mesh\n(Downsampled for viewing)", fontsize=12)
    ax1.axis('off')
    
    # Plot 1D signal
    ax2 = fig.add_subplot(132)
    segment = slice(5000, 6000)
    ax2.plot(t[segment], r_path[segment], 'k-', alpha=0.5, label='Original $r(t)$', linewidth=2)
    ax2.plot(t[segment], r_comp[segment], 'r--', label='Compressed $r(t)$ (10%)', linewidth=1)
    ax2.set_title("1D Unwrapped Spiral Signal (Segment)", fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot Reconstructed Point Cloud with error
    ax3 = fig.add_subplot(133, projection='3d')
    sc = ax3.scatter(X, Y, Z, c=errors, cmap='inferno', s=1, alpha=0.8)
    plt.colorbar(sc, ax=ax3, label='Error (Euclidean Dist)', shrink=0.5)
    ax3.set_title("Reconstructed Point Cloud\n(10% Spectral Coefficients)", fontsize=12)
    ax3.axis('off')
    
    plt.tight_layout()
    os.makedirs("figures", exist_ok=True)
    outpath = "figures/mesh_compression_test.png"
    plt.savefig(outpath, bbox_inches='tight')
    print(f"Saved figure to {outpath}")

if __name__ == "__main__":
    main()
