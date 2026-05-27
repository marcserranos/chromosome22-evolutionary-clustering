#!/usr/bin/env python
"""
Multi-run consistency analysis.
Set parameters below, then run: python run_consistency.py
"""

import time
from multi_run import run_multi_experiment, analyze_multi_run_results

# ============================================================================
# PARAMETERS (edit these)
# ============================================================================

NUM_RUNS = 20  # Number of EA runs (5, 50, 100, ...)

# EA parameters
K_GROUPS = 5
POPULATION_SIZE = 50
GENERATIONS = 6000
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.005
ELITISM_COUNT = 2

# Fitness weights
ALPHA = 1.0
BETA = 1.0
GAMMA = 1.0
OFFSET = 1.0

# Cluster balance penalty (tune this to see impact)
CLUSTER_BALANCE_PENALTY = 0.0001

MIN_GROUP_SIZE = None  # None = auto-calculate

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    start = time.time()

    params = {
        "k_groups": K_GROUPS,
        "population_size": POPULATION_SIZE,
        "generations": GENERATIONS,
        "crossover_rate": CROSSOVER_RATE,
        "mutation_rate": MUTATION_RATE,
        "elitism_count": ELITISM_COUNT,
        "alpha": ALPHA,
        "beta": BETA,
        "gamma": GAMMA,
        "offset": OFFSET,
        "cluster_balance_penalty": CLUSTER_BALANCE_PENALTY,
        "min_group_size": MIN_GROUP_SIZE
    }

    print(f"\n{'='*60}")
    print(f"Running {NUM_RUNS} EA iterations")
    print(f"K={K_GROUPS}, penalty={CLUSTER_BALANCE_PENALTY}")
    print(f"{'='*60}\n")

    results, genetic, geographic, subject_names, metadata_df, _ = run_multi_experiment(
        num_runs=NUM_RUNS,
        base_name="consistency_test",
        parameters=params
    )

    analysis = analyze_multi_run_results(
        results=results,
        genetic_matrix=genetic,
        geographic_matrix=geographic,
        subject_names=subject_names,
        metadata_df=metadata_df
    )

    summary = analysis['stability_summary']
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Mean consistency: {summary['mean_consistency']:.4f}")
    print(f"Mean ARI: {analysis['mean_ari']:.4f}")
    print(f"Stable subjects: {summary['num_stable_subjects']}")
    print(f"Frontier subjects: {summary['num_frontier_subjects']}")
    print(f"Time: {(time.time()-start)/60:.1f} min")
    print(f"Results saved to results/consistency/\n")
