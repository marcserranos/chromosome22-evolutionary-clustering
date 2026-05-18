#!/usr/bin/env python3
"""
Visualize SGDP data: PCA, distance heatmaps, geographic scatter.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.decomposition import PCA
from pathlib import Path
import seaborn as sns

RESULTS_DIR = Path("./results")
VIZ_DIR = Path("./visualizations")
VIZ_DIR.mkdir(exist_ok=True)

# Color scheme for regions
REGION_COLORS = {
    'Africa': '#e74c3c',
    'WestEurasia': '#3498db',
    'EastAsia': '#2ecc71',
    'SouthAsia': '#f39c12',
    'CentralAsia': '#9b59b6',
    'Oceania': '#1abc9c',
    'Americas': '#e67e22'
}

def load_data():
    """Load processed data and distance matrices."""
    print("\n=== Loading Data for Visualization ===")

    genotypes = np.load(Path("./processed_data/genotypes_filtered.npy"))
    samples_df = pd.read_csv(Path("./processed_data/samples_metadata_ordered.csv"))
    genetic_dist = np.load(RESULTS_DIR / "genetic_distance.npy")
    geographic_dist = np.load(RESULTS_DIR / "geographic_distance.npy")

    print(f"Genotypes: {genotypes.shape}")
    print(f"Samples: {len(samples_df)}")
    print(f"Distance matrices: {genetic_dist.shape}")

    return genotypes, samples_df, genetic_dist, geographic_dist

def plot_pca(genotypes, samples_df):
    """PCA on standardized genotypes, colored by region."""
    print("\n=== Computing PCA ===")

    # Standardize
    gt_clean = np.where(genotypes >= 0, genotypes, np.nan).T
    means = np.nanmean(gt_clean, axis=0)
    stds = np.nanstd(gt_clean, axis=0)
    stds[stds == 0] = 1
    gt_standardized = (gt_clean - means) / stds
    gt_standardized = np.nan_to_num(gt_standardized, nan=0.0)

    # PCA
    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(gt_standardized)

    print(f"✓ PCA computed")
    print(f"  PC1 variance: {pca.explained_variance_ratio_[0]:.1%}")
    print(f"  PC2 variance: {pca.explained_variance_ratio_[1]:.1%}")

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))

    regions = samples_df['Region'].unique()
    for region in regions:
        mask = samples_df['Region'] == region
        color = REGION_COLORS.get(region, '#95a5a6')
        ax.scatter(pca_coords[mask, 0], pca_coords[mask, 1],
                  label=region, s=100, alpha=0.7, color=color, edgecolors='black', linewidth=0.5)

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontsize=12)
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontsize=12)
    ax.set_title('PCA of SGDP Chr22 Genotypes (Individual-Level)', fontsize=14, fontweight='bold')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / "01_pca.png", dpi=150, bbox_inches='tight')
    print(f"✓ Saved: 01_pca.png")
    plt.close()

    return pca_coords

def plot_distance_heatmap(genetic_dist, samples_df):
    """Heatmap of genetic distances, clustered and colored by region."""
    print("\n=== Creating Distance Heatmap ===")

    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    # Use hierarchical clustering to order samples
    condensed_dist = squareform(genetic_dist)
    linkage_matrix = linkage(condensed_dist, method='ward')

    # Get order from dendrogram
    dendro = dendrogram(linkage_matrix, no_plot=True)
    order = dendro['leaves']

    # Reorder distance matrix
    dist_reordered = genetic_dist[order][:, order]

    # Plot
    fig, ax = plt.subplots(figsize=(14, 12))

    # Create heatmap
    im = ax.imshow(dist_reordered, cmap='viridis', aspect='auto')

    # Add region colors as strip on side (skip - too complex with hex colors)

    ax.set_title('Genetic Distance Matrix (Euclidean on Standardized Genotypes)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Sample Index (Hierarchically Clustered)', fontsize=10)
    ax.set_ylabel('Sample Index (Hierarchically Clustered)', fontsize=10)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Euclidean Distance', fontsize=10)

    # Legend for regions
    patches = [mpatches.Patch(color=color, label=region)
               for region, color in REGION_COLORS.items()]
    ax.legend(handles=patches, loc='upper right', framealpha=0.9, fontsize=10)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / "02_distance_heatmap.png", dpi=150, bbox_inches='tight')
    print(f"✓ Saved: 02_distance_heatmap.png")
    plt.close()

def plot_geographic_scatter(samples_df, genetic_dist):
    """Geographic scatter plot with genetic distance as point size."""
    print("\n=== Creating Geographic Scatter Plot ===")

    fig, ax = plt.subplots(figsize=(16, 10))

    regions = samples_df['Region'].unique()
    for region in regions:
        mask = samples_df['Region'] == region
        color = REGION_COLORS.get(region, '#95a5a6')
        ax.scatter(samples_df.loc[mask, 'Longitude'],
                  samples_df.loc[mask, 'Latitude'],
                  label=region, s=150, alpha=0.7, color=color,
                  edgecolors='black', linewidth=1)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('SGDP Sample Locations (Individual-Level)', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', framealpha=0.9, fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / "03_geographic_scatter.png", dpi=150, bbox_inches='tight')
    print(f"✓ Saved: 03_geographic_scatter.png")
    plt.close()

def plot_distance_distribution(genetic_dist, geographic_dist):
    """Compare distributions of genetic vs geographic distances."""
    print("\n=== Creating Distance Distribution Plots ===")

    # Extract upper triangular
    genetic_triu = genetic_dist[np.triu_indices_from(genetic_dist, k=1)]
    geographic_triu = geographic_dist[np.triu_indices_from(geographic_dist, k=1)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Genetic distance
    axes[0].hist(genetic_triu, bins=50, color='#3498db', alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('Euclidean Genetic Distance', fontsize=11)
    axes[0].set_ylabel('Frequency', fontsize=11)
    axes[0].set_title('Distribution of Genetic Distances\nBetween Individuals', fontsize=12, fontweight='bold')
    axes[0].axvline(np.mean(genetic_triu), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(genetic_triu):.2f}')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Geographic distance
    axes[1].hist(geographic_triu, bins=50, color='#2ecc71', alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Geographic Distance (km)', fontsize=11)
    axes[1].set_ylabel('Frequency', fontsize=11)
    axes[1].set_title('Distribution of Geographic Distances\nBetween Individuals', fontsize=12, fontweight='bold')
    axes[1].axvline(np.mean(geographic_triu), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(geographic_triu):.0f} km')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / "04_distance_distributions.png", dpi=150, bbox_inches='tight')
    print(f"✓ Saved: 04_distance_distributions.png")
    plt.close()

def plot_correlation(genetic_dist, geographic_dist, samples_df):
    """Correlation between genetic and geographic distance."""
    print("\n=== Creating Correlation Plot ===")

    # Extract upper triangular
    genetic_triu = genetic_dist[np.triu_indices_from(genetic_dist, k=1)]
    geographic_triu = geographic_dist[np.triu_indices_from(geographic_dist, k=1)]

    # Compute correlation
    corr = np.corrcoef(genetic_triu, geographic_triu)[0, 1]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(geographic_triu, genetic_triu, alpha=0.3, s=20, color='#3498db')

    # Add trend line
    z = np.polyfit(geographic_triu, genetic_triu, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(geographic_triu.min(), geographic_triu.max(), 100)
    ax.plot(x_trend, p(x_trend), "r--", linewidth=2, label=f'Trend line')

    ax.set_xlabel('Geographic Distance (km)', fontsize=12)
    ax.set_ylabel('Genetic Distance (Euclidean)', fontsize=12)
    ax.set_title(f'Correlation: Genetic vs Geographic Distance\n(Pearson r = {corr:.3f})',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(VIZ_DIR / "05_genetic_geographic_correlation.png", dpi=150, bbox_inches='tight')
    print(f"✓ Saved: 05_genetic_geographic_correlation.png")
    print(f"  Correlation (r): {corr:.3f}")
    plt.close()

# Main
if __name__ == "__main__":
    print("=" * 70)
    print("SGDP Data Visualization")
    print("=" * 70)

    genotypes, samples_df, genetic_dist, geographic_dist = load_data()

    pca_coords = plot_pca(genotypes, samples_df)
    plot_distance_heatmap(genetic_dist, samples_df)
    plot_geographic_scatter(samples_df, genetic_dist)
    plot_distance_distribution(genetic_dist, geographic_dist)
    plot_correlation(genetic_dist, geographic_dist, samples_df)

    print("\n" + "=" * 70)
    print(f"✓ All visualizations saved to: {VIZ_DIR.absolute()}")
    print("=" * 70)
