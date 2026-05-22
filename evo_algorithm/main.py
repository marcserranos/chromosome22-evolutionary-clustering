from collections import Counter
from data_loader import load_distances
from fitness import FitnessEvaluator
from ea import EvolutionaryAlgorithm
from visualizations import Visualizations

def main():
    '''runs experiments as desired, rifht now it's short in options, will be further
    improved for modularity and experiment variability'''

    genetic, geographic, subject_names = load_distances() # loads data
    num_subjects = len(subject_names)
    k_groups = 4 # define K number (main parameter)
    min_group_size = max(1, num_subjects // (k_groups * 10)) # can be changed

    # class initialization
    evaluator = FitnessEvaluator(genetic_matrix=genetic,geographic_matrix=geographic,k_groups=k_groups,alpha=0,beta=0,min_group_size=min_group_size,gamma=100.0)
    ea = EvolutionaryAlgorithm(num_subjects=num_subjects,k_groups=k_groups,population_size=50,generations=10000,crossover_rate=0.9,mutation_rate=0.05,elitism_count=2,evaluator=evaluator)

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

    # creates plots
    Visualizations(subject_names=subject_names,chromosome=best.chromosome,k_groups=k_groups,genetic_matrix=genetic,geographic_matrix=geographic,fitness_history=ea.history).plot_all()

if __name__ == "__main__":
    main()
