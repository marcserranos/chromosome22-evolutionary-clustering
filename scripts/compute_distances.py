#!/usr/bin/env python3
"""
Compute pairwise distances between individuals.
- Genetic distance: Euclidean on standardized genotypes
- Geographic distance: Haversine on lat/lon
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy.spatial.distance import pdist, squareform
from scipy.spatial.distance import euclidean as euclidean_dist

OUTPUT_DIR = Path("./processed_data")
RESULTS_DIR = Path("./results")
RESULTS_DIR.mkdir(exist_ok=True)

def load_filtered_data():
    """Load the filtered genotypes and metadata."""
    print("\n=== Loading Filtered Data ===")

    genotypes = np.load(OUTPUT_DIR / "genotypes_filtered.npy")
    variants_df = pd.read_csv(OUTPUT_DIR / "variants_filtered.csv")
    samples_df = pd.read_csv(OUTPUT_DIR / "samples_metadata_ordered.csv")

    print(f"Genotypes shape: {genotypes.shape}")
    print(f"Variants: {len(variants_df)}")
    print(f"Samples: {len(samples_df)}")

    # Verify dimensions match
    if samples_df.shape[0] != genotypes.shape[1]:
        raise ValueError(f"Mismatch: {samples_df.shape[0]} samples but {genotypes.shape[1]} genotypes")

    return genotypes, variants_df, samples_df

def compute_genetic_distance_euclidean(genotypes):
    """
    Compute Euclidean distance on standardized genotypes.
    Handles missing values (-1).
    """
    print("\n=== Computing Genetic Distance (Euclidean) ===")

    # Replace missing (-1) with NaN for processing
    gt_clean = np.where(genotypes >= 0, genotypes, np.nan).T  # samples × variants

    # Standardize: (x - mean) / std per variant
    means = np.nanmean(gt_clean, axis=0)
    stds = np.nanstd(gt_clean, axis=0)
    stds[stds == 0] = 1  # avoid division by zero

    gt_standardized = (gt_clean - means) / stds

    # Replace NaN (from missing data) with 0 (neutral value)
    gt_standardized = np.nan_to_num(gt_standardized, nan=0.0)

    print(f"Standardized genotypes shape: {gt_standardized.shape}")

    # Compute pairwise Euclidean distance
    print("Computing pairwise distances...")
    distances = squareform(pdist(gt_standardized, metric='euclidean'))

    print(f"✓ Distance matrix shape: {distances.shape}")
    print(f"  Mean distance: {np.mean(distances[np.triu_indices_from(distances, k=1)]):.3f}")

    return distances

def haversine_distance(lat1, lon1, lat2, lon2):
    """Compute Haversine distance in km."""
    from math import radians, cos, sin, asin, sqrt

    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

def compute_geographic_distance(samples_df):
    """
    Compute pairwise geographic distance using Haversine formula.
    """
    print("\n=== Computing Geographic Distance (Haversine) ===")

    n = len(samples_df)
    distances = np.zeros((n, n))

    lats = samples_df['Latitude'].values
    lons = samples_df['Longitude'].values

    for i in range(n):
        if i % 50 == 0:
            print(f"  Processing sample {i}/{n}...")
        for j in range(i + 1, n):
            d = haversine_distance(lats[i], lons[i], lats[j], lons[j])
            distances[i, j] = d
            distances[j, i] = d

    print(f"✓ Geographic distance matrix computed")
    print(f"  Mean distance: {np.mean(distances[np.triu_indices_from(distances, k=1)]):.0f} km")
    print(f"  Max distance: {np.max(distances):.0f} km")

    return distances

def save_distances(genetic_dist, geographic_dist, samples_df):
    """Save distance matrices and summary."""
    print("\n=== Saving Distance Matrices ===")

    np.save(RESULTS_DIR / "genetic_distance.npy", genetic_dist)
    np.save(RESULTS_DIR / "geographic_distance.npy", geographic_dist)

    # Create DataFrames with sample names
    sample_names = samples_df['SGDP_ID'].values
    genetic_df = pd.DataFrame(genetic_dist, index=sample_names, columns=sample_names)
    geographic_df = pd.DataFrame(geographic_dist, index=sample_names, columns=sample_names)

    genetic_df.to_csv(RESULTS_DIR / "genetic_distance.csv")
    geographic_df.to_csv(RESULTS_DIR / "geographic_distance.csv")

    print("✓ Saved:")
    print("  - genetic_distance.npy")
    print("  - geographic_distance.npy")
    print("  - genetic_distance.csv")
    print("  - geographic_distance.csv")

    return genetic_df, geographic_df

# Main
if __name__ == "__main__":
    print("=" * 70)
    print("Distance Computation: Genetic & Geographic")
    print("=" * 70)

    genotypes, variants_df, samples_df = load_filtered_data()

    genetic_dist = compute_genetic_distance_euclidean(genotypes)
    geographic_dist = compute_geographic_distance(samples_df)

    genetic_df, geographic_df = save_distances(genetic_dist, geographic_dist, samples_df)

    print("\n" + "=" * 70)
    print("✓ Distance computation complete!")
    print("=" * 70)
