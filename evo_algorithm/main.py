from collections import Counter
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


def main():
    '''runs experiments as desired, rifht now it's short in options, will be further
    improved for modularity and experiment variability'''

    # Get run name and setup directory
    run_name = get_run_name()
    run_manager = RunManager()

    genetic, geographic, subject_names = load_distances() # loads data
    num_subjects = len(subject_names)
    k_groups = 7 # define K number (main parameter)
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
