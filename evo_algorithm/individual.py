import random
import numpy as np

class Individual:
    """
    this class represents one possible partition of all subjects into K groups
    """
    def __init__(self, num_subjects: int, k_groups: int, chromosome = None, mutation_rate = None, crossover_rate = None, id=None, parent_id=None):
        self.num_subjects = num_subjects
        self.k_groups = k_groups

        # makes it possible to test specific starting arrangements
        if chromosome is None:
            self.chromosome = self.initialize_randomly()
        else:
            self.chromosome = list(chromosome)

        # self-adaptive parameters
        self.mutation_rate = mutation_rate if mutation_rate is not None else 0.05
        self.crossover_rate = crossover_rate if crossover_rate is not None else 0.9

        # lineage tracking
        self.id = id
        self.parent_id = parent_id

        self.fitness = None # starts uninitialized

    def initialize_randomly(self):
        '''gives a totally random arrangement for all subjects in K groups (chromosome)'''
        return [random.randrange(self.k_groups) for _ in range(self.num_subjects)]

    def mutate(self, adaptive=True):
        '''mutates chromosome and self-adaptive rates (mutation_rate, crossover_rate).
        if adaptive=True, uses self-adaptive step-size; otherwise uses fixed rate'''

        # Self-adaptive parameter evolution
        if adaptive:
            tau = 1.0 / np.sqrt(2.0 * np.sqrt(1))  # simplified for 1D
            r_mut = np.random.normal(0, 1)
            r_cross = np.random.normal(0, 1)

            self.mutation_rate = self.mutation_rate * np.exp(tau * r_mut)
            self.mutation_rate = np.clip(self.mutation_rate, 0.001, 0.5)

            self.crossover_rate = self.crossover_rate * np.exp(tau * r_cross)
            self.crossover_rate = np.clip(self.crossover_rate, 0.1, 0.99)

        # Chromosome mutation using adapted mutation rate
        for i in range(self.num_subjects):
            if random.random() >= self.mutation_rate:
                continue
            current = self.chromosome[i]
            new_group = random.randrange(self.k_groups - 1) # grabs a random cluster
            if new_group >= current:
                new_group += 1 # handles k_groups - 1 logic to correctly assign
            self.chromosome[i] = new_group

    def copy(self):
        '''deep copies the individual for various potential purposes'''
        other = Individual(self.num_subjects, self.k_groups, self.chromosome, self.mutation_rate, self.crossover_rate)
        other.fitness = self.fitness
        return other

    def subjects_per_cluster(self):
        """for each cluster, list of subject indices assigned to it"""
        buckets = [[] for _ in range(self.k_groups)]
        for subject_idx, cluster in enumerate(self.chromosome):
            buckets[cluster].append(subject_idx)
        return buckets

    def __str__(self): # printing made easy
        return f"Individual(fitness={self.fitness})"
