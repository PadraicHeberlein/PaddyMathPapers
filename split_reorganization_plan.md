# Reorganization Plan: Paper Split and Unification

This plan reorganizes the repository's papers into two distinct, mathematically cohesive manuscripts:
1. **Paper A (The Sequence Paper):** Merges Paper 1 (Modular Spectral Entropy) with Parts I & II of Paper 2 (Block Entropy & Continuous Encoding Limits).
2. **Paper B (The Geometry Paper):** Establishes Part III of Paper 2 (Quaternionic Frames & Spiral Transforms) as a standalone geometry and graphics paper.

---

## The Rational Reorganization

### Why This Split Makes Sense
* **Theme Separation:** The original Paper 2 was divided between discrete string analysis (Parts I & II) and 3D differential geometry (Part III). Splitting them groups your work by target audience:
  - **Paper A** becomes a unified manuscript on **discrete sequences, entropy, and representation limits**, appealing to information theorists, number theorists, and computer scientists.
  - **Paper B** becomes a pure **applied geometry and graphics** manuscript, appealing to researchers in geometric modeling, CAD, and computer graphics.
* **Size and Depth:** Merging Parts I & II of Paper 2 into Paper 1 elevates it from a short note on modular tables into a substantial, multi-faceted research paper on the boundaries between discrete sequence periodicities and continuous spectral analysis.

---

## Outline of the New Papers

### Paper A: "On the Spectral Entropy, Periodicity, and Representation Limits of Discrete Sequences"
* **Location:** `/home/padraic/Projects/PaddyMathPapers/spectral-entropy/main.tex`
* **Structure:**
  - **Section 1: Introduction** (Unifying theme: finding periodic structure in discrete sequences and the limits of continuous embeddings).
  - **Part I: Modular Spectral Entropy and Rings** (Original Paper 1 sections)
    - Section 2: Spectral Entropy of Modular Multiplication
    - Section 3: Ring Structure and Wave Mechanics (Schrödinger unit circle model, prime vs. composite participation ratios)
    - Section 4: The Stieltjes Transform & Laurent Primality Criterion
    - Section 5: Continuous Entropy Landscape $S(x)$
  - **Part II: Sequential Periodicity & Block Entropy** (Original Paper 2, Part I)
    - Section 6: First-Order Shannon Entropy and Block Entropy
    - Section 7: Optimal Block Size and Phase Detection via FFT
  - **Part III: Limits of Continuous Curve Representations** (Original Paper 2, Part II)
    - Section 8: Naive Curve Embedding (sinusoidal trajectories)
    - Section 9: The Information Conservation Law and Degrees of Freedom
    - Section 10: Sinusoidal Inflation Penalty & Runge's Phenomenon
  - **Section 11: Conclusion**
  - **Bibliography** (Merged references for Information Theory and Number Theory)

---

### Paper B: "Spectral Compression of 3D Surfaces via Quaternionic Moving Frames and Spiral Transforms"
* **Location:** `/home/padraic/Projects/PaddyMathPapers/spectral-compression/main.tex`
* **Structure:**
  - **Section 1: Introduction** (Theme: coordinate-invariant 3D surface compression via moving frame dimensional reduction).
  - **Section 2: Classical Surfaces of Revolution**
  - **Section 3: The Curved Axis and Moving Frenet Frame**
  - **Section 4: The Planar 2D Ribbon and Cusp Development** (Your hand-sketch analysis)
  - **Section 5: Generalized Surfaces of Revolution** (3D formulation)
  - **Section 6: Quaternionic Frame Parameterization & SU(2) Integration** (RK4 quaternionic integration)
  - **Section 7: The Inverse Problem: Unwrapping to a Cylinder** (Evolute-straightening)
  - **Section 8: The Spiral Limit and Dimensional Reduction** (Space-filling limit proof)
  - **Section 9: Compression via the Spiral Transform** (FFT radius compression and energy decay)
  - **Section 10: Conclusion**
  - **Bibliography** (Geometry, Quaternions, and Graphics references)

---

## Action Plan

### Phase 1: Reframe and Clean Up `spectral-compression` (Paper B)
1. **Strip Out Parts I & II:** Remove the sections on first-order Shannon entropy, block entropy, FFT period detection, and sinusoidal curve encoding from [spectral-compression/main.tex](file:///home/padraic/Projects/PaddyMathPapers/spectral-compression/main.tex).
2. **Reframe Intro & Conclusion:** Rewrite the introduction and conclusion to focus solely on the 3D geometry and compression problem.
3. **Re-number Sections and Equations:** Clean up the LaTeX outline.

### Phase 2: Migrate Scripts and Figures
1. **Move Code:** Move the block-entropy and FFT periodicity scripts from `spectral-compression/scripts/` to `spectral-entropy/scripts/`:
   - `block_entropy.py`
   - `fft_period.py`
   - `piecewise_linear_binary.py`
2. **Move Figures:** Move the corresponding figures to `spectral-entropy/figures/`:
   - `block_entropy_sweep.png`
   - `fft_period_detection.png`
   - `piecewise_linear_encoding.png`

### Phase 3: Update and Merge `spectral-entropy` (Paper A)
1. **Append Text:** Insert the text of Parts I & II of Paper 2 into [spectral-entropy/main.tex](file:///home/padraic/Projects/PaddyMathPapers/spectral-entropy/main.tex) as Parts II & III of the unified paper.
2. **Integrate Figures:** Insert `block_entropy_sweep.png`, `fft_period_detection.png`, and `piecewise_linear_encoding.png` into the appropriate migrated sections.
3. **Merge Bibliography:** Append Cover \& Thomas to the existing number-theoretic bibliography of Paper 1.
4. **Rewrite Intro/Conclusion:** Refocus the unified introduction on the boundaries of discrete sequence analysis and representation limits.

### Phase 4: Compile and Validate
1. Run `pdflatex` on both documents to confirm they compile cleanly with no undefined references or broken floats.
2. Verify that all 2D sequence-related scripts run correctly from `spectral-entropy/scripts/`.
