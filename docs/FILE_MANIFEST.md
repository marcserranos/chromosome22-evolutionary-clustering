# Complete File Manifest

## Summary
- **Total files:** 35 (+ venv, .git directories)
- **Essential files:** 12 (for EA implementation)
- **Archived files:** 4 (can be deleted if space needed)
- **Documentation:** 6 (reference & understanding)
- **Total data size:** ~1.8 GB (including archives)

---

## Essential Files (Required for EA)

### Data Inputs ✓
```
data/processed/genotypes_filtered.npy          28 MB   ✓ KEEP
  Purpose: Individual genotypes (104.5k SNPs × 278 samples)
  Used by: EA fitness function
  Format: numpy array (uint8, shape=(104573, 278))
  
data/processed/samples_metadata_ordered.csv    53 KB   ✓ KEEP
  Purpose: Sample info (SGDP_ID, Region, Lat/Lon)
  Used by: Geographic cost calculation
  Format: pandas CSV
  
results/distances/genetic_distance.npy         ~1.4 MB ✓ KEEP
  Purpose: Pairwise genetic distances (278×278)
  Used by: Genetic separation in fitness
  Format: numpy array (float64, symmetric)
  
results/distances/geographic_distance.npy      ~1.4 MB ✓ KEEP
  Purpose: Pairwise geographic distances (278×278)
  Used by: Geographic coherence penalty in fitness
  Format: numpy array (float64, symmetric)
```

### Documentation ✓
```
docs/PROJECT_OVERVIEW.md                       10 KB   ✓ KEEP
  Purpose: Quick start & project status
  
docs/PIPELINE_SUMMARY.md                       15 KB   ✓ KEEP
  Purpose: Complete data flow with diagrams
  
docs/METHODS.md                                20 KB   ✓ KEEP
  Purpose: Mathematical procedures & transformations
  
docs/DATA_ANALYSIS_REPORT.md                   12 KB   ✓ KEEP
  Purpose: Statistical findings & quality checks
  
docs/ASSIGNMENT.md                             ~8 KB   ✓ KEEP
  Purpose: Original assignment instructions
  
docs/GUIDELINES.md                             ~4 KB   ✓ KEEP
  Purpose: Project constraints & best practices
```

---

## Production Scripts (Keep)

```
scripts/parse_data.py                          8 KB    ✓ KEEP
  Purpose: Parse BCF file & extract genotypes
  Status: Complete & validated
  
scripts/compute_distances.py                   6 KB    ✓ KEEP
  Purpose: Compute genetic & geographic distances
  Status: Complete & validated
  
scripts/visualize_data.py                      8 KB    ✓ KEEP
  Purpose: Create diagnostic plots
  Status: Complete & validated
```

---

## Archived Files (Can Delete for Space)

```
data/raw/chr.sgdp.pub.22.bcf                   942 MB  → ARCHIVE
  Purpose: Original BCF file
  Status: Source data (can re-download if needed)
  Storage: Could delete if storage is critical
  
data/raw/chr.sgdp.pub.22.bcf.csi               25 KB   → ARCHIVE
  Purpose: BCF index
  Status: Only needed if parsing BCF again
  
data/processed/genotypes_raw.npy                291 MB  → ARCHIVE
  Purpose: Raw unfiltered genotypes
  Status: Intermediate (kept for reproducibility)
  Storage: Could delete after validation
  
data/processed/variants_raw.csv                 33 MB   → ARCHIVE
  Purpose: Raw variant list
  Status: Intermediate (kept for reproducibility)
  Storage: Could delete after validation
```

**Space savings if deleted:** 942 + 291 + 33 = 1,266 MB (~1.2 GB)**

---

## Validation Outputs (Keep for Reference)

```
results/distances/genetic_distance.csv          ~5 MB   ✓ KEEP
  Purpose: Human-readable genetic distances
  Format: CSV (can inspect in spreadsheet)
  Use: Verification & manual inspection
  
results/distances/geographic_distance.csv       ~5 MB   ✓ KEEP
  Purpose: Human-readable geographic distances
  Format: CSV (can inspect in spreadsheet)
  Use: Verification & manual inspection
  
results/visualizations/01_pca.png               192 KB  ✓ KEEP
  Purpose: PCA plot (validation)
  Content: 278 samples colored by region
  
results/visualizations/02_distance_heatmap.png  300 KB  ✓ KEEP
  Purpose: Distance heatmap (validation)
  Content: Hierarchical clustering visualization
  
results/visualizations/03_geographic_scatter.png 195 KB ✓ KEEP
  Purpose: Geographic distribution map (validation)
  Content: Global sample locations
  
results/visualizations/04_distance_distributions.png 74 KB ✓ KEEP
  Purpose: Distance statistics (validation)
  Content: Histograms of genetic & geographic distances
  
results/visualizations/05_genetic_geographic_correlation.png 555 KB ✓ KEEP
  Purpose: Correlation plot (validation)
  Content: Scatter + trend line, r=0.503
```

---

## Supporting Files

```
README.md                                      2 KB    ✓ KEEP
  Purpose: Top-level project description
  
LICENSE                                        ~4 KB   ✓ KEEP
  Purpose: Project license
  
claude_context/                                         ✓ KEEP
  Purpose: Reference materials & instructions
  Contains: Assignment, SGDP download guide, guidelines
  
venv/                                          ~200 MB ✓ KEEP
  Purpose: Python virtual environment
  Contains: numpy, pandas, pysam, matplotlib, scipy, sklearn, seaborn
  
.git/                                          ~15 MB  ✓ KEEP
  Purpose: Version control
```

---

## Scripts (Not Used in Final Pipeline)

```
scripts/parse_data_v2.py                       5 KB    - DELETE
  Purpose: Alternative parsing script (unused)
  Status: Superseded by parse_data.py
  
scripts/fix_parsing.py                         6 KB    - DELETE
  Purpose: Metadata parsing fix (one-time use)
  Status: Used once, not needed again
  
data_gathering/download_data.sh                2 KB    - DELETE
  Purpose: Data download script (one-time use)
  Status: Used once, data already local
```

**Cleanup savings:** 13 KB (negligible)**

---

## Space Analysis

### Current Usage
```
Essential data:           ~60 MB    (genotypes_filtered + distances)
Metadata & documentation: ~50 MB    (metadata + docs + CSVs)
Visualizations:          ~1.3 MB    (5 PNG plots)
Python packages:         ~200 MB    (venv/)
Raw data (archive):      ~1,260 MB  (BCF + raw genotypes/variants)
Git history:             ~15 MB     (.git/)
───────────────────────────────────
TOTAL:                   ~1.6 GB
```

### If Archives Deleted
```
Current - Raw data archives = ~340 MB
```

### Recommendation
- **Keep:** Everything until EA is working
- **Delete after:** BCF file (already downloaded, can re-download)
- **Final size:** ~350-400 MB (very manageable)

---

## File Access Patterns

### For EA Implementation
```
Load at startup:
  ├─ data/processed/genotypes_filtered.npy
  ├─ data/processed/samples_metadata_ordered.csv
  ├─ results/distances/genetic_distance.npy
  └─ results/distances/geographic_distance.npy
  
Compute during fitness evaluation:
  ├─ Intra-cluster variance (from genotypes)
  ├─ Inter-cluster separation (from genetic_distance)
  └─ Geographic cost (from geographic_distance)
```

### For Reproducibility
```
To re-run entire pipeline from raw BCF:
  └─ data/raw/chr.sgdp.pub.22.bcf
     ├─ scripts/parse_data.py
     ├─ scripts/fix_parsing.py
     ├─ scripts/compute_distances.py
     └─ scripts/visualize_data.py
```

---

## Version Control

### What's Tracked (.git)
- All `.py` scripts
- All `.md` documentation
- All `.csv` results (human-readable)
- Small data files (.csv, metadata)
- .gitignore excludes:
  - `venv/` (too large)
  - `*.npy` (binary, version-controlled elsewhere)
  - `*.png` (regenerable)

### Not Tracked
- BCF file (too large, external source)
- Raw numpy arrays (regenerable from BCF)
- Virtual environment (regenerable with pip)

---

## Cleanup Checklist

When deploying for final analysis:

- [ ] Delete `scripts/parse_data_v2.py` (unused variant)
- [ ] Delete `scripts/fix_parsing.py` (one-time fix)
- [ ] Delete `data_gathering/` directory (one-time use)
- [ ] Option: Delete `data/raw/chr.sgdp.pub.22.bcf` (saves 942 MB)
- [ ] Option: Delete `data/processed/genotypes_raw.npy` (saves 291 MB)
- [ ] Option: Delete `data/processed/variants_raw.csv` (saves 33 MB)

**Recommended final size:** ~350 MB (with all archives)

---

## Backup Recommendations

### Essential (Must Keep)
```
data/processed/genotypes_filtered.npy
data/processed/samples_metadata_ordered.csv
results/distances/genetic_distance.npy
results/distances/geographic_distance.npy
docs/ (all markdown files)
scripts/ (all .py files)
```

### Nice to Have (For Reproducibility)
```
data/raw/chr.sgdp.pub.22.bcf     (source data)
data/processed/genotypes_raw.npy  (intermediate)
.git/                             (version history)
```

### Not Critical (Regenerable)
```
results/visualizations/ (can rerun visualize_data.py)
results/distances/*.csv (can regenerate from .npy)
```

---

## Summary Table

| Category | Files | Size | Keep | Archive |
|----------|-------|------|------|---------|
| **Raw Data** | 3 | 967 MB | ✓ | bcf, index |
| **Processed Data** | 6 | 324 MB | ✓ | raw arrays |
| **Results** | 9 | 17 MB | ✓ | - |
| **Documentation** | 6 | 70 KB | ✓ | - |
| **Scripts** | 5 | 33 KB | ✓ | deprecated |
| **Venv** | 1 | 200 MB | ✓ | - |
| **Version Control** | 1 | 15 MB | ✓ | - |
| **TOTAL** | 31 | ~1.5 GB | | 1.2 GB |

---

**Status: All files organized, documented, and ready for EA implementation.**

Next: Begin evolutionary algorithm development.
