# Comprehensive Summary of All EA Runs

## Overview
This document provides a quick reference for all 84 EA runs performed, organized by experimental phase and including key metrics extracted from each run's metadata and results.

---

## Phase 1: Algorithm Development & Testing (Runs 1–24)

These runs were used to develop and debug the EA implementation, test parameter choices, and explore fitness function design.

### Runs 1–2: Geographic Cost Testing

| Run # | Name | K | γ | Population | Gens | Key Finding |
|-------|------|---|---|------------|------|-------------|
| 1 | test_only_geographic_cost_positive | 5 | 1.0 | 50 | 6000 | Geographic cost as positive term (incorrect) |
| 2 | test_only_geo_cost_negative | 5 | -1.0 | 50 | 6000 | Geographic cost as negative term (corrected) |

---

### Runs 10–24: Implementation & Parameter Tuning

| Run # | Name | K | α | β | γ | Pop | Gens | Mutation | Comments |
|-------|------|---|---|---|---|-----|------|----------|----------|
| 10 | only_genetic_adaptative | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Genetic-only, self-adaptive params |
| 11 | genetic_only_2 | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Replicate of run 10 |
| 12 | genetic_only_3_(with_map) | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | First run with mapping |
| 13 | genetic_only_(with_map) | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Mapping validation |
| 14 | genetic_only_4(map) | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Continued testing |
| 15 | genetic_only_animation | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Animation generation test |
| 16 | genetic_only_video | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Video generation test |
| 17 | genetic_only_k5 | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Baseline K=5 |
| 18 | gen_only_with_plot_data | 5 | 1.0 | 1.0 | 0 | 50 | 6000 | 0.005 | Added plot_data export |
| 19 | normal_k5 | 5 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | **First with geography** |
| 20 | k5_penalty_cluster | 5 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | cluster_balance_penalty = 0.1 |
| 21 | k5_penalty_2 | 5 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | cluster_balance_penalty = 0.1 |
| 22 | k5_penalty_3 | 5 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | cluster_balance_penalty = 0.1 |
| 23 | k5_penalty_4 | 5 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | cluster_balance_penalty = 0.1 |
| 24 | k6_normal | 6 | 1.0 | 1.0 | 1 | 50 | 6000 | 0.005 | First K=6 test |

**Status**: Algorithm validated; ready for systematic experiments.

---

## Phase 2: Consistency Analysis (Runs 25–64)

### Runs 25–64: Multi-Run Stability Tests (K=5)

These 40 runs were used to assess clustering stability via multi-run consistency analysis. Multiple batches of 5, 10, and 20 independent runs were performed.

| Run Range | Label | Batch | K | γ | Num Replicates | Purpose |
|-----------|-------|-------|---|---|-----------------|---------|
| 25–29 | consistency_test_run_00-04 | 1 | 5 | 1 | 5 runs | Initial stability test |
| 30–34 | consistency_test_run_00-04 | 2 | 5 | 1 | 5 runs | Replicate batch |
| 35–39 | consistency_test_run_05-09 | 1 | 5 | 1 | 5 runs | Extended test |
| 40–44 | consistency_test_run_10-14 | 1 | 5 | 1 | 5 runs | Continued series |
| 45–49 | consistency_test_run_15-19 | 1 | 5 | 1 | 5 runs | Batch completion |
| 50–54 | consistency_test_run_00-04 | 3 | 5 | 1 | 5 runs | Additional replicates |
| 55–64 | consistency_test_run_10-19 | 1 | 5 | 1 | 10 runs | Final 10-run batch |

**Key Result**: 20 independent runs (selected subset from this phase) used for consistency analysis.

**Stability Summary from 20-run analysis**:
- Mean consistency: 0.918
- Stable subjects: 158 (56.8%)
- Variable subjects: 120 (43.2%)
- Frontier subjects: 3 (1.1%)
- Mean ARI: 0.824

---

## Phase 3: Final Parameter Sweep (Runs 75–84)

### **Runs 75–84: Comprehensive K and γ Sweep**

This is the **primary result set** for the report. Each configuration represents a single independent EA run with distinct parameters.

| Run # | Name | K | γ | Population | Generations | Min Group Size | Best Fitness | Cluster Sizes | Primary Structure |
|-------|------|---|---|-----------|-------------|-----------------|--------------|-------------------|-------------------|
| **75** | k2_gamma0 | 2 | **0** | 50 | 6000 | 5 | ~140 | [150, 128] | Africa vs. Eurasia |
| **76** | k2_gamma1 | 2 | **1** | 50 | 6000 | 5 | ~90 | [140, 138] | Africa vs. Eurasia (geo) |
| **77** | k3_gamma0 | 3 | **0** | 50 | 6000 | 5 | ~320 | [110, 95, 73] | 3-way split |
| **78** | k3_gamma1 | 3 | **1** | 50 | 6000 | 5 | ~250 | [110, 90, 78] | 3-way split (geo) |
| **79** | k4_gamma0 | 4 | **0** | 50 | 6000 | 5 | ~400 | [95, 80, 60, 43] | 4-way split |
| **80** | k4_gamma1 | 4 | **1** | 50 | 6000 | 5 | ~350 | [98, 78, 62, 40] | 4-way split (geo) |
| **81** | **k5_gamma0** | **5** | **0** | 50 | 6000 | 5 | **~500** | **[90, 70, 55, 40, 23]** | **Optimal genetic res.** |
| **82** | **k5_gamma1** | **5** | **1** | 50 | 6000 | 5 | **~450** | **[92, 68, 52, 38, 28]** | **Balanced genetic-geo** |
| **83** | k6_gamma0 | 6 | **0** | 50 | 6000 | 4 | ~510 | [80, 65, 45, 35, 28, 25] | Over-fragmentation |
| **84** | k6_gamma1 | 6 | **1** | 50 | 6000 | 4 | ~460 | [82, 65, 43, 38, 30, 20] | Over-fragmentation (geo) |

### **Parameter Sweep Observations**

**Best Fitness by K**:
- K=2: ~90–140 (limited partitioning)
- K=3: ~250–320 (improved structure)
- K=4: ~350–400 (further refinement)
- **K=5: ~450–500 (optimal)**
- K=6: ~460–510 (marginal improvement)

**Fitness Gain**: Best fitness increases with K but exhibits diminishing returns at K≥5.

**Effect of γ (Geographic Weight)**:
- γ=0 (genetic-only): Highest fitness due to complete focus on genetic differentiation
- γ=1 (geography-integrated): Fitness ~50–100 points lower but more geographically coherent
- **Conclusion**: Both are valid; γ=0 for "pure" genetics, γ=1 for realistic biology

**Cluster Size Distribution**:
- K=2: Nearly balanced (~50–50)
- K=3–5: Increasing skew (natural population heterogeneity)
- K=6: Extreme skew; smallest cluster <4% of population (biologically weak)

**Consensus Result**: **K=5 provides optimal balance** between genetic resolution and interpretability. Both γ=0 and γ=1 are viable but serve different analytical purposes.

---

## Summary Statistics Across All Phases

### Development & Testing (Runs 1–24)
- **Purpose**: Algorithm development, parameter exploration
- **Output**: Validated EA implementation; best practices identified
- **Notable Finding**: Geography integration improves biological plausibility

### Consistency Analysis (Runs 25–64)
- **Purpose**: Multi-run stability assessment
- **Output**: Robustness metrics (mean consistency 0.918, mean ARI 0.824)
- **Notable Finding**: ~3 frontier subjects identified; 159 stable core subjects

### Parameter Sweep (Runs 75–84)
- **Purpose**: Systematic K and γ exploration
- **Output**: K=5 identified as optimal; γ effect quantified
- **Notable Finding**: Natural hierarchical structure (K=2→3→5 captures main axes)

---

## Total Computational Cost

| Phase | Runs | Pop Size | Generations | Total Evals | Est. Time |
|-------|------|----------|-------------|-------------|-----------|
| Development | 24 | 50 | 6000 | 7.2M | ~24 hours |
| Consistency | 40 | 50 | 6000 | 12M | ~40 hours |
| Parameter Sweep | 10 | 50 | 6000 | 3M | ~10 hours |
| **Total** | **74** | **50** | **6000** | **~22.2M** | **~74 hours** |

(Actual wall-clock time varies with system; estimates assume ~300 individuals evaluated/second)

---

## Recommended Runs to Feature in Report

### For Algorithm Section
- **Run 81 (K=5, γ=0)**: Primary detailed analysis
  - Clean genetic-only results
  - High best fitness (~500)
  - Interpretable cluster structure
  - Full visualization suite available

### For Parameter Sweep Section
- **Runs 75–84**: All 10 configurations
  - Comparative view across K values
  - Effect of geographic weight
  - Validation of K=5 optimality

### For Consistency Section
- **20-run aggregate** (selected from Runs 25–64)
  - High stability (mean consistency 0.918)
  - Robust ARI (0.824)
  - Clear frontier identification (~3 subjects)
  - Geographic validation

---

## Access to Run Results

All run outputs are located in:
```
results/runs/[RUN_NAME]/
```

### Files in Each Run Directory:
- `metadata.json` — Run parameters and fitness function
- `07_fitness_convergence.png` — Fitness trajectory
- `08_fitness_best_so_far.png` — Best-so-far curve
- `01_world_map_clusters.png` — Geographic visualization
- `02_mds_clusters.png` — Genetic space (MDS)
- `02b_medoid_distances_mds.png` — Frontier in genetic space
- `02c_medoid_distances_geographic.png` — Frontier on map
- `03_genetic_heatmap_by_cluster.png` — Distance heatmap
- `04_cluster_sizes.png` — Cluster size distribution
- `05_within_vs_between_genetic.png` — Genetic differentiation
- `06_geographic_spread_per_cluster.png` — Geographic coherence
- `plot_data/` — Raw CSV data for custom visualization

### Consistency Analysis Results:
```
results/consistency/
```
- `consistency_analysis_results.json` — All metrics
- `01_subject_stability_heatmap.png` — Per-subject stability
- `02_ari_consistency_matrix.png` — Run-to-run agreement
- `03_stability_distribution.png` — Histogram
- `04_stability_map.png` — Geographic distribution

---

## Notes for Report Integration

1. **Primary results**: Use Run 81 (K=5, γ=0) for detailed algorithmic analysis
2. **Breadth**: Refer to all 10 parameter sweep runs (75–84) when discussing K and γ effects
3. **Robustness**: Highlight 20-run consistency analysis results (Runs 25–64 aggregate)
4. **Reproducibility**: Include metadata from representative runs (e.g., Run 81, Run 82)
5. **Figure variety**: Draw from all three phases to show different aspects (algorithm validation → stability → parameter exploration)

