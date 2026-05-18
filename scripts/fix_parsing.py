#!/usr/bin/env python3
"""
Fix parsing - properly handle metadata and complete filtering.
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path

OUTPUT_DIR = Path("./processed_data")
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_metadata_correctly():
    """Parse metadata with explicit column names."""
    print("\n=== Loading Metadata ===", flush=True)

    col_names = [
        'Sequencing_Panel', 'Illumina_ID', 'Sample_ID', 'Sample_ID_Aliases',
        'SGDP_ID', 'Population_ID', 'Region', 'Country', 'Town', 'Contributor',
        'Gender', 'Latitude', 'Longitude', 'DNA_Source', 'Embargo', 'SGDP_lite'
    ]

    meta = pd.read_csv(
        "data/SGDP_metadata.279public.21signedLetter.44Fan.samples.txt",
        sep='\t',
        comment='#',
        encoding='latin-1',
        header=None,  # No header - we'll set manually
        names=col_names
    )

    # Convert coordinates to numeric
    meta['Latitude'] = pd.to_numeric(meta['Latitude'], errors='coerce')
    meta['Longitude'] = pd.to_numeric(meta['Longitude'], errors='coerce')

    print(f"✓ Loaded {len(meta)} samples", flush=True)
    print(f"  Columns: {list(meta.columns)}", flush=True)
    return meta

def filter_and_save():
    """Load raw data, filter, save filtered."""
    print("\n=== Loading Raw Data ===", flush=True)

    genotypes_raw = np.load(OUTPUT_DIR / "genotypes_raw.npy")
    variants_raw = pd.read_csv(OUTPUT_DIR / "variants_raw.csv")
    metadata = parse_metadata_correctly()

    print(f"Raw genotypes: {genotypes_raw.shape}", flush=True)
    print(f"Raw variants: {len(variants_raw)}", flush=True)

    # Filter SNPs
    print("\n=== Filtering SNPs ===", flush=True)

    gt_clean = np.where(genotypes_raw >= 0, genotypes_raw, np.nan)
    allele_counts = np.nansum(gt_clean, axis=1)
    sample_counts = np.sum(~np.isnan(gt_clean), axis=1)
    allele_freqs = allele_counts / (2 * sample_counts)
    maf = np.minimum(allele_freqs, 1 - allele_freqs)
    variance = np.nanvar(gt_clean, axis=1)

    maf_pass = maf >= 0.05
    var_pass = variance > 0
    pass_filter = maf_pass & var_pass

    n_initial = len(genotypes_raw)
    n_passed = pass_filter.sum()

    print(f"Initial variants: {n_initial:,}", flush=True)
    print(f"  Failed MAF (< 0.05): {(~maf_pass).sum():,}", flush=True)
    print(f"  Failed variance (monomorphic): {(~var_pass).sum():,}", flush=True)
    print(f"  Passed: {n_passed:,} ({100*n_passed/n_initial:.1f}%)", flush=True)

    # Apply filter
    genotypes_filt = genotypes_raw[pass_filter]
    variants_filt = variants_raw[pass_filter].reset_index(drop=True)

    print(f"\nFiltered shape: {genotypes_filt.shape}", flush=True)

    # Save filtered
    print("\n=== Saving Filtered Data ===", flush=True)

    np.save(OUTPUT_DIR / "genotypes_filtered.npy", genotypes_filt)
    variants_filt.to_csv(OUTPUT_DIR / "variants_filtered.csv", index=False)

    metadata.to_csv(OUTPUT_DIR / "samples_metadata.csv", index=False)

    print(f"✓ Saved filtered genotypes: {genotypes_filt.shape}", flush=True)
    print(f"✓ Saved {len(variants_filt)} variant positions", flush=True)
    print(f"✓ Saved metadata for all samples", flush=True)

    return genotypes_filt, variants_filt, metadata

if __name__ == "__main__":
    print("="*60)
    print("Fix: Complete Parsing & Filtering")
    print("="*60, flush=True)

    genotypes_filt, variants_filt, metadata = filter_and_save()

    # Quick stats
    print("\n=== Data Statistics ===", flush=True)

    gt_valid = np.where(genotypes_filt >= 0, genotypes_filt, np.nan)
    allele_counts = np.nansum(gt_valid, axis=1)
    sample_counts = np.sum(~np.isnan(gt_valid), axis=1)
    allele_freqs = allele_counts / (2 * sample_counts)

    print(f"Allele frequency distribution:", flush=True)
    print(f"  Mean: {np.mean(allele_freqs):.3f}", flush=True)
    print(f"  Std: {np.std(allele_freqs):.3f}", flush=True)
    print(f"  Min-Max: {np.min(allele_freqs):.3f} - {np.max(allele_freqs):.3f}", flush=True)

    print(f"\nMissing data: {np.sum(genotypes_filt < 0):,} / {genotypes_filt.size:,} ({100*np.sum(genotypes_filt<0)/genotypes_filt.size:.2f}%)", flush=True)

    print(f"\nSample regions:", flush=True)
    for region in sorted(metadata['Region'].unique()):
        n = (metadata['Region'] == region).sum()
        print(f"  {region}: {n}", flush=True)

    print("\n" + "="*60)
    print(f"✓ READY: {genotypes_filt.shape[1]} samples × {genotypes_filt.shape[0]} SNPs")
    print("="*60, flush=True)
