# Development & Internal Documentation

This folder contains development-only materials and is excluded from the published repository.

## Contents

### `legacy_scripts/`
Old data processing scripts used during the data pipeline phase:
- `parse_data.py` — Parse BCF files to genotypes
- `compute_distances.py` — Compute distance matrices
- `visualize_data.py` — Generate diagnostic plots
- `download_sgdp.py` — SGDP data acquisition

**Status:** Archived (outputs are in `results/` and `data/processed/`)

### `claude_context/`
Context files and guidelines used during AI-assisted development:
- `claude.md` — Development instructions
- `DATA_SUMMARY.md` — Data overview
- `GUIDELINES.md` — Project guidelines
- `README_SGDP_Download.md` — SGDP download guide

**Status:** Reference only (not part of published repo)

### `handovers/`
Handover documentation and early implementations:
- `evo_algorithm_handover/` — Initial EA code iteration

**Status:** Superseded by main `evo_algorithm/` implementation

---

## Notes for Developers

- Keep this folder excluded from `git add .` (covered by `.gitignore`)
- Reference documentation here for context, but main docs are in `/docs`
- Do not commit binary files or data files to this folder
- Clean up old files periodically
