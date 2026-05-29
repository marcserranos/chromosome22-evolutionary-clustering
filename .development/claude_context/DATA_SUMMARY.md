# SGDP Chr22 Data Summary

## Download Status
✅ **Complete** - 1.0 GB total (~0.95 GB BCF + 0.05 MB metadata)

## Files

### 1. Chromosome 22 VCF Data
- **File:** `data/chr.sgdp.pub.22.bcf` (942 MB)
- **Format:** BCF (binary VCF, phased)
- **Samples:** 278 individuals
- **Variants:** 1,096,476 SNPs
- **Index:** `data/chr.sgdp.pub.22.bcf.csi` (25 KB)

### 2. Metadata
- **File:** `data/SGDP_metadata.279public.21signedLetter.44Fan.samples.txt` (53 KB)
- **Rows:** 345 samples (includes 279 SGDP + some duplicates/notes)
- **Key columns:**
  - `SGDP_ID`: Sample identifier
  - `Population_ID`: Population name (e.g., "Australian", "Crete")
  - `Region`: Major region (Africa, Oceania, WestEurasia, EastAsia, CentralAsia, SouthAsia, Americas)
  - `Latitude` / `Longitude`: Geographic coordinates
  - `Gender`, `Country`, `Town`: Additional metadata

## Data Preparation Tasks

### Phase 1: Data Parsing
- Parse BCF and extract genotypes for 278 samples × 1,096,476 variants
- Parse metadata and map sample IDs to population IDs and coordinates
- Validate sample name matching between BCF and metadata

### Phase 2: Aggregation & Filtering
- Aggregate to **population level** (278 individuals → ~130 populations)
- Compute **allele frequencies** per population per SNP
- Apply **MAF filtering** (>0.05)
- Remove non-varying SNPs
- Output: `populations × SNPs` allele frequency matrix

### Phase 3: Distance Matrices
- Compute **F_ST** matrix (population-level genetic distance)
- Compute **Haversine** distance matrix (geographic distance)
- Validate against expected continent/region structure

### Phase 4: EA Input Preparation
- Package allele freq matrix + distance matrices + population coordinates
- Structure ready for Evolutionary Algorithm
- Include K=5 config + later allow dynamic K

## Next Steps
1. ✅ Data downloaded
2. → Write data parsing script (bcf → genotypes + metadata integration)
3. → Aggregation to population level (genotypes → allele frequencies)
4. → Distance computations
5. → Visualization check (PCA, map)
