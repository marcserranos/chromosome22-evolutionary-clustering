"""Plots for the best partition found by the evolutionary algorithm."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from data_loader import load_subject_metadata, align_metadata


def mds_2d(distance_matrix):
    """Classical MDS into 2D from a distance matrix (no sklearn)."""
    d = np.asarray(distance_matrix, dtype=float)
    n = d.shape[0]
    h = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * h @ (d ** 2) @ h
    vals, vecs = np.linalg.eigh(b)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    vals = np.maximum(vals[:2], 0)
    return vecs[:, :2] * np.sqrt(vals)

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False


class Visualizations:
  def __init__(
      self,
      subject_names,
      chromosome,
      k_groups,
      genetic_matrix,
      geographic_matrix,
      fitness_history=None,
      metadata_df=None,
      output_dir=None,
  ):
      self.subject_names = subject_names
      self.chromosome = np.asarray(chromosome, dtype=int)
      self.k_groups = k_groups
      self.genetic_matrix = genetic_matrix
      self.geographic_matrix = geographic_matrix
      self.fitness_history = fitness_history
      self.n = len(subject_names)

      if metadata_df is None:
          metadata_df = load_subject_metadata()
      self.meta = align_metadata(subject_names, metadata_df)

      if output_dir is None:
          output_dir = (
              Path(__file__).resolve().parent.parent
              / "results"
              / "visualizations"
              / "ea"
          )
      self.output_dir = Path(output_dir)
      self.output_dir.mkdir(parents=True, exist_ok=True)

      self.colors = plt.cm.tab10(np.linspace(0, 1, max(k_groups, 1)))

  def plot_all(self):
      print(f"\nSaving plots to {self.output_dir}")
      if self.fitness_history:
          self.plot_fitness_convergence()
      self.plot_world_map()
      self.plot_mds()
      self.plot_cluster_heatmap()
      self.plot_cluster_sizes()
      self.plot_within_between_distances()
      self.plot_geographic_spread_per_cluster()
      print("All EA visualizations saved.")

  def _save(self, fig, name):
      path = self.output_dir / name
      fig.savefig(path, dpi=150, bbox_inches="tight")
      plt.close(fig)
      print(f"  {name}")

  def plot_fitness_convergence(self):
      h = self.fitness_history
      gens = h["generation"]
      best = h["best_fitness"]
      mean = h["mean_fitness"]
      worst = h["worst_fitness"]

      fig, ax = plt.subplots(figsize=(10, 5))
      ax.plot(gens, best, label="Best", color="#27ae60", linewidth=2)
      ax.plot(gens, mean, label="Mean", color="#2980b9", linewidth=1.5)
      ax.plot(gens, worst, label="Worst", color="#c0392b", linewidth=1, alpha=0.7)
      ax.set_xlabel("Generation")
      ax.set_ylabel("Fitness")
      ax.set_title("Fitness convergence over generations")
      ax.legend(loc="lower right")
      ax.grid(True, alpha=0.3)
      self._save(fig, "07_fitness_convergence.png")

      fig, ax = plt.subplots(figsize=(10, 5))
      best_only = np.maximum.accumulate(best)
      ax.plot(gens, best_only, color="#27ae60", linewidth=2)
      ax.set_xlabel("Generation")
      ax.set_ylabel("Best fitness so far")
      ax.set_title("Best fitness seen up to each generation")
      ax.grid(True, alpha=0.3)
      self._save(fig, "08_fitness_best_so_far.png")

  def plot_world_map(self):
      lat = self.meta["Latitude"].astype(float).values
      lon = self.meta["Longitude"].astype(float).values

      fig = plt.figure(figsize=(16, 9))
      if HAS_CARTOPY:
          ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
          ax.set_global()
          ax.add_feature(cfeature.OCEAN, facecolor="#d4e6f1")
          ax.add_feature(cfeature.LAND, facecolor="#e8e8e8")
          ax.coastlines(linewidth=0.4, color="#555555")
          ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5)
          transform = ccrs.PlateCarree()
      else:
          ax = fig.add_subplot(1, 1, 1)
          ax.set_xlim(-180, 180)
          ax.set_ylim(-60, 85)
          ax.set_facecolor("#d4e6f1")
          ax.grid(True, alpha=0.3)
          transform = None

      for c in range(self.k_groups):
          mask = self.chromosome == c
          kw = dict(s=55, alpha=0.85, color=self.colors[c], edgecolors="black", linewidths=0.4)
          if transform:
              ax.scatter(lon[mask], lat[mask], transform=transform, label=f"Cluster {c}", **kw)
          else:
              ax.scatter(lon[mask], lat[mask], label=f"Cluster {c}", **kw)

      ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
      ax.set_title("Subjects by EA cluster (world map)", fontsize=14, fontweight="bold")
      self._save(fig, "01_world_map_clusters.png")

  def plot_mds(self):
      coords = mds_2d(self.genetic_matrix)

      fig, ax = plt.subplots(figsize=(10, 8))
      for c in range(self.k_groups):
          mask = self.chromosome == c
          ax.scatter(
              coords[mask, 0],
              coords[mask, 1],
              c=[self.colors[c]],
              label=f"Cluster {c} (n={mask.sum()})",
              s=60,
              alpha=0.8,
              edgecolors="black",
              linewidths=0.4,
          )
      ax.set_xlabel("MDS 1")
      ax.set_ylabel("MDS 2")
      ax.set_title("Genetic space (MDS) colored by cluster")
      ax.legend(loc="best", fontsize=9)
      ax.grid(True, alpha=0.3)
      self._save(fig, "02_mds_clusters.png")

  def plot_cluster_heatmap(self):
      order = np.argsort(self.chromosome * self.n + np.arange(self.n))
      ordered = self.genetic_matrix[order][:, order]

      fig, ax = plt.subplots(figsize=(12, 10))
      im = ax.imshow(ordered, cmap="viridis", aspect="auto")
      plt.colorbar(im, ax=ax, label="Genetic distance", fraction=0.046)

      boundaries = [0]
      for c in range(self.k_groups):
          boundaries.append(boundaries[-1] + np.sum(self.chromosome[order] == c))
      for b in boundaries[1:-1]:
          ax.axhline(b - 0.5, color="white", linewidth=0.8)
          ax.axvline(b - 0.5, color="white", linewidth=0.8)

      ax.set_title("Genetic distances (subjects sorted by cluster)")
      ax.set_xlabel("Subject index (cluster blocks)")
      ax.set_ylabel("Subject index (cluster blocks)")
      patches = [
          mpatches.Patch(color=self.colors[c], label=f"Cluster {c}")
          for c in range(self.k_groups)
      ]
      ax.legend(handles=patches, loc="upper right", fontsize=8)
      self._save(fig, "03_genetic_heatmap_by_cluster.png")

  def plot_cluster_sizes(self):
      counts = [np.sum(self.chromosome == c) for c in range(self.k_groups)]
      fig, ax = plt.subplots(figsize=(8, 5))
      bars = ax.bar(range(self.k_groups), counts, color=self.colors[: self.k_groups], edgecolor="black")
      ax.set_xticks(range(self.k_groups))
      ax.set_xticklabels([f"Cluster {c}" for c in range(self.k_groups)])
      ax.set_ylabel("Number of subjects")
      ax.set_title("Cluster sizes")
      for bar, n in zip(bars, counts):
          ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(n), ha="center", fontsize=10)
      ax.grid(True, axis="y", alpha=0.3)
      self._save(fig, "04_cluster_sizes.png")

  def plot_within_between_distances(self):
      i, j = np.triu_indices(self.n, k=1)
      same = self.chromosome[i] == self.chromosome[j]
      within = self.genetic_matrix[i, j][same]
      between = self.genetic_matrix[i, j][~same]

      fig, ax = plt.subplots(figsize=(7, 5))
      ax.boxplot(
          [within, between],
          labels=["Within cluster", "Between clusters"],
          patch_artist=True,
          boxprops=dict(facecolor="#aed6f1"),
          medianprops=dict(color="red", linewidth=2),
      )
      ax.set_ylabel("Genetic distance")
      ax.set_title("Within vs between cluster genetic distance")
      ax.grid(True, axis="y", alpha=0.3)
      self._save(fig, "05_within_vs_between_genetic.png")

  def plot_geographic_spread_per_cluster(self):
      i, j = np.triu_indices(self.n, k=1)
      fig, axes = plt.subplots(1, self.k_groups, figsize=(4 * self.k_groups, 4), squeeze=False)

      for c in range(self.k_groups):
          ax = axes[0, c]
          mask_i = self.chromosome[i] == c
          mask_j = self.chromosome[j] == c
          pair_mask = mask_i & mask_j
          vals = self.geographic_matrix[i, j][pair_mask]
          if len(vals) > 0:
              ax.hist(vals, bins=30, color=self.colors[c], edgecolor="black", alpha=0.75)
          ax.set_title(f"Cluster {c}\ngeographic distance")
          ax.set_xlabel("km")
          if c == 0:
              ax.set_ylabel("Pair count")
          ax.grid(True, alpha=0.3)

      fig.suptitle("Geographic spread within each cluster", fontsize=13, fontweight="bold")
      fig.tight_layout()
      self._save(fig, "06_geographic_spread_per_cluster.png")
