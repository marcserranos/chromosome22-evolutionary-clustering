"""
Multi-run experiment: execute EA multiple times and perform consistency analysis.
"""

from pathlib import Path
import json
import time
import numpy as np
from collections import Counter

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    tqdm = lambda x, **kwargs: x  # Fallback: tqdm becomes identity function

from data_loader import load_distances, load_subject_metadata, align_metadata
from fitness import FitnessEvaluator
from ea import EvolutionaryAlgorithm
from run_manager import RunManager
from consistency_analyzer import ConsistencyAnalyzer
from consistency_visualizations import ConsistencyVisualizations


def run_single_ea(run_name, parameters, genetic_matrix, geographic_matrix, subject_names, run_manager):
    """
    Run a single evolutionary algorithm and return best individual.

    Args:
        run_name: name for this run
        parameters: dict with EA parameters
        genetic_matrix: genetic distance matrix
        geographic_matrix: geographic distance matrix
        subject_names: list of subject identifiers
        metadata_df: metadata dataframe
        run_manager: RunManager instance

    Returns:
        best_individual: the best individual found
        run_dir: where the run results were saved
    """
    # Setup run directory
    run_dir = run_manager.setup_run(run_name, parameters)

    num_subjects = len(subject_names)

    # Initialize evaluator and EA
    evaluator = FitnessEvaluator(
        genetic_matrix=genetic_matrix,
        geographic_matrix=geographic_matrix,
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

    # Run EA
    print(f"\n{'='*60}")
    print(f"Running: {run_name}")
    print(f"{'='*60}")
    best = ea.run()

    # Summary
    counts = Counter(best.chromosome)
    print(f"\nBest fitness: {best.fitness:.4f}")
    print(f"Cluster sizes: {dict(sorted(counts.items()))}")

    return best, run_dir, ea


def run_multi_experiment(num_runs, base_name="consistency_test", parameters=None):
    """
    Run EA multiple times with different random seeds.

    Args:
        num_runs: number of times to run the EA
        base_name: base name for run directories
        parameters: dict with EA parameters (see main.py for example)

    Returns:
        results: list of dicts, each with:
            - best_individual: the best individual found
            - run_dir: where results were saved
            - run_name: name of this run
        genetic_matrix: loaded genetic distances
        geographic_matrix: loaded geographic distances
        subject_names: list of subject names
        metadata_df: metadata dataframe
    """

    # Load data once (same for all runs)
    print("\nLoading data...")
    genetic, geographic, subject_names = load_distances()
    metadata_df = load_subject_metadata()
    metadata_df = align_metadata(subject_names, metadata_df)

    num_subjects = len(subject_names)

    # Default parameters if not provided
    if parameters is None:
        k_groups = 5
        min_group_size = max(1, num_subjects // (k_groups * 10))
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

    run_manager = RunManager()

    # Run EA multiple times with progress tracking
    results = []
    iterator = tqdm(range(num_runs), desc="Running EA", disable=not HAS_TQDM) if HAS_TQDM else range(num_runs)

    loop_start = time.time()
    for i in iterator:
        run_name = f"{base_name}_run_{i:02d}"
        best, run_dir, ea = run_single_ea(run_name, parameters, genetic, geographic, subject_names, run_manager)

        results.append({
            'run_name': run_name,
            'best_individual': best,
            'run_dir': run_dir,
            'ea': ea
        })

        if not HAS_TQDM and i < num_runs - 1:
            elapsed = time.time() - loop_start
            avg_per_run = elapsed / (i + 1)
            remaining_runs = num_runs - (i + 1)
            eta_seconds = remaining_runs * avg_per_run
            print(f"  Progress: {i+1}/{num_runs} | Elapsed: {elapsed/60:.1f}m | ETA: {eta_seconds/60:.1f}m")

    return results, genetic, geographic, subject_names, metadata_df, parameters


def analyze_multi_run_results(results, genetic_matrix, geographic_matrix, subject_names, metadata_df, output_dir=None):
    """
    Perform consistency analysis on multi-run results.

    Performs:
    1. Canonical labeling (relabel all runs to match first run)
    2. Subject stability computation
    3. ARI consistency metrics
    4. Visualizations

    Args:
        results: list of result dicts from run_multi_experiment
        genetic_matrix: genetic distance matrix
        geographic_matrix: geographic distance matrix
        subject_names: list of subject names
        metadata_df: metadata dataframe
        output_dir: where to save results

    Returns:
        analysis_dict: dict with all analysis results
    """

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "results" / "consistency"
    output_dir = Path(output_dir)

    print(f"\n{'='*60}")
    print("CONSISTENCY ANALYSIS")
    print(f"{'='*60}\n")

    # Extract chromosomes
    chromosomes = [result['best_individual'].chromosome for result in results]
    num_runs = len(chromosomes)
    k_groups = len(set(chromosomes[0]))

    print(f"Analyzing {num_runs} runs with {k_groups} clusters and {len(subject_names)} subjects\n")

    # 1. Canonical labeling
    print("1. Canonical labeling (relabeling all runs to match first run)...")
    print("   Reference chromosome = best solution from Run 0 (used to relabel all other runs)")
    canonicalized, permutations, _ = ConsistencyAnalyzer.canonicalize_all_partitions(chromosomes)
    print("   ✓ Canonicalization complete\n")

    # 2. Subject stability
    print("2. Computing subject stability...")
    stability_scores, cluster_assignments = ConsistencyAnalyzer.compute_subject_stability(canonicalized)
    stability_summary = ConsistencyAnalyzer.compute_stability_summary(stability_scores)
    print("   ✓ Stability computation complete\n")

    # Print summary
    print("STABILITY SUMMARY:")
    print(f"  Mean consistency: {stability_summary['mean_consistency']:.4f}")
    print(f"  Std consistency: {stability_summary['std_consistency']:.4f}")
    print(f"  Stable subjects (1.0): {stability_summary['num_stable_subjects']}")
    print(f"  Variable subjects (< 1.0): {stability_summary['num_variable_subjects']}")
    print(f"  Frontier subjects (< 0.5): {stability_summary['num_frontier_subjects']}\n")

    # 3. ARI matrix
    print("3. Computing pairwise Adjusted Rand Index...")
    ari_matrix = ConsistencyAnalyzer.compute_ari_matrix(canonicalized)
    mean_ari = np.mean(ari_matrix[np.triu_indices_from(ari_matrix, k=1)])
    print(f"   Mean off-diagonal ARI: {mean_ari:.4f}\n")

    # 4. Visualizations
    print("4. Creating visualizations...")
    viz = ConsistencyVisualizations(
        subject_names=subject_names,
        k_groups=k_groups,
        stability_scores=stability_scores,
        cluster_assignments=cluster_assignments,
        ari_matrix=ari_matrix,
        metadata_df=metadata_df,
        output_dir=output_dir
    )
    viz.plot_all()

    # 5. Save analysis results
    print("\n5. Saving analysis results...")
    analysis_dict = {
        'num_runs': num_runs,
        'k_groups': k_groups,
        'num_subjects': len(subject_names),
        'stability_summary': stability_summary,
        'mean_ari': float(mean_ari),
        'ari_matrix': ari_matrix.tolist(),
        'permutations': [{str(int(k)): int(v) for k, v in perm.items()} for perm in permutations],
        'stability_scores': {str(k): v for k, v in stability_scores.items()},
        'cluster_assignments': {str(k): [int(x) for x in v] for k, v in cluster_assignments.items()}
    }

    results_path = output_dir / "consistency_analysis_results.json"
    with open(results_path, 'w') as f:
        json.dump(analysis_dict, f, indent=2)

    print(f"   Saved to: {results_path}\n")

    # Save detailed subject stability report
    stability_report_path = output_dir / "subject_stability_report.txt"
    with open(stability_report_path, 'w') as f:
        f.write("SUBJECT STABILITY REPORT\n")
        f.write("="*80 + "\n\n")

        # Sort by consistency
        sorted_subjects = sorted(
            stability_scores.items(),
            key=lambda x: x[1]['consistency_fraction'],
            reverse=True
        )

        for subject_idx, scores in sorted_subjects:
            f.write(f"Subject {subject_idx}: {subject_names[subject_idx]}\n")
            f.write(f"  Consistency: {scores['consistency_fraction']:.4f} ({int(scores['consistency_fraction']*num_runs)}/{num_runs})\n")
            f.write(f"  Primary cluster: {scores['consistent_cluster']}\n")
            f.write(f"  Unique clusters: {scores['num_unique_clusters']}\n")
            f.write(f"  Assignments: {cluster_assignments[subject_idx]}\n\n")

    print(f"   Saved to: {stability_report_path}\n")

    return analysis_dict


if __name__ == "__main__":
    # Example usage: run 5 experiments with custom parameters
    num_runs = 5
    custom_params = {
        "k_groups": 5,
        "population_size": 50,
        "generations": 6000,
        "crossover_rate": 0.9,
        "mutation_rate": 0.005,
        "elitism_count": 2,
        "alpha": 1.0,
        "beta": 1.0,
        "gamma": 1.0,
        "offset": 1.0,
        "cluster_balance_penalty": 0.0001,
        "min_group_size": None  # Will be calculated
    }

    # Run experiments
    results, genetic, geographic, subject_names, metadata_df, params = run_multi_experiment(
        num_runs=num_runs,
        base_name="consistency_test",
        parameters=custom_params
    )

    # Analyze results
    analysis = analyze_multi_run_results(
        results=results,
        genetic_matrix=genetic,
        geographic_matrix=geographic,
        subject_names=subject_names,
        metadata_df=metadata_df
    )

    print("="*60)
    print("CONSISTENCY ANALYSIS COMPLETE")
    print("="*60)
