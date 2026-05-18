# SGDP Chr22 Analysis Pipeline

## Overview
Individual-level analysis of 278 SGDP individuals using Chromosome 22 variants.
**No population aggregation** — each individual analyzed directly.

## Data Flow

```
Raw BCF (1.1M variants × 278 individuals)
        ↓
    [parse_data.py]
        ↓
   Checkpoint: raw
   ├─ genotypes_raw.npy (1.1M × 278)
   ├─ variants_raw.csv
   ├─ samples_raw.csv
        ↓
   Filtering (MAF > 0.05, non-varying)
        ↓
   Checkpoint: filtered
   ├─ genotypes_filtered.npy (~400k × 278)
   ├─ variants_filtered.csv
   ├─ samples_filtered.csv
        ↓
    [compute_distances.py]
        ↓
   Euclidean genetic distance (278 × 278)
   Haversine geographic distance (278 × 278)
        ↓
    [visualize_data.py]
        ↓
   Visualizations:
   ├─ 01_pca.png
   ├─ 02_distance_heatmap.png
   ├─ 03_geographic_scatter.png
   ├─ 04_distance_distributions.png
   └─ 05_genetic_geographic_correlation.png
        ↓
   Ready for Evolutionary Algorithm
```

## Scripts

### 1. **parse_data.py** (Running Now)
- **Input:** BCF file + metadata
- **Steps:**
  1. Load metadata (345 samples → 278 in BCF)
  2. Parse BCF incrementally (1.1M variants)
  3. Filter SNPs: MAF > 0.05, remove monomorphic
  4. Save checkpoints (raw & filtered)
  5. Compute statistics & distributions

- **Output:** Genotype matrix (278 individuals × ~400k SNPs)
- **Time:** ~5-10 min

### 2. **compute_distances.py** (Next)
- **Input:** Filtered genotypes + samples metadata
- **Steps:**
  1. Standardize genotypes (z-score per variant)
  2. Compute Euclidean distance between all pairs
  3. Compute Haversine geographic distance
  4. Save distance matrices

- **Output:** 2 distance matrices (278 × 278)
- **Time:** ~2-3 min

### 3. **visualize_data.py** (After distances)
- **Input:** Genotypes + distance matrices + metadata
- **Steps:**
  1. PCA on standardized genotypes → 2D projection
  2. Hierarchical clustering of distance matrix
  3. Create 5 diagnostic plots
  4. Compute genetic-geographic correlation

- **Output:** 5 PNG visualizations
- **Time:** ~2-3 min

## Validation Checks

**At each stage:**
- ✓ Dimensions match (278 samples consistent)
- ✓ Missing data handled (marked as -1, then imputed as 0)
- ✓ Standardization applied (mean=0, std=1 per variant)
- ✓ Distances valid (non-negative, symmetric)

## Next: Evolutionary Algorithm

Once visualizations confirm data quality:
1. Design fitness function: `α·genetic_separation - β·genetic_variance - γ·geographic_scatter`
2. Implement EA operators: selection, crossover, mutation
3. Run for K=5 (and test K=2,3,4)
4. Analyze partition stability

## Configuration (Tunable)

```python
MAF_THRESHOLD = 0.05  # Minor allele frequency filter
K_CLUSTERS = 5         # Number of clusters to find
POPULATION_LEVEL = False  # Use individuals, not populations
```

## Expected Results

- ~400k SNPs after filtering (~36% of original 1.1M)
- PCA: first 2 components explain ~5-10% variance
- Genetic distances: 0-20 (Euclidean scale)
- Geographic distances: 0-20000 km
- Correlation genetic-geographic: ~0.3-0.5 (moderate)
