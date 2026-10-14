# PaddyMath Open Research Notebook

Welcome to the internal research notebook and design archive for `PaddyMathPapers`. 

This directory contains the background context, critical peer reviews, architectural decision logs, implementation histories, and provenance records that shaped the manuscripts in this repository. Rather than hiding the exploratory journey, this notebook documents the full intellectual process—from raw conjectures and critical audits to formal proofs and future research roadmaps.

---

## 🗂️ Notebook Navigation Index

| Document | Purpose & Core Contents | Key Highlights |
| :--- | :--- | :--- |
| [**`author_context.md`**](author_context.md) | **Author Background & Research Philosophy** | Educational/exploratory mission, mathematical interests, and the evolution of AI-collaborative workflows. |
| [**`reviews_and_critiques.md`**](reviews_and_critiques.md) | **Critical Reviews & Sanity Audits** | Ruthless peer-style audits of early drafts that challenged unearned claims and enforced mathematical rigor. |
| [**`decision_log.md`**](decision_log.md) | **Research Decisions & Breakthroughs** | How 6 key challenges were solved: prime-square decay $\Delta(p^2) \sim 1/2p$, quantum Anderson localization, Laurent divisor sums, 2D cusp singularities, spiral density, and $L_p$ variance optimization. |
| [**`publication_roadmap.md`**](publication_roadmap.md) | **Future Work & Publication Milestones** | Next steps for peer-reviewed venues: Bishop parallel transport frame, Sobolev rate-distortion bounds, Google Draco benchmarks, and automated 3D mesh skeletonization. |
| [**`implementation_history.md`**](implementation_history.md) | **Engineering Blueprints & History** | Phase-by-phase implementation blueprints for Paper A (Spectral Entropy) and Paper B (Spectral Compression). |
| [**`provenance.md`**](provenance.md) | **AI Provenance & Lineage Protocols** | Guidelines for prompt tracking, model attribution, and audit ledgers in [`.ai-lineage/prompts.json`](../.ai-lineage/prompts.json). |

---

## 🔬 Research Lifecycle Overview

```
                      [ Initial Intuition & Sketches ]
                                     │
                                     ▼
                      [ Exploratory AI Sparring ]
                                     │
                                     ▼
                [ Critical Peer Audits & Red-Teaming ]  <─── docs/reviews_and_critiques.md
                                     │
                                     ▼
                [ Mathematical Proofs & Vectorized Sims ] <─── docs/decision_log.md
                                     │
                                     ▼
                [ Formal LaTeX Manuscripts & Figures ]   <─── spectral-compression/ & spectral-entropy/
                                     │
                                     ▼
                [ Future Benchmarking & Peer Publication ] <─── docs/publication_roadmap.md
```
