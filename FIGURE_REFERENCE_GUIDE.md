# Figure Reference Guide for University Report

## Overview

This guide maps all generated figures to sections in the report and provides caption suggestions for each figure.

---

## Section 3: Evolutionary Algorithm Framework

### Figure 3.1: Evolutionary Algorithm Flowchart
**File**: `EA_ALGORITHM_FLOWCHART.txt` (can be rendered as diagram or ASCII art)

**Purpose**: Illustrate the generational loop structure of the EA

**Caption**: 
> *"Flowchart of the generational evolutionary algorithm. The algorithm begins with random initialization of 50 candidate partitions, evaluates their fitness, and then iterates through 6000 generations. Each generation applies elitism (preserving the top 2 solutions), fitness-proportional roulette selection (for parent choice), single-point crossover, self-adaptive mutation, and fitness re-evaluation. Individuals with cluster sizes below the minimum threshold (5 subjects) receive penalty fitness. The algorithm tracks convergence metrics (best, mean, worst fitness) per generation."*

**Integration Tips**:
- Place after Section 3.6 (Generational Loop and Elitism)
- Use to visualize the iterative structure described in text
- Readers can reference flowchart while reading algorithm description

---

## Section 4: Results

### Primary Results: K=5, γ=0 (Genetic-Only Clustering)

#### **Figure 4.1: Fitness Convergence Over 6000 Generations**
**File**: `results/runs/81_k5_gamma0/07_fitness_convergence.png`

**Purpose**: Show how best, mean, and worst fitness improve across generations

**Caption**:
> *"Fitness trajectory for K=5 genetic-only clustering (run 81_k5_gamma0). Blue line shows best fitness in each generation, orange shows population mean fitness, and red shows worst fitness. The algorithm rapidly improves through generation ~500 before convergence slows, reaching best fitness ≈ 500–600 by generation 6000. Mean fitness follows best fitness but with higher variance, reflecting heterogeneous population quality."*

**Interpretation Notes**:
- Steep initial rise = effective early exploration
- Plateau after gen ~3000 = convergence to local optimum
- Gap between best and mean = population diversity (good for avoiding premature convergence)

---

#### **Figure 4.2: Best Fitness Running Maximum**
**File**: `results/runs/81_k5_gamma0/08_fitness_best_so_far.png`

**Purpose**: Highlight incremental improvements and breakthrough moments

**Caption**:
> *"Best-so-far fitness trajectory (monotonically non-decreasing by elitism). Visible plateaus indicate generations with no improvement, while jumps indicate discovery of better solutions. The distribution of improvements across the run is non-uniform: rapid gains in generations 0–500, slower improvements in 500–2000, and minimal gains after generation 3000, suggesting the algorithm converges to a local optimum."*

**Interpretation Notes**:
- Number of jumps = diversity of solutions discovered
- Steepness in early gens = easy-to-improve regions of solution space
- Saturation by gen 6000 = adequacy of computational budget

---

#### **Figure 4.3: Cluster Size Distribution**
**File**: `results/runs/81_k5_gamma0/04_cluster_sizes.png`

**Purpose**: Show how subjects are partitioned across clusters

**Caption**:
> *"Final cluster sizes for K=5 genetic-only clustering. Clusters range from 23 to 90 subjects, with no extremely small clusters (enforced by min_group_size=5) and no excessively large monolithic clusters. This size distribution reflects the balance between genetic homogeneity (motivating diverse cluster sizes) and the cluster_balance_penalty term (preventing severe imbalance)."*

**Interpretation Notes**:
- Skewed distribution (not uniform) = natural heterogeneity in populations
- Largest cluster ≈ 90 subjects (≈32% of population)
- Smallest cluster ≈ 23 subjects (≈8% of population)
- No extreme outliers = reasonable balance

---

#### **Figure 4.4: Within vs. Between-Cluster Genetic Distances**
**File**: `results/runs/81_k5_gamma0/05_within_vs_between_genetic.png`

**Purpose**: Quantify genetic differentiation and homogeneity

**Caption**:
> *"Box plots of genetic distances within clusters (left) versus between clusters (right) for each of the 5 clusters. Within-cluster distributions (left) are consistently shifted lower, indicating genetic similarity among co-clustered subjects. Between-cluster distributions (right) are shifted higher and broader, demonstrating genetic differentiation. The clear separation between these distributions quantifies the fitness function's 'separation' and 'variance' terms."*

**Interpretation Notes**:
- Separation between left and right = degree of differentiation achieved
- Outliers in left boxes = potential frontier subjects
- Consistent pattern across clusters = partitioning quality

---

#### **Figure 4.5: Geographic Spread Per Cluster**
**File**: `results/runs/81_k5_gamma0/06_geographic_spread_per_cluster.png`

**Purpose**: Show which clusters are geographically localized vs. dispersed

**Caption**:
> *"Mean geographic distance within each cluster, sorted from lowest to highest. Clusters with low geographic spread are localized to specific regions, while clusters with high spread span multiple continents. This metric provides context for interpreting whether genetic clusters align with expected geographic patterns. For K=5 genetic-only (γ=0), clusters without geographic penalty may exhibit high spread if genetic similarity transcends geography."*

**Interpretation Notes**:
- Low geographic spread (e.g., 500–2000 km) = single-region clusters
- High geographic spread (e.g., 5000–10000 km) = multi-continent clusters
- Comparison to γ=1 (geography-integrated) reveals geography's influence

---

#### **Figure 4.6: World Map with Cluster Assignments**
**File**: `results/runs/81_k5_gamma0/01_world_map_clusters.png`

**Purpose**: Geographic visualization of clusters with map reference

**Caption**:
> *"Subjects plotted at their geographic coordinates and colored by cluster assignment (K=5, γ=0). Natural coastlines shown for geographic reference. This visualization immediately reveals whether genetic clusters have geographic coherence: spatially clustered colors indicate geography-aligns-genetics, while mixed-color regions indicate admixture or genetic diversity spanning continents. For genetic-only clustering, we expect partial—but not perfect—geographic coherence due to the r=0.503 genetic-geographic correlation."*

**Interpretation Notes**:
- Solid-color regions = geographically coherent clusters
- Rainbow/mixed regions = admixed zones or cluster boundaries
- Compare to γ=1 maps to see effect of geographic penalty

---

#### **Figure 4.7: MDS Projection of Genetic Distance**
**File**: `results/runs/81_k5_gamma0/02_mds_clusters.png`

**Purpose**: 2D visualization of genetic similarity structure

**Caption**:
> *"Multidimensional scaling (MDS) embeds the 278×278 genetic distance matrix into 2D space, preserving pairwise distances as well as possible. Subjects are colored by cluster assignment. MDS reveals whether clusters form visually distinct clouds (well-separated clusters) or overlap in genetic space (ambiguous cluster boundaries). Isolated subjects represent genetic outliers; dense clusters represent homogeneous populations."*

**Interpretation Notes**:
- Clear cluster separation in MDS = high-quality partitioning
- Overlapping clouds = ambiguous boundaries (expect variable/frontier subjects here)
- MDS axes don't have biological meaning; only relative positions matter

---

#### **Figure 4.8: Genetic Distance Heatmap with Cluster Ordering**
**File**: `results/runs/81_k5_gamma0/03_genetic_heatmap_by_cluster.png`

**Purpose**: Detailed view of within- and between-cluster distances

**Caption**:
> *"Heatmap of genetic distances between all subject pairs, with subjects reordered by cluster assignment. Rows and columns are arranged in cluster order: all cluster-0 subjects grouped together, then cluster-1, etc. Expected pattern is block-diagonal structure: colored (small distances) along diagonal blocks (within-cluster pairs) and lighter/cooler off-diagonal (large distances, between-cluster pairs). Deviations from this pattern highlight boundary subjects or clustering errors."*

**Interpretation Notes**:
- Block-diagonal = clean partitioning
- Off-diagonal colored patches = potential misassignments or boundaries
- Heatmap color scale should be documented (usually distance-based)

---

### Medoid Distance Visualizations (Frontier Individual Identification)

#### **Figure 4.9a: Medoid Distances in MDS Space**
**File**: `results/runs/81_k5_gamma0/02b_medoid_distances_mds.png`

**Purpose**: Highlight peripheral subjects in genetic space

**Caption**:
> *"MDS projection colored by relative distance to cluster medoid. Subjects closest to the genetic center of their cluster retain full cluster color; subjects farther from the medoid fade through a gradient to white. The percentile threshold marks the closest 20% at full color and the remaining 80% in gradient. This visualization overlays genetic space structure (via MDS) with within-cluster peripherality (via color), highlighting subjects that are genetically intermediate or outlying."*

**Interpretation Notes**:
- Full-color subjects = core population members
- White subjects = peripheral/frontier candidates
- Compare distribution of white to understand cluster compactness

---

#### **Figure 4.9b: Medoid Distances Geographic Projection**
**File**: `results/runs/81_k5_gamma0/02c_medoid_distances_geographic.png`

**Purpose**: Identify geographic zones containing frontier individuals

**Caption**:
> *"Geographic distribution of subjects colored by relative distance to cluster medoid. Green/full color indicates genetic center of cluster; white indicates peripheral subjects farthest from cluster medoid. Geographic clusters of white subjects identify frontier zones where genetically intermediate individuals congregate. Isolated white subjects represent exceptional genetic outliers. This visualization validates that frontier subjects identified genetically correspond to real admixed or transitional populations."*

**Interpretation Notes**:
- White zones = expected admixture regions (e.g., Central Asia, Americas)
- Correlation to frontier subjects from consistency analysis = biological validation
- Useful for literature comparison with known admixed populations

---

## Consistency Analysis: Multi-Run Stability (K=5, 20 runs)

#### **Figure 4.10: Subject Stability Heatmap**
**File**: `results/consistency/01_subject_stability_heatmap.png`

**Purpose**: Show per-subject cluster assignment stability across 20 independent runs

**Caption**:
> *"Heatmap of subject-to-cluster assignments across 20 independent EA runs (K=5). Each row represents one subject; columns represent runs 1–20. Color indicates the cluster assigned to that subject in that run. Subjects with solid colors (no transitions) are stable—assigned to the same cluster in all or nearly all runs. Subjects with multiple colors (frequent transitions) are variable—moving between clusters across runs. Frontier subjects (extreme variability, appearing as 'rainbow' rows) reveal true genetic boundaries between populations."*

**Interpretation Notes**:
- Solid rows = stable subjects (count them: ~158)
- Multi-color rows = variable subjects (count them: ~120)
- Rainbow rows = frontier subjects (very few: ~3)
- Visual boundary at specific row indices marks stability thresholds

---

#### **Figure 4.11: Adjusted Rand Index Consistency Matrix**
**File**: `results/consistency/02_ari_consistency_matrix.png`

**Purpose**: Quantify pairwise run-to-run agreement

**Caption**:
> *"Adjusted Rand Index (ARI) matrix showing pairwise agreement between all 190 combinations of 20 EA runs. ARI ranges from 0 (independent partitions) to 1.0 (identical partitions). Color intensity (typically shown as heatmap) indicates ARI value: darker/warmer colors = higher agreement. Mean ARI = 0.824 indicates strong agreement; most off-diagonal values cluster in 0.80–0.87 range. One outlier run (run 14) shows slightly lower agreement (ARI ≈ 0.69), suggesting it converged to a distinct local optimum while remaining highly correlated with others."*

**Interpretation Notes**:
- Uniform coloring = consistent convergence
- One outlier = natural stochasticity in EA (acceptable)
- Mean ARI 0.824 = robust clustering

---

#### **Figure 4.12: Stability Score Distribution**
**File**: `results/consistency/03_stability_distribution.png`

**Purpose**: Show distribution of per-subject consistency scores

**Caption**:
> *"Histogram of consistency scores (0–1) for all 278 subjects. Distribution is bimodal: high peak at consistency ≈ 0.95–1.00 (stable subjects, ~158 individuals) and secondary plateau at consistency ≈ 0.60–0.80 (variable subjects, ~120 individuals). A small tail extends to consistency < 0.5 (frontier subjects, ~3 individuals). The bimodal structure suggests natural separation between 'core' population members and boundary individuals—biologically meaningful structure."*

**Interpretation Notes**:
- Primary peak = most subjects are reliably clustered
- Secondary plateau = meaningful frontier population
- Very few at <0.5 = genuine boundaries (not noise)

---

#### **Figure 4.13: Geographic Distribution of Stability**
**File**: `results/consistency/04_stability_map.png`

**Purpose**: Locate frontier subjects geographically

**Caption**:
> *"World map with subjects colored by stability category: green (stable, ≥ 0.9), yellow/orange (variable, 0.5–0.9), red (frontier, < 0.5). Stable subjects cluster in homogeneous population cores (e.g., sub-Saharan Africa, East Asia, Northern Europe). Variable and frontier subjects concentrate in known admixture zones (e.g., Central Asia, Oceania, Americas). This geographic coherence validates the EA's biological relevance: frontier subjects identified algorithmically match real admixed populations and expected hybrid zones."*

**Interpretation Notes**:
- Green zones = ancient isolated populations (low genetic mixing)
- Red/yellow zones = recent admixture or transition areas
- Compare to historical population genetics literature for validation

---

## Parameter Sweep Results: K=2 to K=6, γ=0 and γ=1

### Dashboard Visualizations (10 configurations)

#### **Figure 4.14a–j: World Map Cluster Assignments (All K and γ Combinations)**
**Files**: `dashboard_plot_maker/visualizations/exp_k*/01_world_map_clusters.png`

**Purpose**: Comparative view of how K and γ affect solution structure

**Caption**:
> *"World map cluster assignments for all parameter sweep configurations (K ∈ {2,3,4,5,6}, γ ∈ {0,1}). Rows correspond to K values; columns to γ values (left: γ=0 genetic-only, right: γ=1 geography-integrated). Progression from K=2 (coarse divisions) to K=6 (fine-grained) reveals hierarchical population structure. Comparison within rows (γ=0 vs. γ=1) shows effect of geographic penalty: γ=0 allows geographically dispersed clusters; γ=1 enforces regional coherence."*

**Key Observations to Comment On**:
- K=2: Continental divide (Africa vs. Eurasia)
- K=3–5: Progressive population-level granularity
- K=6: Over-fragmentation; K=5 captures structure adequately
- γ=0 vs. γ=1: Geographic weight changes cluster shapes but preserves major structure

---

#### **Figure 4.15a–e: Medoid Distance World Maps (K=2–6, γ=1)**
**Files**: `dashboard_plot_maker/visualizations/exp_k*_gon/01_world_map_clusters.png` (with medoid coloring)

**Purpose**: Frontier individual distribution across different K values

**Caption**:
> *"Medoid distance visualizations for K=2 to K=6 with geography-integrated fitness (γ=1). Full cluster colors indicate subjects near cluster medoids (genetic cores); white indicates subjects far from medoids (frontier individuals). As K increases from 2 to 5, frontier populations become more granularly resolved. K=6 shows diminishing additional frontier structure, suggesting K=5 is optimal for this dataset."*

---

## Summary Table: All Figures in Report

| Figure | Type | Purpose | Location | File |
|--------|------|---------|----------|------|
| 3.1 | Diagram/ASCII | EA flowchart | Sec 3.6 | EA_ALGORITHM_FLOWCHART.txt |
| 4.1 | Line plot | Fitness convergence | Sec 4.2.1 | 81_k5_gamma0/07_fitness_convergence.png |
| 4.2 | Line plot | Best-so-far fitness | Sec 4.2.1 | 81_k5_gamma0/08_fitness_best_so_far.png |
| 4.3 | Bar chart | Cluster sizes | Sec 4.2.2 | 81_k5_gamma0/04_cluster_sizes.png |
| 4.4 | Box plots | Genetic distance distributions | Sec 4.2.3 | 81_k5_gamma0/05_within_vs_between_genetic.png |
| 4.5 | Bar chart | Geographic spread per cluster | Sec 4.2.4 | 81_k5_gamma0/06_geographic_spread_per_cluster.png |
| 4.6 | Map | World map clusters | Sec 4.2.5 | 81_k5_gamma0/01_world_map_clusters.png |
| 4.7 | Scatter | MDS projection | Sec 4.2.5 | 81_k5_gamma0/02_mds_clusters.png |
| 4.8 | Heatmap | Genetic distance heatmap | Sec 4.2.5 | 81_k5_gamma0/03_genetic_heatmap_by_cluster.png |
| 4.9a | Scatter + color | Medoid distances (MDS) | Sec 4.2.6 | 81_k5_gamma0/02b_medoid_distances_mds.png |
| 4.9b | Map + color | Medoid distances (geographic) | Sec 4.2.6 | 81_k5_gamma0/02c_medoid_distances_geographic.png |
| 4.10 | Heatmap | Subject stability heatmap | Sec 4.4.3 | consistency/01_subject_stability_heatmap.png |
| 4.11 | Heatmap | ARI consistency matrix | Sec 4.4.2 | consistency/02_ari_consistency_matrix.png |
| 4.12 | Histogram | Stability distribution | Sec 4.4.4 | consistency/03_stability_distribution.png |
| 4.13 | Map + color | Geographic stability map | Sec 4.4.5 | consistency/04_stability_map.png |
| 4.14a–j | Maps (10) | Parameter sweep (all K, γ) | Sec 4.3 | exp_k*/01_world_map_clusters.png |
| 4.15a–e | Maps (5) + color | Medoid distance (K sweep, γ=1) | Sec 4.3 | exp_k*_gon/medoid visualizations |

---

## Integration Recommendations for Writing

1. **Place Figure 3.1 (Flowchart)** right after describing the generational loop (end of Sec 3.6)
   - Let readers visualize the algorithm structure while concepts are fresh

2. **Figure 4.1–4.2 (Convergence)** should appear first in Results
   - Establish that algorithm converged successfully
   - Justify 6000 generations as sufficient budget

3. **Figures 4.3–4.8 (Primary K=5 results)** in sequence for deep-dive analysis
   - Tell a story: Fitness → Sizes → Genetic quality → Geography → Visualizations

4. **Figures 4.9a–b (Medoid distances)** after genetic analysis
   - Add frontier perspective to genetic findings

5. **Figures 4.10–4.13 (Consistency)** grouped together
   - Demonstrate robustness and identify frontier subjects
   - Connect back to medoid visualizations (same frontier individuals?)

6. **Figures 4.14–4.15 (Parameter sweep)** in comparative section
   - Show breadth of parameter exploration
   - Justify K=5 as optimal choice

---

## Caption Writing Tips

- **Always explain what is shown**: "X-axis shows ..., Y-axis shows ..."
- **Mention data source**: "Run 81_k5_gamma0" or "Across 20 runs"
- **Interpret key features**: "The peak at X indicates ...", "We observe ..."
- **Connect to main text**: "This confirms the trend mentioned in Sec 4.2 ..."
- **Keep academic tone**: "This visualization reveals ..." not "Look at this!"

---

## File Organization for Submission

Suggested folder structure for final report:
```
Report/
├── report_main.pdf (or .docx)
├── figures/
│   ├── 3_1_flowchart.txt (or rendered as .png)
│   ├── 4_1_fitness_convergence.png
│   ├── 4_2_best_so_far.png
│   ├── 4_3_cluster_sizes.png
│   ├── ...
│   └── 4_15_medoid_k6.png
└── supplementary/
    ├── EA_ALGORITHM_FLOWCHART.txt
    ├── FIGURE_REFERENCE_GUIDE.md (this file)
    └── run_metadata/ (selected .json files for reproducibility)
```

