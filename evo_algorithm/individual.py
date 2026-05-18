import random
from typing import List, Optional


class Individual:
    """
    One candidate partition: assigns each subject to a cluster 0 .. K-1.
    chromosome[i] is the cluster label for subject i.
    """

    def __init__(self, num_subjects: int, k_groups: int, chromosome: Optional[List[int]] = None):
        self.num_subjects = num_subjects
        self.k_groups = k_groups

        if chromosome is None:
            self.chromosome = self.initialize_randomly()
        else:
            self.chromosome = list(chromosome)
            if len(self.chromosome) != num_subjects:
                raise ValueError("chromosome length must equal num_subjects")

        self.fitness = None

    def initialize_randomly(self):
        return [random.randrange(self.k_groups) for _ in range(self.num_subjects)]

    def mutate(self, mutation_rate: float):
        if self.k_groups <= 1:
            return
        for i in range(self.num_subjects):
            if random.random() >= mutation_rate:
                continue
            current = self.chromosome[i]
            new_group = random.randrange(self.k_groups - 1)
            if new_group >= current:
                new_group += 1
            self.chromosome[i] = new_group

    def copy(self):
        other = Individual(self.num_subjects, self.k_groups, self.chromosome)
        other.fitness = self.fitness
        return other

    def subjects_per_cluster(self):
        """For each cluster, list of subject indices assigned to it."""
        buckets = [[] for _ in range(self.k_groups)]
        for subject_idx, cluster in enumerate(self.chromosome):
            buckets[cluster].append(subject_idx)
        return buckets

    def __str__(self):
        return f"Individual(fitness={self.fitness})"
