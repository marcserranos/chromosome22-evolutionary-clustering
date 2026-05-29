# Project Guidelines

## Core Architecture

**Analysis Level:** Population-level (aggregated allele frequency matrix: populations × SNPs)

**Genetic Distance:** Pairwise F_ST computed directly from allele frequencies

**Geography (γ):** Integrated into fitness function from day one; penalties geographic scatter via Haversine distance

**Cluster Target (K):** Start with K=5, but code must allow dynamic K exploration later

## Data & Filtering

- **Filtering:** MAF > 0.05, non-varying SNPs removed
- **LD Pruning:** Deferred for later optimization
- **Inputs:** Chromosome 22 VCF (SGDP), individual-to-population metadata, population lat/lon coordinates

## Tech Stack & Policy

**Environment:** Python, local VS Code (Cursor)

**Dependencies:** Only standard libraries allowed (numpy, pandas, scikit-allel) for data prep/math

**Custom EA Engine:** Zero black-box libraries for core evolutionary algorithm. Full custom implementation, visible and auditable.

## Key Constraints

- No pre-built clustering/optimization libraries (scikit-learn clustering, scipy optimization, etc.) for the EA core
- All evolutionary operators (selection, crossover, mutation) must be explicitly coded
- Geography constraint is non-negotiable—fitness balances genetics + spatial coherence

## Success Criteria

✓ Functional custom EA implementation  
✓ Population partitions into K=5 groups  
✓ Visualizations: map + genetic PCA by group  
✓ Fitness evolution plots  
✓ Comparison across K values (2, 3, 4, 5)  
✓ Biological interpretation against known superpopulations
