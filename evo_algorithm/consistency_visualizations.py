"""
Visualizations for cluster consistency analysis across multiple runs.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from data_loader import load_subject_metadata, align_metadata


class ConsistencyVisualizations:
    """Create visualizations for stability and consistency analysis."""

    def __init__(self, subject_names, k_groups, stability_scores, cluster_assignments,
                 ari_matrix, metadata_df=None, output_dir=None):
        """
        Args:
            subject_names: list of subject identifiers
            k_groups: number of clusters
            stability_scores: dict from ConsistencyAnalyzer.compute_subject_stability
            cluster_assignments: dict from ConsistencyAnalyzer.compute_subject_stability
            ari_matrix: matrix from ConsistencyAnalyzer.compute_ari_matrix
            metadata_df: optional metadata with Latitude/Longitude for map
            output_dir: where to save plots
        """
        self.subject_names = subject_names
        self.k_groups = k_groups
        self.stability_scores = stability_scores
        self.cluster_assignments = cluster_assignments
        self.ari_matrix = ari_matrix
        self.num_subjects = len(subject_names)
        self.num_runs = ari_matrix.shape[0]

        if metadata_df is None:
            metadata_df = load_subject_metadata()
        self.metadata = align_metadata(subject_names, metadata_df)

        if output_dir is None:
            output_dir = Path(__file__).resolve().parent.parent / "results" / "consistency"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.colors = plt.cm.tab10(np.linspace(0, 1, max(k_groups, 1)))

    def _save(self, fig, name):
        """Save figure and close."""
        path = self.output_dir / name
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  {name}")

    def plot_all(self):
        """Create all consistency visualizations."""
        print(f"\nSaving consistency plots to {self.output_dir}")
        self.plot_subject_stability_heatmap()
        self.plot_ari_consistency_matrix()
        self.plot_stability_distribution()
        self.plot_stability_map()
        print("All consistency visualizations saved.")

    def plot_subject_stability_heatmap(self):
        """
        Heatmap: rows=subjects, cols=runs, color=cluster assignment.
        Subjects sorted by stability (most stable first).

        This is the most intuitive view: you can directly see which subjects
        are always in the same cluster (clean blocks) vs. which vary (scattered colors).
        """
        # Sort subjects by consistency (descending)
        sorted_indices = sorted(
            range(self.num_subjects),
            key=lambda i: self.stability_scores[i]['consistency_fraction'],
            reverse=True
        )

        # Build matrix: rows=sorted subjects, cols=runs
        matrix = np.zeros((self.num_subjects, self.num_runs))
        for row, subject_idx in enumerate(sorted_indices):
            assignments = np.array(self.cluster_assignments[subject_idx])
            matrix[row, :] = assignments

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 16))

        # Use cluster colors
        cmap = ListedColormap(self.colors[:self.k_groups])
        im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=self.k_groups - 1)

        # Labels
        ax.set_xlabel('Run number', fontsize=11)
        ax.set_ylabel('Subject (sorted by stability)', fontsize=11)
        ax.set_title('Subject cluster assignments across runs\n(rows sorted by consistency)', fontsize=13, fontweight='bold')
        ax.set_xticks(range(self.num_runs))
        ax.set_xticklabels([f'Run {i}' for i in range(self.num_runs)], rotation=45, ha='right')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, ticks=range(self.k_groups))
        cbar.set_label('Cluster ID', fontsize=10)

        # Add text annotations showing consistency on right side
        for row, subject_idx in enumerate(sorted_indices):
            consistency = self.stability_scores[subject_idx]['consistency_fraction']
            if consistency < 1.0:  # Only annotate non-perfect stability
                ax.text(self.num_runs + 0.3, row, f'{consistency:.2f}',
                       va='center', fontsize=7, color='red')

        plt.tight_layout()
        self._save(fig, "01_subject_stability_heatmap.png")

    def plot_ari_consistency_matrix(self):
        """
        Heatmap of pairwise ARI (Adjusted Rand Index) between all runs.
        Shows which runs are similar to each other (off-diagonal values).
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        im = ax.imshow(self.ari_matrix, cmap='RdYlGn', vmin=0, vmax=1)

        ax.set_xlabel('Run number', fontsize=11)
        ax.set_ylabel('Run number', fontsize=11)
        ax.set_title('Run-to-run similarity (Adjusted Rand Index)', fontsize=13, fontweight='bold')
        ax.set_xticks(range(self.num_runs))
        ax.set_yticks(range(self.num_runs))
        ax.set_xticklabels([f'Run {i}' for i in range(self.num_runs)])
        ax.set_yticklabels([f'Run {i}' for i in range(self.num_runs)])

        # Add text annotations
        for i in range(self.num_runs):
            for j in range(self.num_runs):
                ax.text(j, i, f'{self.ari_matrix[i, j]:.2f}',
                       ha="center", va="center", color="black", fontsize=9)

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('ARI (1.0 = identical)', fontsize=10)

        plt.tight_layout()
        self._save(fig, "02_ari_consistency_matrix.png")

    def plot_stability_distribution(self):
        """
        Histogram of consistency fractions across all subjects.
        Shows how many subjects are stable (1.0) vs. variable.
        """
        consistencies = np.array([s['consistency_fraction'] for s in self.stability_scores.values()])

        fig, ax = plt.subplots(figsize=(10, 6))

        bins = np.linspace(0, 1.05, 22)  # Bins: 0.0, 0.05, 0.10, ..., 1.0
        _, _, patches = ax.hist(consistencies, bins=bins, edgecolor='black', alpha=0.7)

        # Color bins: green for stable (1.0), red for variable (< 1.0)
        for i, patch in enumerate(patches):
            if bins[i+1] >= 1.0:
                patch.set_facecolor('green')
            elif bins[i+1] >= 0.8:
                patch.set_facecolor('yellow')
            else:
                patch.set_facecolor('red')

        ax.set_xlabel('Consistency fraction (% of runs in primary cluster)', fontsize=11)
        ax.set_ylabel('Number of subjects', fontsize=11)
        ax.set_title('Distribution of subject stability across runs', fontsize=13, fontweight='bold')
        ax.set_xlim(-0.05, 1.05)
        ax.grid(True, alpha=0.3, axis='y')

        # Add text showing key stats
        num_stable = np.sum(consistencies == 1.0)
        num_variable = np.sum((consistencies < 1.0) & (consistencies >= 0.8))
        num_frontier = np.sum(consistencies < 0.5)

        stats_text = f"Stable (1.0): {num_stable}\nVariable (0.8-1.0): {num_variable}\nFrontier (<0.5): {num_frontier}"
        ax.text(0.5, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='center',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        self._save(fig, "03_stability_distribution.png")

    def plot_stability_map(self):
        """
        World map with subjects colored by stability:
        - Green: consistent across all runs (1.0)
        - Yellow: mostly consistent (0.8-1.0)
        - Orange: moderate (0.5-0.8)
        - Red: frontier (< 0.5)
        """
        try:
            import geopandas as gpd
            HAS_GEOPANDAS = True
        except ImportError:
            HAS_GEOPANDAS = False

        lat = self.metadata["Latitude"].astype(float).values
        lon = self.metadata["Longitude"].astype(float).values

        # Define stability color map
        def get_stability_color(consistency):
            if consistency >= 0.99:
                return '#2ecc71'  # Green
            elif consistency >= 0.8:
                return '#f39c12'  # Orange
            elif consistency >= 0.5:
                return '#e67e22'  # Dark orange
            else:
                return '#e74c3c'  # Red

        colors_stability = [get_stability_color(self.stability_scores[i]['consistency_fraction'])
                           for i in range(self.num_subjects)]

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
        ax.set_facecolor("#e6f2ff")

        # Add world map
        if HAS_GEOPANDAS:
            try:
                world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
                world.plot(ax=ax, color="#d3d3d3", edgecolor="#333333", linewidth=0.5, alpha=0.7)
            except Exception:
                ax.grid(True, alpha=0.2)
        else:
            ax.grid(True, alpha=0.2)

        # Plot subjects
        ax.scatter(lon, lat, c=colors_stability, s=80, alpha=0.8, edgecolors='black', linewidths=0.5)

        ax.set_xlabel('Longitude', fontsize=11)
        ax.set_ylabel('Latitude', fontsize=11)
        ax.set_title('Subject stability across runs (world map)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.1)

        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor='#2ecc71', edgecolor='black', label='Stable (1.0)'),
            mpatches.Patch(facecolor='#f39c12', edgecolor='black', label='Mostly stable (0.8-1.0)'),
            mpatches.Patch(facecolor='#e67e22', edgecolor='black', label='Moderate (0.5-0.8)'),
            mpatches.Patch(facecolor='#e74c3c', edgecolor='black', label='Frontier (< 0.5)')
        ]
        ax.legend(handles=legend_elements, loc='lower left', fontsize=9, framealpha=0.95)

        plt.tight_layout()
        self._save(fig, "04_stability_map.png")
