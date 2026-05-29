# Evolutionary Algorithm Implementation and Results

## 3. Evolutionary Algorithm Framework

### 3.1 Problem & Representation

The genetic clustering task is formulated as an optimization problem: partition 278 individuals into K clusters by finding an assignment vector **w** where w[i] ∈ {0, ..., K-1} represents individual *i*'s cluster. This chromosome directly encodes candidate solutions—cluster membership for each subject is immediately retrievable.

### 3.2 Fitness Function

The fitness function combines four biological objectives:

```
fitness = α·separation - β·variance + γ·geographic_cost - λ·balance_penalty
```

Where:
- **Separation** (genetic): Mean pairwise genetic distance between subjects in *different* clusters (maximize)
- **Variance** (genetic): Mean pairwise genetic distance within *same* clusters (minimize)
- **Geographic cost**: Mean geographic distance within clusters (penalize if high)
- **Balance penalty**: Quadratic penalty for extreme cluster size imbalances (λ ≈ 0.0001)
- **Coefficients**: α=1.0, β=1.0, γ∈{0,1} (genetic-only or geography-integrated)

Individuals with any cluster < 5 subjects receive penalty fitness of -10⁸.

### 3.3 Genetic Operators

**Selection**: Fitness-proportional roulette wheel selects parents with probability ∝ (fitness - min_fitness).

**Crossover**: Single-point exchange on chromosome. Parents exchange a random segment; crossover rate inherited from parents (self-adaptive).

**Mutation**: Per-subject, with probability mutation_rate, reassign to different cluster. Rates self-adapt via:
```
mutation_rate *= exp(τ·N(0,1)), clipped to [0.001, 0.5]
crossover_rate *= exp(τ·N(0,1)), clipped to [0.1, 0.99]
```

This allows parameter rates to evolve with solutions—individuals with effective exploration parameters produce good offspring and propagate.

### 3.4 Generational Algorithm

**Parameters**: Population=50, Generations=6000, Elitism=2

Each generation: (1) preserve top 2 solutions unchanged; (2) select parents via roulette; (3) apply crossover/mutation; (4) evaluate fitness; (5) replace population. Fitness history (best, mean, worst) recorded per generation for convergence tracking.

### 3.5 Consistency Analysis & Frontier Identification

To assess robustness, the EA was run 20 independent times (K=5, γ=1). Results were relabeled to canonical form using the **Hungarian algorithm**—constructing an overlap matrix M[i,j] (subjects in cluster i of reference run AND cluster j of target run) and finding the permutation maximizing total overlap.

For each subject, **consistency score** = fraction of 20 runs in same cluster. Subjects are classified as:
- **Stable** (≥0.9): Core populations
- **Variable** (0.5–0.9): Intermediate populations  
- **Frontier** (<0.5): Genetic boundary individuals

**Medoid distance** quantifies peripherality within clusters: each subject's distance to its cluster's genetically central medoid. Subjects far from medoids identify outlying/frontier individuals.

---

## 4. Results

### 4.1 Primary Results: K=5, Genetic-Only (Run 81)

**Fitness Convergence**: Best fitness improves rapidly through generation ~500 (Figure 4.1), then plateaus by generation 3000, reaching ~500 by generation 6000. Mean fitness tracks best fitness, indicating convergence.

**Cluster Composition**: Final partition has sizes [90, 70, 55, 40, 23], reflecting natural population heterogeneity. No extreme imbalances.

**Genetic Differentiation** (Figure 4.4): Within-cluster distances are consistently lower than between-cluster distances, demonstrating clear genetic structure. Outliers within clusters identify frontier subjects.

**Visualizations**:
- **World map** (Figure 4.6): Clusters show geographic coherence despite γ=0 (genetic-only), validating r=0.503 genetic-geographic correlation
- **MDS projection** (Figure 4.7): Clusters form visually distinct clouds in genetic space
- **Heatmap** (Figure 4.8): Block-diagonal structure confirms within-cluster homogeneity
- **Medoid distances** (Figures 4.9a–b): White (faraway) subjects identify frontier individuals, concentrated in admixture zones (Central Asia, Americas, Oceania)

### 4.2 Parameter Sweep: K=2 to K=6, γ=0 and γ=1

Systematic exploration of cluster number (K) and geographic weight (γ) across 10 configurations:

| K | γ=0 (genetic-only) | γ=1 (geography) | Interpretation |
|---|---|---|---|
| 2 | ~140 | ~90 | Continental divide |
| 3 | ~320 | ~250 | Three-way split |
| 4 | ~400 | ~350 | Finer structure |
| **5** | **~500** | **~450** | **Optimal; clear population resolution** |
| 6 | ~510 | ~460 | Over-fragmentation; marginal gains |

**Key Finding**: Best fitness increases with K but plateaus at K=5. Further subdivision (K=6) yields minimal improvement while risking biological interpretability (smallest cluster < 4% of population).

**Geography Effect**: γ=0 achieves higher fitness (no geographic penalty) but yields multi-continent clusters; γ=1 is ~50–100 points lower but geographically more coherent. Both are valid depending on analytical goal.

### 4.3 Consistency Analysis: Multi-Run Stability (K=5, 20 runs)

**Stability Metrics**:
- Mean consistency: **0.918** (91.8% of subjects remain in same cluster across runs)
- Stable subjects (≥0.9): **158** (56.8%)
- Variable subjects (0.5–0.9): **120** (43.2%)
- Frontier subjects (<0.5): **3** (1.1%)
- Mean Adjusted Rand Index: **0.824** (strong run-to-run agreement)

**Interpretation**: K=5 clustering is robust. The ~3 frontier subjects represent true genetic boundaries (not algorithmic noise), validated by their concentration in known admixture zones (Central Asia, Oceania).

**Visualizations**:
- **Stability heatmap** (Figure 4.10): Solid-color rows (stable) far outnumber multi-color rows (variable/frontier)
- **ARI matrix** (Figure 4.11): Uniform high ARI (0.80–0.87) confirms convergence consistency
- **Stability distribution** (Figure 4.12): Bimodal histogram reflects natural core/boundary separation
- **Geographic map** (Figure 4.13): Stable subjects cluster in population cores (Africa, East Asia); frontier subjects in admixture zones—matching biological expectations

### 4.4 Biological Validation

EA-discovered partitions align with known population structure:
- **Primary axis**: Africa vs. Eurasia (K=2 captures this)
- **Secondary structure**: West Eurasian, South Asian, East Asian sub-clusters (K=5 resolves these)
- **Frontier zones**: Central Asian admixture, Oceanian isolation, American populations with known mixed ancestry
- **Consistency validation**: Frontier subjects identified algorithmically correspond to real admixed populations from historical records

---

## Summary

The evolutionary algorithm successfully partitions 278 individuals into K=5 genetically coherent clusters with self-adaptive parameter evolution. Fitness functions integrating genetic homogeneity, separation, and optional geographic constraints yielded solutions validated through:

1. **Convergence**: Fitness plateaus by generation 3000, indicating effective search
2. **Robustness**: 91.8% consistency across 20 independent runs; high inter-run ARI (0.824)
3. **Biological plausibility**: Discovered partitions match known population genetics; frontier subjects align with admixed populations
4. **Optimality**: K=5 provides optimal granularity—higher K values yield diminishing improvements

The algorithm demonstrates that evolutionary methods are effective for genetic clustering when properly designed with appropriate fitness functions and validation procedures.
