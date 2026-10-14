# Publication Roadmap & Technical Action Items

This roadmap outlines the planned theoretical extensions, algorithmic implementations, and empirical benchmarks required to elevate `PaddyMathPapers` (particularly the 3D geometry framework) toward peer-reviewed publication standards (*ACM Transactions on Graphics*, *IEEE Transactions on Signal Processing*, or *Computer-Aided Geometric Design*).

---

## 1. Differential Geometry & Mathematical Extensions

### 1.1. Bishop Parallel Transport Moving Frame ($\kappa = 0$ Inflection Points)
* **Current Limitation:** The Frenet–Serret frame $\{\mathbf{T}, \mathbf{N}, \mathbf{B}\}$ relies on the principal normal $\mathbf{N} = \mathbf{T}'/\|\mathbf{T}'\|$, which is undefined when curvature vanishes ($\kappa(s) = 0$, e.g., straight segments or inflection points). This can cause coordinate discontinuities.
* **Planned Implementation:** Implement **Bishop's Parallel Transport Frame** (also known as the Relatively Parallel Adapted Frame). The Bishop frame defines two normal vectors $\{\mathbf{M}_1, \mathbf{M}_2\}$ that do not twist around the tangent vector and remain smooth and continuous even when curvature vanishes. Update the quaternionic differential integration routines to support parallel transport frames.

### 1.2. Sobolev Error Bounds for the Spiral Limit
* **Current Achievement:** Proved that the spiral path $\mathbf{c}_n(t)$ is dense in the surface $\mathcal{M}$ as winding number $n \to \infty$.
* **Planned Theory:** Derive explicit rate-distortion bounds. Assuming the radius function $r(s, \theta)$ resides in a Sobolev space $H^k(\mathcal{M})$ (representing surfaces with square-integrable derivatives up to order $k$), prove how the $L^2$ surface reconstruction error scales jointly as a function of winding density $n$ and retained Fourier modes $K$.

### 1.3. Optimal Axis Selection (The Gauge Problem)
* **Current Status:** Axis curves are selected via standard geometric heuristics or evolutes.
* **Planned Theory:** Because the axis curve $\gamma(s)$ is not unique for a given 3D object, different axis choices produce different radius waveforms $r(s, \theta)$ with differing spectral decay rates. Formulate an optimization problem to find the "canonical axis" that minimizes the high-frequency spectral energy of the unwrapped radius signal.

---

## 2. Practical Compression & Benchmarking Pipeline

### 2.1. Rate-Distortion Analysis & Coefficient Quantization
* **Current Achievement:** Demonstrated that discarding 97% of Fourier modes produces near-lossless visual reconstruction of continuous surfaces.
* **Planned Implementation:** Implement a production-grade quantization and entropy-coding stage:
  1. Quantize retained Fourier coefficients into 8-bit, 12-bit, and 16-bit integers.
  2. Apply Huffman or arithmetic compression to the quantized bitstream.
  3. Measure true compressed file sizes (in bytes) and generate standard Rate-Distortion curves (PSNR and Hausdorff distance vs. bits-per-vertex).

### 2.2. Benchmarking Against Industry Standards
* **Objective:** Benchmark the spiral transform compression pipeline against established industry mesh encoders:
  - **Google Draco** (industry-standard open-source 3D mesh compressor).
  - **Geometry Images** (planar parameterization with wavelet compression).
  - **MPEG-3DMC** (standardized 3D mesh coding).
* **Deliverable:** Comparative rate-distortion plots across organic shapes (human head, biological organs) and CAD mechanical shapes (using $L_p$ metric optimization).

### 2.3. Automated Mesh Skeletonization (Centerline Extraction)
* **Current Status:** Axis curves are specified or extracted via slice-based evolutes.
* **Planned Pipeline:** Build an automated end-to-end preprocessing pipeline:
  1. Ingest raw triangle meshes (OBJ/STL).
  2. Extract the medial centerline curve using mean curvature flow or radial basis skeletonization.
  3. Parameterize the Bishop moving frame along the extracted centerline.
  4. Perform dynamic $L_p$ ray-casting to sample $r(t)$.
  5. Compute the 1D FFT and output the compressed bitstream.
