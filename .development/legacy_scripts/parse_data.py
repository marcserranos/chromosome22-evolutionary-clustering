#!/usr/bin/env python3
"""
Incremental SGDP chr22 data parsing and cleaning.
Individual-level analysis (no population aggregation).
"""

import pysam
import pandas as pd
import numpy as np
from pathlib import Path
import json

BCF_FILE = "./data/chr.sgdp.pub.22.bcf"
METADATA_FILE = "./data/SGDP_metadata.279public.21signedLetter.44Fan.samples.txt"
OUTPUT_DIR = Path("./processed_data")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_metadata():
    """Load and parse metadata file."""
    print("\n=== Loading Metadata ===")
    meta = pd.read_csv(METADATA_FILE, sep='\t', comment='#', encoding='latin-1')
    print(f"Loaded {len(meta)} sample records")
    print(f"Columns: {list(meta.columns)}")
    return meta

def parse_bcf_incremental(chunk_size=10000):
    """
    Parse BCF file in chunks to show progress.
    Returns: samples list, genotype matrix, variant info.
    """
    print("\n=== Parsing BCF File (Incremental) ===")

    bcf = pysam.VariantFile(BCF_FILE)
    samples = list(bcf.header.samples)
    n_samples = len(samples)

    print(f"Samples: {n_samples}")
    print(f"Sample names (first 5): {samples[:5]}")

    # Initialize storage
    genotypes = []  # Will be list of variant arrays
    variant_info = []  # CHROM, POS, REF, ALT

    print(f"\nReading variants in chunks of {chunk_size}...")
    chunk_num = 0

    for rec in bcf:
        # Extract genotypes for this variant
        gt_array = np.zeros(n_samples, dtype=np.int8)

        for i, sample_id in enumerate(samples):
            # Get genotype (0/0=0, 0/1=1, 1/1=2)
            gt = rec.samples[sample_id]['GT']
            if gt is not None:
                gt_array[i] = sum(gt)  # sum gives 0, 1, or 2
            else:
                gt_array[i] = -1  # missing

        genotypes.append(gt_array)
        variant_info.append({
            'chrom': rec.contig,
            'pos': rec.pos,
            'ref': rec.ref,
            'alt': rec.alts[0] if rec.alts else '.',
            'id': f"chr{rec.contig}_{rec.pos}"
        })

        chunk_num += 1
        if chunk_num % chunk_size == 0:
            print(f"  ✓ Read {chunk_num:,} variants...")

    bcf.close()

    # Convert to arrays
    genotypes = np.array(genotypes, dtype=np.int8)  # variants × samples
    variant_df = pd.DataFrame(variant_info)

    print(f"\n✓ Total variants read: {len(genotypes):,}")
    print(f"  Shape: {genotypes.shape[0]:,} variants × {genotypes.shape[1]} samples")
    print(f"  Memory: {genotypes.nbytes / (1024**3):.2f} GB")

    return samples, genotypes, variant_df

def filter_variants(genotypes, variant_df, maf_threshold=0.05):
    """
    Filter SNPs by:
    1. MAF > threshold
    2. Non-zero variance (not monomorphic)
    """
    print("\n=== Filtering Variants ===")
    n_initial = len(genotypes)

    # Handle missing values (-1)
    genotypes_clean = np.where(genotypes >= 0, genotypes, np.nan)

    # Compute allele frequencies (ignoring missing)
    allele_counts = np.nansum(genotypes_clean, axis=1)  # sum of alleles per SNP
    sample_counts = np.sum(~np.isnan(genotypes_clean), axis=1)  # count non-missing
    allele_freqs = allele_counts / (2 * sample_counts)  # freq of alt allele

    # Minor allele frequency
    maf = np.minimum(allele_freqs, 1 - allele_freqs)

    # Variance filter (remove monomorphic)
    variance = np.var(genotypes_clean, axis=1, nan_policy='propagate')

    # Apply filters
    maf_pass = maf >= maf_threshold
    var_pass = variance > 0
    pass_filter = maf_pass & var_pass

    # Report
    print(f"Initial variants: {n_initial:,}")
    print(f"  Failed MAF filter (< {maf_threshold}): {(~maf_pass).sum():,}")
    print(f"  Failed variance filter (monomorphic): {(~var_pass).sum():,}")
    print(f"  Passed filters: {pass_filter.sum():,} ({100*pass_filter.sum()/n_initial:.1f}%)")

    # Filter
    genotypes_filt = genotypes[pass_filter]
    variant_df_filt = variant_df[pass_filter].reset_index(drop=True)

    return genotypes_filt, variant_df_filt, maf[pass_filter], variance[pass_filter]

def compute_statistics(genotypes, samples):
    """Compute summary statistics on filtered genotypes."""
    print("\n=== Data Statistics ===")

    # Missing data
    n_missing = np.sum(genotypes < 0)
    pct_missing = 100 * n_missing / genotypes.size
    print(f"Missing values: {n_missing:,} ({pct_missing:.2f}%)")

    # Allele frequency distribution
    gt_valid = np.where(genotypes >= 0, genotypes, np.nan)
    allele_counts = np.nansum(gt_valid, axis=1)
    sample_counts = np.sum(~np.isnan(gt_valid), axis=1)
    allele_freqs = allele_counts / (2 * sample_counts)

    print(f"Allele frequency (alt allele):")
    print(f"  Mean: {np.mean(allele_freqs):.3f}")
    print(f"  Std: {np.std(allele_freqs):.3f}")
    print(f"  Range: {np.min(allele_freqs):.3f} - {np.max(allele_freqs):.3f}")

    # Per-sample stats
    print(f"\nPer-sample statistics:")
    gt_per_sample = np.nanmean(gt_valid, axis=0)
    print(f"  Mean genotype per sample: {np.mean(gt_per_sample):.3f}")
    print(f"  Range: {np.min(gt_per_sample):.3f} - {np.max(gt_per_sample):.3f}")

    # Missing per sample
    missing_per_sample = np.sum(genotypes < 0, axis=0)
    pct_per_sample = 100 * missing_per_sample / genotypes.shape[0]
    print(f"  Missing per sample:")
    print(f"    Mean: {np.mean(pct_per_sample):.2f}%")
    print(f"    Max: {np.max(pct_per_sample):.2f}% (sample: {samples[np.argmax(pct_per_sample)]})")

    return allele_freqs

def save_checkpoint(genotypes, variant_df, samples, metadata, stage_name):
    """Save intermediate results."""
    print(f"\n=== Saving Checkpoint: {stage_name} ===")

    np.save(OUTPUT_DIR / f"genotypes_{stage_name}.npy", genotypes)
    variant_df.to_csv(OUTPUT_DIR / f"variants_{stage_name}.csv", index=False)

    # Save sample metadata
    sample_meta = metadata[metadata['SGDP_ID'].isin(samples)].copy()
    sample_meta.to_csv(OUTPUT_DIR / f"samples_{stage_name}.csv", index=False)

    # Save index mapping
    with open(OUTPUT_DIR / f"sample_index_{stage_name}.json", 'w') as f:
        json.dump({s: i for i, s in enumerate(samples)}, f)

    print(f"✓ Saved: genotypes ({genotypes.shape}), variants ({len(variant_df)}), samples ({len(samples)})")

    return sample_meta

# Main pipeline
if __name__ == "__main__":
    print("=" * 70)
    print("SGDP Chr22 Data Parsing & Cleaning Pipeline")
    print("=" * 70)

    # Step 1: Load metadata
    metadata = load_metadata()

    # Step 2: Parse BCF
    samples, genotypes_raw, variant_df_raw = parse_bcf_incremental(chunk_size=100000)
    save_checkpoint(genotypes_raw, variant_df_raw, samples, metadata, "raw")

    # Step 3: Filter variants
    genotypes_filt, variant_df_filt, maf_vals, var_vals = filter_variants(genotypes_raw, variant_df_raw, maf_threshold=0.05)
    save_checkpoint(genotypes_filt, variant_df_filt, samples, metadata, "filtered")

    # Step 4: Statistics
    allele_freqs = compute_statistics(genotypes_filt, samples)

    print("\n" + "=" * 70)
    print("✓ Data parsing complete!")
    print(f"Ready for distance computation: {len(samples)} samples × {len(genotypes_filt)} variants")
    print("=" * 70)
