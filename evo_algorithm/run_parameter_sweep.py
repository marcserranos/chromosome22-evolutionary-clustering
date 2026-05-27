#!/usr/bin/env python
"""
Parameter sweep: run EA for all combinations of k and gamma.
Loops through k=[2,3,4,5,6] and gamma=[0,1] automatically.
Each run produces normal outputs in results/runs/.
"""

import time
import csv
import numpy as np
from collections import Counter
from pathlib import Path
from data_loader import load_distances, load_subject_metadata, align_metadata
from fitness import FitnessEvaluator
from ea import EvolutionaryAlgorithm
from visualizations import Visualizations
from run_manager import RunManager


def create_plot_data(run_dir, genetic_matrix, ea_history, lineage, subject_names):
    """Create plot_data folder with raw data for custom visualizations"""
    from sklearn.decomposition import PCA

    plot_data_dir = Path(run_dir) / "plot_data"
    plot_data_dir.mkdir(exist_ok=True)

    lineage_path = plot_data_dir / "lineage.csv"
    with open(lineage_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['generation', 'fitness', 'chromosome'])
        for gen, individual in enumerate(lineage):
            chromosome_str = ','.join(map(str, individual.chromosome))
            writer.writerow([gen, individual.fitness, chromosome_str])

    pca = PCA(n_components=3)
    pca_coords = pca.fit_transform(genetic_matrix)
    pca_path = plot_data_dir / "genetic_pca.csv"
    with open(pca_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['subject_index', 'subject_name', 'pc1', 'pc2', 'pc3'])
        for i, (coords, name) in enumerate(zip(pca_coords, subject_names)):
            writer.writerow([i, name, coords[0], coords[1], coords[2]])

    pca_var_path = plot_data_dir / "genetic_pca_variance.csv"
    with open(pca_var_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['component', 'variance_explained', 'cumulative_variance'])
        cumvar = 0
        for i, var in enumerate(pca.explained_variance_ratio_):
            cumvar += var
            writer.writerow([i+1, var, cumvar])

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

    heatmap_path = plot_data_dir / "genetic_distance_matrix.csv"
    np.savetxt(heatmap_path, genetic_matrix, delimiter=',')

    print(f"  Plot data saved to: plot_data/")

# ============================================================================
# PARAMETER SWEEP CONFIGURATION
# ============================================================================

K_VALUES = [2, 3, 4, 5, 6]
GAMMA_VALUES = [0, 1]

# Base parameters (same as main.py)
POPULATION_SIZE = 50
GENERATIONS = 6000
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.005
ELITISM_COUNT = 2
ALPHA = 1.0
BETA = 1.0
OFFSET = 1.0
CLUSTER_BALANCE_PENALTY = 0.0001

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    # Load data once
    print("Loading data...")
    genetic, geographic, subject_names = load_distances()
    metadata_df = load_subject_metadata()
    metadata_df = align_metadata(subject_names, metadata_df)
    num_subjects = len(subject_names)

    run_manager = RunManager()
    total_runs = len(K_VALUES) * len(GAMMA_VALUES)
    run_count = 0
    loop_start = time.time()

    print(f"\n{'='*60}")
    print(f"Running {total_runs} parameter combinations")
    print(f"K: {K_VALUES}, Gamma: {GAMMA_VALUES}")
    print(f"{'='*60}\n")

    # Loop through all combinations
    for k_groups in K_VALUES:
        for gamma in GAMMA_VALUES:
            run_count += 1
            run_name = f"k{k_groups}_gamma{gamma}"
            min_group_size = max(1, num_subjects // (k_groups * 10))

            print(f"\n[{run_count}/{total_runs}] Running: {run_name}")
            print(f"{'='*60}")

            # Setup parameters
            parameters = {
                "k_groups": k_groups,
                "population_size": POPULATION_SIZE,
                "generations": GENERATIONS,
                "crossover_rate": CROSSOVER_RATE,
                "mutation_rate": MUTATION_RATE,
                "elitism_count": ELITISM_COUNT,
                "alpha": ALPHA,
                "beta": BETA,
                "gamma": gamma,
                "offset": OFFSET,
                "cluster_balance_penalty": CLUSTER_BALANCE_PENALTY,
                "min_group_size": min_group_size
            }

            # Setup run directory
            run_dir = run_manager.setup_run(run_name, parameters)

            # Create evaluator and EA
            evaluator = FitnessEvaluator(
                genetic_matrix=genetic,
                geographic_matrix=geographic,
                k_groups=k_groups,
                alpha=ALPHA,
                beta=BETA,
                gamma=gamma,
                offset=OFFSET,
                cluster_balance_penalty=CLUSTER_BALANCE_PENALTY,
                min_group_size=min_group_size
            )

            ea = EvolutionaryAlgorithm(
                num_subjects=num_subjects,
                k_groups=k_groups,
                population_size=POPULATION_SIZE,
                generations=GENERATIONS,
                crossover_rate=CROSSOVER_RATE,
                mutation_rate=MUTATION_RATE,
                elitism_count=ELITISM_COUNT,
                evaluator=evaluator
            )

            # Save fitness formula to metadata
            run_manager.metadata["fitness_function"] = evaluator.get_fitness_formula()
            run_manager._save_metadata()

            # Run EA
            best = ea.run()
            counts = Counter(best.chromosome)
            print(f"\nBest fitness: {best.fitness:.4f}")
            print(f"Cluster sizes: {dict(sorted(counts.items()))}")

            # Create plot data
            print("\nPlot data:")
            lineage = ea.get_lineage(best)
            lineage = ea.sample_lineage(lineage, num_samples=300)
            create_plot_data(run_dir, genetic, ea.history, lineage, subject_names)

            # Create visualizations (normal output)
            Visualizations(
                subject_names=subject_names,
                chromosome=best.chromosome,
                k_groups=k_groups,
                genetic_matrix=genetic,
                geographic_matrix=geographic,
                fitness_history=ea.history,
                output_dir=run_dir
            ).plot_all()

            # Progress update
            if run_count < total_runs:
                elapsed = time.time() - loop_start
                avg_per_run = elapsed / run_count
                remaining_runs = total_runs - run_count
                eta_seconds = remaining_runs * avg_per_run
                print(f"\nProgress: {run_count}/{total_runs} | Elapsed: {elapsed/60:.1f}m | ETA: {eta_seconds/60:.1f}m")

    # Summary
    total_time = (time.time() - loop_start) / 60
    print(f"\n{'='*60}")
    print(f"PARAMETER SWEEP COMPLETE")
    print(f"Total time: {total_time:.1f}m")
    print(f"Results saved to results/runs/")
    print(f"{'='*60}\n")
