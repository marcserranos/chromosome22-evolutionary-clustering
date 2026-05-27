from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Allow running both:
# - python -m dashboard_plot_maker.generate_dashboard_plots
# - python dashboard_plot_maker/generate_dashboard_plots.py
try:
    from dashboard_plot_maker.style import apply_dashboard_style, cluster_color, style_axes
except ModuleNotFoundError:  # running as a script from within the package folder
    from style import apply_dashboard_style, cluster_color, style_axes


def _read_last_chromosome(lineage_csv: Path) -> List[int]:
    last_row = None
    with lineage_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            last_row = row
    if last_row is None:
        raise ValueError(f"Empty lineage CSV: {lineage_csv}")

    chromo_cell = last_row["chromosome"]
    chromo = [int(x) for x in chromo_cell.split(",") if x.strip() != ""]
    return chromo


def _load_pca_scatter(pca_csv: Path, chromo: List[int]) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    pc1: List[float] = []
    pc2: List[float] = []
    clusters: List[int] = []

    with pca_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row["subject_index"])
            pc1.append(float(row["pc1"]))
            pc2.append(float(row["pc2"]))
            cid = chromo[idx] if 0 <= idx < len(chromo) else 0
            clusters.append(cid)

    return np.asarray(pc1, dtype=float), np.asarray(pc2, dtype=float), clusters


def _read_pca_variance(variance_csv: Path) -> Tuple[float, float]:
    # expects rows with:
    # component,variance_explained,cumulative_variance
    # component is 1-indexed for PC1/PC2.
    pc1_var = None
    pc2_var = None
    with variance_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            comp = int(row["component"])
            var = float(row["variance_explained"])
            if comp == 1:
                pc1_var = var
            elif comp == 2:
                pc2_var = var
    if pc1_var is None or pc2_var is None:
        # fallback: 0 if missing
        return 0.0, 0.0
    return pc1_var, pc2_var


def _load_matrix_csv(path: Path) -> np.ndarray:
    """
    Load a matrix from CSV.

    Supported formats:
    - Raw numeric matrix (no header): each row is a list of floats separated by commas
    - Labeled matrix (header + row labels): first row contains column names, first column contains row names
    """
    try:
        return np.loadtxt(str(path), delimiter=",", dtype=float)
    except ValueError:
        # Labeled matrix format with a header and an initial row-label column.
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            _header = next(reader, None)
            rows: List[List[float]] = []
            for row in reader:
                if not row:
                    continue
                # Skip first cell (row label), parse the rest as floats.
                vals = [float(x) for x in row[1:] if str(x).strip() != ""]
                rows.append(vals)
        return np.asarray(rows, dtype=float)


def make_genetic_pca(input_dir: Path, output_path: Path) -> None:
    lineage_csv = input_dir / "lineage.csv"
    pca_csv = input_dir / "genetic_pca.csv"
    variance_csv = input_dir / "genetic_pca_variance.csv"

    chromo = _read_last_chromosome(lineage_csv)
    pc1, pc2, clusters = _load_pca_scatter(pca_csv, chromo)
    pc1_var, pc2_var = _read_pca_variance(variance_csv)

    apply_dashboard_style()
    fig, ax = plt.subplots(figsize=(10, 7))

    colors = [cluster_color(int(cid)) for cid in clusters]
    ax.scatter(
        pc1,
        pc2,
        s=35,
        c=colors,
        alpha=0.92,
        edgecolors="#ffffff",
        linewidths=0.7,
    )

    ax.set_xlabel(f"PC1 ({pc1_var * 100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pc2_var * 100:.1f}%)")
    ax.set_title("Genetic PCA (colored by last generation clusters)")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def make_genetic_distance_heatmap(input_dir: Path, output_path: Path) -> None:
    lineage_csv = input_dir / "lineage.csv"
    genetic_matrix_csv = input_dir / "genetic_distance_matrix.csv"

    chromo = _read_last_chromosome(lineage_csv)
    chromo_arr = np.asarray(chromo, dtype=int)
    n = chromo_arr.shape[0]
    dist = _load_matrix_csv(genetic_matrix_csv)
    if dist.shape != (n, n):
        raise ValueError(f"Genetic matrix shape {dist.shape} != (n,n) {(n, n)}")

    k = int(np.max(chromo_arr)) + 1 if n > 0 else 0

    order = np.argsort(chromo_arr * n + np.arange(n))
    ordered = dist[order][:, order]

    # Determine cluster block boundaries in the ordered representation.
    sorted_clusters = chromo_arr[order]
    boundaries: List[int] = []
    running = 0
    for c in range(k):
        cnt = int(np.sum(sorted_clusters == c))
        running += cnt
        if c != k - 1:
            boundaries.append(running)

    apply_dashboard_style()
    fig, ax = plt.subplots(figsize=(11, 9))

    im = ax.imshow(ordered, cmap="viridis", aspect="auto")
    plt.colorbar(im, ax=ax, label="Genetic distance", fraction=0.046)

    for b in boundaries:
        # white gridline between cluster blocks
        ax.axhline(b - 0.5, color="#ffffff", linewidth=0.9)
        ax.axvline(b - 0.5, color="#ffffff", linewidth=0.9)

    ax.set_title("Genetic distances (subjects sorted by cluster)")
    ax.set_xlabel("Subject index (cluster blocks)")
    ax.set_ylabel("Subject index (cluster blocks)")
    style_axes(ax)

    # Legend: only for clusters we might have (0..k-1)
    # Note: clusters 5 & 6 are white, but we still include them for completeness.
    from matplotlib.patches import Patch

    patches = [Patch(color=cluster_color(c), label=f"Cluster {c}") for c in range(k)]
    leg = ax.legend(handles=patches, loc="upper right")
    for t in leg.get_texts():
        t.set_color("#ffffff")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def make_fitness_evolution(input_dir: Path, output_path: Path) -> None:
    fitness_csv = input_dir / "fitness_evolution.csv"

    gens: List[int] = []
    best: List[float] = []
    mean: List[float] = []
    worst: List[float] = []

    with fitness_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gens.append(int(row["generation"]))
            best.append(float(row["best_fitness"]))
            mean.append(float(row["mean_fitness"]))
            worst.append(float(row["worst_fitness"]))

    apply_dashboard_style()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    gens_arr = np.asarray(gens, dtype=int)

    # Lines mostly white to match the dashboard’s emphasis.
    ax.plot(gens_arr, best, label="Best", color="#ffffff", linewidth=2.6, alpha=0.98)
    ax.plot(gens_arr, mean, label="Mean", color="#ffffff", linewidth=2.0, alpha=0.78)
    ax.plot(gens_arr, worst, label="Worst", color="#ffffff", linewidth=1.6, alpha=0.58)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.set_title("Fitness evolution (per generation)")
    leg = ax.legend(loc="lower right")
    for t in leg.get_texts():
        t.set_color("#ffffff")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def make_genetic_geo_correlation(input_dir: Path, output_path: Path) -> None:
    lineage_csv = input_dir / "lineage.csv"
    genetic_matrix_csv = input_dir / "genetic_distance_matrix.csv"

    # Prefer a geo matrix inside plot_data; otherwise use the repo-wide static one.
    geo_matrix_csv = input_dir / "geographic_distance_matrix.csv"
    if not geo_matrix_csv.exists():
        # Typical relative layout:
        # results/runs/<run>/plot_data  -> repo/results
        repo_results_dir = input_dir.parents[2]  # .../results
        geo_matrix_csv = repo_results_dir / "distances" / "geographic_distance.csv"

    chromo = _read_last_chromosome(lineage_csv)
    chromo_arr = np.asarray(chromo, dtype=int)

    dist_gen = _load_matrix_csv(genetic_matrix_csv)
    dist_geo = _load_matrix_csv(geo_matrix_csv)

    n = chromo_arr.shape[0]
    if dist_gen.shape != (n, n) or dist_geo.shape != (n, n):
        raise ValueError(
            f"Distance matrices must match n. Got genetic={dist_gen.shape}, geo={dist_geo.shape}, n={n}"
        )

    i, j = np.triu_indices(n, k=1)
    x = dist_geo[i, j]
    y = dist_gen[i, j]
    pair_cluster = chromo_arr[i]

    apply_dashboard_style()
    fig, ax = plt.subplots(figsize=(10, 7))

    unique_clusters = np.unique(pair_cluster)
    for cid in unique_clusters:
        mask = pair_cluster == cid
        ax.scatter(
            x[mask],
            y[mask],
            s=10,
            color=cluster_color(int(cid)),
            alpha=0.35,
            linewidths=0,
        )

    ax.set_xlabel("Geographic distance (km)")
    ax.set_ylabel("Genetic distance")
    ax.set_title("Genetic ↔ Geographic distance correlation (upper triangle)")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate styled dashboard-compatible matplotlib plots from plot_data.")
    ap.add_argument("--input", required=True, help="Path to a run's plot_data/ folder")
    ap.add_argument(
        "--output",
        default=None,
        help="Output folder (defaults to dashboard_plot_maker/visualizations/<run_name>/)",
    )
    args = ap.parse_args()

    input_dir = Path(args.input).resolve()
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        # If input is .../results/runs/<run_name>/plot_data, keep output isolated:
        # dashboard_plot_maker/visualizations/<run_name>/
        run_name = input_dir.parent.name
        repo_root = Path(__file__).resolve().parents[1]
        output_dir = repo_root / "dashboard_plot_maker" / "visualizations" / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    make_genetic_pca(input_dir, output_dir / "genetic_pca.png")
    make_genetic_distance_heatmap(input_dir, output_dir / "heatmap.png")
    make_fitness_evolution(input_dir, output_dir / "fitness_evolution.png")
    make_genetic_geo_correlation(input_dir, output_dir / "gen_geo_correlation.png")

    print(f"Plots written to: {output_dir}")


if __name__ == "__main__":
    main()

