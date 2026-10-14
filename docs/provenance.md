# AI Provenance, Governance & Lineage Ledger

This document maintains an audit ledger of AI-assisted contributions, active model identifiers, prompt specifications, and provenance protocols for `PaddyMathPapers`.

---

## Provenance Policy & Transparency Note

> [!NOTE]
> **Evolution of Provenance Tracking in this Repository:**
> Systematic prompt and provenance tracking via `.ai-lineage/` was introduced after the repository was underway, coinciding with the author's adoption of structured AI agent workflows. During the earliest exploratory phases of this project, informal prompts and exploratory chat sessions were not systematically archived. As the project grew in mathematical rigor and architectural complexity, formal logging, commit attribution, and prompt provenance were established as standard practices. All subsequent work adheres to the lineage protocols outlined below.

---

## AI Collaboration Framework

In this repository, artificial intelligence models (Gemini, Claude, GPT) serve as **interactive mathematical collaborators** under direct human leadership:
- **Principal Investigator (Human Author):** Conceptualizes the research direction, formulates original geometric and information-theoretic hypotheses, constructs physical analogies, designs simulation experiments, and reviews every equation for mathematical validity.
- **AI Collaborator:** Assists with symbolic algebra expansion, formal LaTeX proof drafting, literature cross-referencing, script vectorization, and critical red-teaming (e.g., challenging early informal claims).

---

## Provenance Audit Log

Prompts and execution traces are recorded in [`.ai-lineage/prompts.json`](../.ai-lineage/prompts.json).

### Summary of Major Logged Interactions

| Date | Conversation / Session ID | Model | Scope of Work | Verified Artifacts |
| :--- | :--- | :--- | :--- | :--- |
| **2026-09-24** | `system-init` | Gemini 3.6 Flash | Initialized repository AI lineage audit ledger and prompt log. | `PROVENANCE.md`, `.ai-lineage/prompts.json` |
| **2026-10-14** | `452521c0-...` | Gemini 3.8 Flash | Restructured repository into curated `docs/` Research Notebook, built `pdf/` distribution, and created root showcase `README.md`. | `docs/`, `pdf/`, `README.md` |

---

## Commit Attribution Standards

In accordance with Linux Kernel AI coding guidelines and emerging academic transparency standards, commits involving AI assistance include trailers indicating the model utilized:
```git
chore(governance): initialize AI provenance, lineage, and change log

AI-Model: Gemini 3.6 Flash (Antigravity)
AI-Prompt-URI: conversation://system-init
```
