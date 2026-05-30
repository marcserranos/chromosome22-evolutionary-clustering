#!/usr/bin/env python3
"""
FASTER incremental SGDP parsing - test version with early exit option.
"""

import pysam
import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys

BCF_FILE = "./data/chr.sgdp.pub.22.bcf"
METADATA_FILE = "./data/SGDP_metadata.279public.21signedLetter.44Fan.samples.txt"
OUTPUT_DIR = Path("./processed_data")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_VARIANTS = None  # Set to 10000 to test on subset, None for full

def load_metadata():
    """Load metadata."""
    print("\n=== Loading Metadata ===", flush=True)
    meta = pd.read_csv(METADATA_FILE, sep='\t', comment='#', encoding='latin-1')
    print(f"✓ Loaded {len(meta)} samples", flush=True)
    return meta

def parse_bcf_fast(chunk_print=100000):
    """Parse BCF with frequent progress updates."""
    print("\n=== Parsing BCF ===", flush=True)

    bcf = pysam.VariantFile(BCF_FILE)
    samples = list(bcf.header.samples)
    n_samples = len(samples)

    print(f"Samples: {n_samples}", flush=True)

    genotypes = []
    variant_info = []
    count = 0

    for rec in bcf:
        gt_array = np.array([sum(rec.samples[s]['GT'] or (0, 0)) for s in samples], dtype=np.int8)
        genotypes.append(gt_array)
        variant_info.append({'chrom': rec.contig, 'pos': rec.pos, 'ref': rec.ref, 'alt': rec.alts[0] if rec.alts else '.'})

        count += 1
        if count % chunk_print == 0:
            print(f"  {count:,} variants...", flush=True)

        if MAX_VARIANTS and count >= MAX_VARIANTS:
            print(f"  (Stopped at {count:,} for testing)", flush=True)
            break

    bcf.close()

    genotypes = np.array(genotypes, dtype=np.int8)
    variant_df = pd.DataFrame(variant_info)

    print(f"✓ Parsed: {count:,} variants × {n_samples} samples", flush=True)
    return samples, genotypes, variant_df

def filter_snps(genotypes, variant_df, maf_th=0.05):
    """Filter variants."""
    print("\n=== Filtering SNPs ===", flush=True)

    gt_clean = np.where(genotypes >= 0, genotypes, np.nan)
    allele_counts = np.nansum(gt_clean, axis=1)
    sample_counts = np.sum(~np.isnan(gt_clean), axis=1)
    allele_freqs = allele_counts / (2 * sample_counts)
    maf = np.minimum(allele_freqs, 1 - allele_freqs)
    variance = np.nanvar(gt_clean, axis=1)

    maf_pass = maf >= maf_th
    var_pass = variance > 0
    pass_filter = maf_pass & var_pass

    print(f"Initial: {len(genotypes):,}", flush=True)
    print(f"  MAF filter: -{(~maf_pass).sum():,}", flush=True)
    print(f"  Variance filter: -{(~var_pass).sum():,}", flush=True)
    print(f"  Passed: {pass_filter.sum():,} ({100*pass_filter.sum()/len(genotypes):.1f}%)", flush=True)

    return genotypes[pass_filter], variant_df[pass_filter].reset_index(drop=True)

def save_all(genotypes, variant_df, samples, metadata, stage):
    """Save checkpoint."""
    print(f"\n=== Saving {stage} ===", flush=True)
    np.save(OUTPUT_DIR / f"genotypes_{stage}.npy", genotypes)
    variant_df.to_csv(OUTPUT_DIR / f"variants_{stage}.csv", index=False)
    sample_meta = metadata[metadata['SGDP_ID'].isin(samples)].copy()
    sample_meta.to_csv(OUTPUT_DIR / f"samples_{stage}.csv", index=False)
    with open(OUTPUT_DIR / f"sample_index_{stage}.json", 'w') as f:
        json.dump({s: i for i, s in enumerate(samples)}, f)
    print(f"✓ Saved: genotypes {genotypes.shape}, variants {len(variant_df)}", flush=True)

if __name__ == "__main__":
    print("="*60)
    print("SGDP Parsing (Fast Version)")
    print("="*60, flush=True)

    metadata = load_metadata()
    samples, genotypes_raw, variant_df_raw = parse_bcf_fast()

    print(f"\n→ Filtering...", flush=True)
    genotypes_filt, variant_df_filt = filter_snps(genotypes_raw, variant_df_raw)

    print(f"\n→ Saving checkpoints...", flush=True)
    save_all(genotypes_raw, variant_df_raw, samples, metadata, "raw")
    save_all(genotypes_filt, variant_df_filt, samples, metadata, "filtered")

    print("\n" + "="*60)
    print(f"✓ COMPLETE: {len(samples)} samples × {len(genotypes_filt)} SNPs")
    print("="*60, flush=True)
