from collections import Counter
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sklearn.decomposition import PCA
from data_loader import load_distances
from fitness import FitnessEvaluator
from ea import EvolutionaryAlgorithm
from visualizations import Visualizations
from run_manager import RunManager


def get_run_name():
    """Prompt user for run name."""
    run_name = input("Enter run name: ").strip()
    if not run_name:
        raise ValueError("Run name cannot be empty")
    return run_name


def create_plot_data(run_dir, genetic_matrix, ea_history, lineage, subject_names):
    """Create plot_data folder with raw data for custom visualizations"""
    plot_data_dir = Path(run_dir) / "plot_data"
    plot_data_dir.mkdir(exist_ok=True)

    # 1. Lineage data (historic best fitness)
    lineage_path = plot_data_dir / "lineage.csv"
    with open(lineage_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['generation', 'fitness', 'chromosome'])
        for gen, individual in enumerate(lineage):
            chromosome_str = ','.join(map(str, individual.chromosome))
            writer.writerow([gen, individual.fitness, chromosome_str])

    # 2. Genetic PCA
    pca = PCA(n_components=3)
    pca_coords = pca.fit_transform(genetic_matrix)
    pca_path = plot_data_dir / "genetic_pca.csv"
    with open(pca_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['subject_index', 'subject_name', 'pc1', 'pc2', 'pc3'])
        for i, (coords, name) in enumerate(zip(pca_coords, subject_names)):
            writer.writerow([i, name, coords[0], coords[1], coords[2]])

    # Save PCA variance explained
    pca_var_path = plot_data_dir / "genetic_pca_variance.csv"
    with open(pca_var_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['component', 'variance_explained', 'cumulative_variance'])
        cumvar = 0
        for i, var in enumerate(pca.explained_variance_ratio_):
            cumvar += var
            writer.writerow([i+1, var, cumvar])

    # 3. Genetic distance heatmap (matrix)
    heatmap_path = plot_data_dir / "genetic_distance_matrix.csv"
    np.savetxt(heatmap_path, genetic_matrix, delimiter=',')

    # 4. Fitness evolution
    fitness_path = plot_data_dir / "fitness_evolution.csv"
    with open(fitness_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['generation', 'best_fitness', 'mean_fitness', 'worst_fitness'])
        for gen, best, mean, worst in zip(
            ea_history['generation'],
            ea_history['best_fitness'],
            ea_history['mean_fitness'],
            ea_history['worst_fitness']
        ):
            writer.writerow([gen, best, mean, worst])

    print(f"  Plot data saved to: plot_data/")
    return plot_data_dir


def save_lineage_csv(lineage, run_dir):
    """Save lineage to CSV: generation, fitness, chromosome"""
    csv_path = Path(run_dir) / "lineage.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['generation', 'fitness', 'chromosome'])
        for gen, individual in enumerate(lineage):
            chromosome_str = ','.join(map(str, individual.chromosome))
            writer.writerow([gen, individual.fitness, chromosome_str])
    print(f"  Lineage saved: {csv_path.name}")
    return csv_path


def create_world_map_animation(lineage, k_groups, subject_names, metadata_df, run_dir):
    """Create animation of world map with cluster evolution"""
    try:
        import geopandas as gpd
        HAS_GEOPANDAS = True
    except ImportError:
        HAS_GEOPANDAS = False
        print(f"  World map animation skipped (geopandas not available)")
        return

    lat = metadata_df["Latitude"].astype(float).values
    lon = metadata_df["Longitude"].astype(float).values
    colors = plt.cm.tab10(np.linspace(0, 1, k_groups))

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_facecolor("#e6f2ff")

    if HAS_GEOPANDAS:
        try:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            world.plot(ax=ax, color="#d3d3d3", edgecolor="#333333", linewidth=0.5, alpha=0.7)
        except Exception:
            ax.grid(True, alpha=0.2)
    else:
        ax.grid(True, alpha=0.2)

    def animate(frame):
        ax.clear()
        if HAS_GEOPANDAS:
            try:
                world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
                world.plot(ax=ax, color="#d3d3d3", edgecolor="#333333", linewidth=0.5, alpha=0.7)
            except Exception:
                ax.grid(True, alpha=0.2)
        else:
            ax.grid(True, alpha=0.2)

        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
        ax.set_facecolor("#e6f2ff")

        individual = lineage[frame]
        chromosome = individual.chromosome
        for c in range(k_groups):
            mask = np.array(chromosome) == c
            ax.scatter(lon[mask], lat[mask], s=55, alpha=0.85, color=colors[c],
                      edgecolors="black", linewidths=0.4, label=f"Cluster {c}")

        ax.legend(loc="lower left", fontsize=8, framealpha=0.95)
        ax.set_title(f"Lineage evolution - Generation {frame} (fitness: {individual.fitness:.4f})",
                    fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.1)

    anim = FuncAnimation(fig, animate, frames=len(lineage), repeat=True)
    for ext in ['mp4', 'gif']:
        try:
            output_path = Path(run_dir) / f"lineage_world_map_animation.{ext}"
            anim.save(str(output_path), fps=60, dpi=100)
            print(f"  World map animation saved: {output_path.name}")
            plt.close(fig)
            return
        except Exception:
            continue
    plt.close(fig)
    print(f"  World map animation skipped (ffmpeg not available)")


def main():
    '''runs experiments as desired, rifht now it's short in options, will be further
    improved for modularity and experiment variability'''

    # Get run name and setup directory
    run_name = get_run_name()
    run_manager = RunManager()

    genetic, geographic, subject_names = load_distances() # loads data
    from data_loader import load_subject_metadata, align_metadata
    metadata_df = load_subject_metadata()
    metadata_df = align_metadata(subject_names, metadata_df)

    num_subjects = len(subject_names)
    k_groups = 5 # define K number (main parameter)
    min_group_size = max(1, num_subjects // (k_groups * 10)) # can be changed

    # Prepare parameters for metadata
    parameters = {
        "k_groups": k_groups,
        "population_size": 50,
        "generations": 6000,
        "crossover_rate": 0.9,
        "mutation_rate": 0.005,
        "elitism_count": 2,
        "alpha": 1,
        "beta": 1,
        "gamma": 1,
        "offset": 1.0,
        "cluster_balance_penalty": 0.0001,
        "min_group_size": min_group_size
    }

    # Setup run directory and save metadata
    run_dir = run_manager.setup_run(run_name, parameters)
    print(f"\nRun directory: {run_dir}\n")

    # class initialization using parameters dict
    evaluator = FitnessEvaluator(
        genetic_matrix=genetic,
        geographic_matrix=geographic,
        k_groups=parameters["k_groups"],
        alpha=parameters["alpha"],
        beta=parameters["beta"],
        gamma=parameters["gamma"],
        offset=parameters["offset"],
        cluster_balance_penalty=parameters["cluster_balance_penalty"],
        min_group_size=parameters["min_group_size"]
    )
    ea = EvolutionaryAlgorithm(
        num_subjects=num_subjects,
        k_groups=parameters["k_groups"],
        population_size=parameters["population_size"],
        generations=parameters["generations"],
        crossover_rate=parameters["crossover_rate"],
        mutation_rate=parameters["mutation_rate"],
        elitism_count=parameters["elitism_count"],
        evaluator=evaluator
    )

    # Extract fitness function from evaluator and save to metadata
    fitness_function = evaluator.get_fitness_formula()
    run_manager.metadata["fitness_function"] = fitness_function
    run_manager._save_metadata()
    print(f"Fitness function: {fitness_function}\n")

    # runs the evolutionary algorithm
    best = ea.run()
    counts = Counter(best.chromosome)
    print("\nDone.")
    print(f"Best fitness: {best.fitness:.4f}")
    print(f"Cluster sizes: {dict(sorted(counts.items()))}")

    # save lineage of best individual
    print("\nLineage tracking:")
    lineage = ea.get_lineage(best)
    lineage = ea.sample_lineage(lineage, num_samples=300)
    save_lineage_csv(lineage, run_dir)
    create_world_map_animation(lineage, k_groups, subject_names, metadata_df, run_dir)

    # create plot data for custom visualizations
    print("\nPlot data:")
    create_plot_data(run_dir, genetic, ea.history, lineage, subject_names)

    # shows cluster distribution
    for cluster in range(k_groups):
        names = [
            subject_names[i]
            for i, label in enumerate(best.chromosome)
            if label == cluster
        ]
        print(f"\nCluster {cluster} ({len(names)} subjects), first 10:")
        for name in names[:10]:
            print(f"  {name}")
        if len(names) > 10:
            print(f"  ... and {len(names) - 10} more")

    # creates plots with run-specific directory
    Visualizations(subject_names=subject_names,chromosome=best.chromosome,k_groups=k_groups,genetic_matrix=genetic,geographic_matrix=geographic,fitness_history=ea.history,output_dir=run_dir).plot_all()

if __name__ == "__main__":
    main()
