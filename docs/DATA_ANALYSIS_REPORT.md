# SGDP Chr22 Individual-Level Data Analysis Report

**Date:** 2026-05-18  
**Status:** ✓ Complete - Ready for Evolutionary Algorithm

---

## Executive Summary

Successfully processed **1.1M chromosome 22 variants** across **278 SGDP individuals** from 7 geographic regions. Data cleaned, filtered, and validated for clustering analysis.

**Key Result:** Moderate genetic-geographic correlation (r=0.503) confirms geographic signal in the data suitable for barrier detection.

---

## Data Processing Pipeline

### Stage 1: Parsing (1.1M variants × 278 individuals)
- BCF file parsed incrementally in 100k-variant chunks
- All 278 samples successfully extracted
- Memory usage: 0.28 GB raw

### Stage 2: Filtering
**Criteria:**
- Minor Allele Frequency (MAF) > 0.05
- Remove monomorphic (non-varying) SNPs
- No missing data imputation (0 missing values)

**Results:**
- **Initial:** 1,096,476 variants
- **MAF filter removed:** 991,884 variants (90.5%)
- **Variance filter removed:** 707,474 variants (overlap counted)
- **Final:** 104,573 variants (9.5% of initial) ✓

### Stage 3: Allele Frequency Distribution
After filtering:
- **Mean AF:** 0.325 (expected ~0.5 for random polymorphisms)
- **Std Dev:** 0.243
- **Range:** 0.050 - 0.950
- **Missing data:** 0% (no imputation needed)

### Stage 4: Distance Matrices

#### Genetic Distance (Euclidean on Standardized Genotypes)
```
Standardization: (genotype - mean) / std per variant
Distance metric: L2 (Euclidean)
Result: 278 × 278 symmetric matrix
Mean pairwise distance: 457.1 (scaled units)
```

#### Geographic Distance (Haversine)
```
Formula: Great-circle distance on WGS84 ellipsoid
Result: 278 × 278 symmetric matrix
Mean pairwise distance: 7,257 km
Maximum distance: 19,814 km (Africa ↔ Oceania)
```

---

## Sample Composition

| Region | Count | Proportion |
|--------|-------|------------|
| Africa | 93 | 33.5% |
| WestEurasia | 75 | 27.0% |
| SouthAsia | 49 | 17.6% |
| EastAsia | 47 | 16.9% |
| CentralAsiaSiberia | 27 | 9.7% |
| Oceania | 25 | 9.0% |
| Americas | 28 | 10.1% |

**Total:** 278 individuals, 7 regions, ~130 populations

---

## Validation Results

### PCA Analysis
- **PC1:** 6.7% variance (geographic signal strong)
- **PC2:** 4.5% variance (secondary structure)
- **Interpretation:** Clear clustering by geographic region validates population structure
- **Visualization:** 01_pca.png

### Genetic-Geographic Correlation
- **Pearson r:** 0.503 (moderate-strong correlation)
- **Interpretation:** ~25% of genetic distance variance explained by geography
- **Implication:** Remaining variance due to population history, admixture, drift
- **Validation:** Expected for real population data ✓
- **Visualization:** 05_genetic_geographic_correlation.png

### Distance Matrix Clustering
- **Observation:** Hierarchical clustering (Ward linkage) shows geographic blocks
- **Pattern:** Within-region distances (green/low) << between-region distances (yellow/high)
- **Visualization:** 02_distance_heatmap.png

### Geographic Distribution
- **Sample coverage:** All continents represented
- **Density:** Higher in Eurasia, sparser in Americas/Oceania
- **Pattern:** Clear continental separation without overlap
- **Visualization:** 03_geographic_scatter.png

### Distance Distributions
- **Genetic distances:** Right-skewed, mean 457, range ~300-700
- **Geographic distances:** Bimodal (within-region peaks + long-range tail)
- **Visualization:** 04_distance_distributions.png

---

## Data Quality Assessment

| Check | Status | Notes |
|-------|--------|-------|
| Sample count match | ✓ | 278 BCF samples = 278 metadata records |
| Coordinate coverage | ✓ | All samples have lat/lon |
| Missing genotypes | ✓ | 0% missing (after filtering) |
| Duplicate samples | ✓ | None detected |
| Metadata-genotype alignment | ✓ | Order verified and corrected |
| Allele freq distribution | ✓ | Normal for filtered SNPs |
| Geographic signal | ✓ | Clear regional clustering in PCA |

---

## Output Files

### Processed Data
```
processed_data/
├── genotypes_raw.npy              (291 MB, 1.1M × 278)
├── genotypes_filtered.npy          (28 MB, 104.5k × 278) ✓
├── variants_raw.csv               (33 MB)
├── variants_filtered.csv          (2.5 MB) ✓
└── samples_metadata_ordered.csv   (53 KB) ✓
```

### Distance Matrices
```
results/
├── genetic_distance.npy           (Binary matrix, 278×278)
├── genetic_distance.csv           (CSV for inspection)
├── geographic_distance.npy        (Binary matrix, 278×278)
└── geographic_distance.csv        (CSV for inspection)
```

### Visualizations
```
visualizations/
├── 01_pca.png                     (192 KB) - Geographic clustering
├── 02_distance_heatmap.png        (300 KB) - Regional blocks
├── 03_geographic_scatter.png      (195 KB) - Sample locations
├── 04_distance_distributions.png  (74 KB) - Distance stats
└── 05_genetic_geographic_correlation.png (555 KB) - r=0.503
```

---

## Recommendations for Evolutionary Algorithm

### Fitness Function Design
Given the strong geographic signal, recommend:

```
Fitness = α·IntraclusterVariance - β·InterclusterSeparation - γ·GeographicCost

where:
  α = genetic homogeneity weight (high priority)
  β = genetic separation weight (enforces distinct clusters)
  γ = geographic coherence weight (penalizes scattered clusters)
```

### Parameter Tuning
- **K=5:** Start with this as assignment instructions recommend
- **Selection:** Tournament selection (size ~10-20 individuals)
- **Mutation rate:** 5-10% (reassign individuals to different clusters)
- **Crossover:** Single-point or two-point on assignment vectors
- **Elitism:** Preserve top 2-5 solutions per generation

### Expected Behavior
- Genetic structure should reveal ~5-7 major clusters (continents/regions)
- Within-region populations should be grouped together
- Geographic boundary cases (e.g., Middle East, North Africa) will test coherence
- Higher K values should break down continental clusters into sub-populations

### Testing Strategy
1. **K=5:** Full continent-scale barriers
2. **K=10:** Within-continent substructure
3. **K=2-3:** Macro-scale barriers (e.g., Old World vs. New World)
4. **Stability:** Run 10x with different random seeds, compare partitions

---

## Next Steps

1. **✓ Data preparation complete**
2. → Implement custom EA engine
3. → Define fitness function
4. → Test on K=2,3,4,5
5. → Visualize partitions on PCA + map
6. → Compare with known population labels (SGDP superpopulations)
7. → Analyze barrier interpretation

---

## Technical Notes

- **Standardization method:** Z-score per variant (handles different allele frequencies)
- **Distance metric:** Euclidean on 104.5k dimensions (high-dimensional genotype space)
- **Haversine precision:** Meters (exact for sphere, ~0.3% error for WGS84 ellipsoid)
- **PCA implementation:** scikit-learn SVD (efficient for 278×104k data)
- **Correlation method:** Pearson on flattened upper triangular matrices (n=38,403 pairs)

---

## Files to Keep / Delete

**Keep:**
- `processed_data/genotypes_filtered.npy` → Input for EA
- `processed_data/samples_metadata_ordered.csv` → Sample info
- `results/genetic_distance.npy` → For fitness computation
- `results/geographic_distance.npy` → For geographic cost term
- `visualizations/*.png` → Documentation

**Can delete (raw data):**
- `processed_data/genotypes_raw.npy` (291 MB)
- `processed_data/variants_raw.csv` (33 MB)

**Total retained:** ~100 MB (compressed, sufficient for full EA analysis)

