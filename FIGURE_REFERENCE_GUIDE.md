# Figure Reference Guide (Compressed)

## Essential Figures for 3-Page Report

### Section 3: Algorithm

**No figures needed** — text description is sufficient for algorithm section.

---

### Section 4: Results

| Figure | Type | Section | File | Caption |
|--------|------|---------|------|---------|
| 4.1 | Line plot | 4.1 | 81_k5_gamma0/07_fitness_convergence.png | Fitness improvement over 6000 generations. Best fitness (blue) rapidly improves through gen ~500, then plateaus. Mean fitness (orange) shows population-wide improvement. Demonstrates successful algorithm convergence. |
| 4.2 | Map | 4.1 | 81_k5_gamma0/01_world_map_clusters.png | Geographic distribution of 5 clusters. Subjects colored by cluster assignment; solid-color regions indicate geographically coherent clusters. White coastlines for reference. |
| 4.3 | Scatter | 4.1 | 81_k5_gamma0/02_mds_clusters.png | Genetic space structure (MDS embedding of distance matrix). Clusters form visually distinct clouds, validating genetic differentiation. |
| 4.4 | Box plot | 4.1 | 81_k5_gamma0/05_within_vs_between_genetic.png | Within-cluster (left) vs. between-cluster (right) genetic distances per cluster. Clear separation confirms genetic homogeneity. |
| 4.5 | Heatmap | 4.1 | 81_k5_gamma0/03_genetic_heatmap_by_cluster.png | Genetic distance heatmap with subjects ordered by cluster. Block-diagonal structure indicates within-cluster homogeneity; off-diagonal blocks show between-cluster distances. |
| 4.6a | Map+color | 4.1 | 81_k5_gamma0/02b_medoid_distances_mds.png | Medoid distance in MDS space. Full color = close to cluster center; white = far from medoid (frontier). Identifies genetically peripheral subjects. |
| 4.6b | Map+color | 4.1 | 81_k5_gamma0/02c_medoid_distances_geographic.png | Geographic projection of medoid distances. White zones indicate frontier subjects, concentrated in known admixture areas (Central Asia, Oceania, Americas). |
| 4.7 | Table | 4.2 | (in text) | Parameter sweep table (K=2–6, γ=0,1). Shows best fitness for each configuration. Demonstrates K=5 optimality. |
| 4.8 | Heatmap | 4.3 | consistency/01_subject_stability_heatmap.png | Subject stability across 20 runs. Each row = subject; columns = runs. Solid colors = stable subjects; multiple colors = variable subjects. Visual confirmation of bimodal stability distribution. |
| 4.9 | Heatmap | 4.3 | consistency/02_ari_consistency_matrix.png | Adjusted Rand Index between all run pairs. Uniform high values (0.80–0.87) with one outlier at 0.69 confirm robust convergence. |
| 4.10 | Histogram | 4.3 | consistency/03_stability_distribution.png | Distribution of consistency scores (0–1). Bimodal: high peak at 0.95–1.0 (stable subjects); secondary plateau at 0.6–0.8 (variable); tail <0.5 (frontier). Validates natural core/boundary separation. |
| 4.11 | Map+color | 4.3 | consistency/04_stability_map.png | Geographic distribution of stability. Green (stable ≥0.9) clusters in population cores (Africa, East Asia); red/yellow (variable/frontier <0.9) in admixture zones. Biological validation: frontier subjects match known admixed populations. |

---

## Integration Instructions

### Placement in Report

1. **After Section 4.1 (Primary Results)**: Place Figures 4.1–4.7 in sequence
   - 4.1 validates convergence
   - 4.2–4.5 show cluster structure and genetic differentiation
   - 4.6a–b highlight frontier individuals

2. **After Section 4.2 (Parameter Sweep)**: Place parameter sweep table in text (no figure)

3. **After Section 4.3 (Consistency)**: Place Figures 4.8–4.11 in sequence
   - 4.8 shows per-subject stability visually
   - 4.9 quantifies run-to-run agreement
   - 4.10 shows stability distribution
   - 4.11 validates biological plausibility

---

## Figure File Locations

All figures are in the project repository:

```
results/runs/81_k5_gamma0/
  ├── 07_fitness_convergence.png       (Figure 4.1)
  ├── 01_world_map_clusters.png        (Figure 4.2)
  ├── 02_mds_clusters.png              (Figure 4.3)
  ├── 05_within_vs_between_genetic.png (Figure 4.4)
  ├── 03_genetic_heatmap_by_cluster.png (Figure 4.5)
  ├── 02b_medoid_distances_mds.png     (Figure 4.6a)
  └── 02c_medoid_distances_geographic.png (Figure 4.6b)

results/consistency/
  ├── 01_subject_stability_heatmap.png (Figure 4.8)
  ├── 02_ari_consistency_matrix.png    (Figure 4.9)
  ├── 03_stability_distribution.png    (Figure 4.10)
  └── 04_stability_map.png             (Figure 4.11)
```

---

## Captions (Ready to Copy)

**Figure 4.1**: Fitness convergence over 6000 generations for K=5 genetic-only clustering. Best fitness (blue line) rapidly improves through generation ~500, then plateaus by generation 3000. Mean fitness (orange) tracks best fitness with higher variance, indicating population heterogeneity. Worst fitness (red) shows the quality floor of each generation.

**Figure 4.2**: World map showing cluster assignments for K=5 (colors indicate clusters). Geographic coherence validates the r=0.503 genetic-geographic correlation despite genetic-only optimization (γ=0). Solid-color regions indicate geographically localized clusters.

**Figure 4.3**: Multidimensional scaling (MDS) projection of genetic distances into 2D space. Clusters form visually distinct clouds, confirming genetic differentiation. Isolated points represent genetic outliers.

**Figure 4.4**: Box plots of genetic distances within clusters (left) vs. between clusters (right) for each of 5 clusters. Within-cluster distributions are consistently lower and tighter, demonstrating genetic homogeneity. Between-cluster distributions are higher and broader, confirming separation. Outliers identify frontier subjects.

**Figure 4.5**: Heatmap of genetic distances between all subject pairs, reordered by cluster. Block-diagonal structure (colored blocks along diagonal) indicates within-cluster homogeneity. Off-diagonal blocks show between-cluster distances. Deviations highlight boundary subjects.

**Figure 4.6a**: MDS projection colored by relative distance to cluster medoid. Full cluster color indicates subjects close to genetic center; white indicates far from medoid (frontier candidates). Combines genetic space structure with within-cluster peripherality.

**Figure 4.6b**: Geographic projection of medoid distances. Full color = cluster core; white = frontier individuals. Frontier subjects concentrate in known admixture zones (Central Asia, Oceania, Americas), validating biological plausibility.

**Figure 4.8**: Heatmap of cluster assignments for each of 278 subjects (rows) across 20 independent runs (columns). Solid-color rows = stable subjects (assigned to same cluster in all/most runs). Multi-color rows = variable subjects. Very few multi-color rows confirm high stability (mean consistency 0.918).

**Figure 4.9**: Adjusted Rand Index (ARI) pairwise agreement matrix for all 20 runs. Colors represent ARI values (1.0 = identical, 0 = independent). Uniform high values (0.80–0.87) across most of matrix confirm strong run-to-run agreement. One outlier at 0.69 suggests different local optimum but still high agreement.

**Figure 4.10**: Histogram of consistency scores (0–1) for all 278 subjects. Bimodal distribution: primary peak at 0.95–1.0 (~158 stable subjects); secondary plateau at 0.6–0.8 (~120 variable subjects); tail <0.5 (~3 frontier subjects). Bimodality validates natural separation between core and boundary populations.

**Figure 4.11**: World map with subjects colored by stability category. Green (stable ≥0.9) subjects cluster in population cores (sub-Saharan Africa, East Asia, Northern Europe). Red/yellow (variable/frontier <0.9) subjects concentrate in admixture zones (Central Asia, Oceania, Americas). Geographic coherence validates biological interpretability.

---

## Summary Table

**11 figures total** for 3-page report:
- 1 convergence plot (4.1)
- 3 genetic space visualizations (4.2, 4.3, 4.5)
- 1 genetic differentiation (4.4)
- 2 medoid distance visualizations (4.6a–b)
- 4 consistency analysis (4.8–4.11)

All figures are publication-ready. Captions provided above can be copied directly or lightly edited to match your paper's style.
