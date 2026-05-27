import numpy as np
from individual import Individual


class FitnessEvaluator:
    """
    scores an Individual (candidate partition) using input distance matrices
    matrix rows/columns index subjects (one subject per index).
    """

    # Single source of truth for fitness formula
    FITNESS_FORMULA = "fitness = offset + alpha * separation - beta * variance + gamma * geographic_distance - lambda * sum(max(0, |size - mean| - threshold)^2)"

    PENALTY = -100000000 # massive penalty given to erase invalid individals with ease

    def __init__(self,genetic_matrix,geographic_matrix,k_groups,alpha=1.0,beta=1.0,min_group_size=1,gamma=1.0,offset=1.0,cluster_balance_penalty=0.0):
        self.genetic_matrix = genetic_matrix # input matrix of genetic distances
        self.geographic_matrix = geographic_matrix # input matrix of geographic distances
        self.k_groups = k_groups
        self.alpha = alpha # weight for genetic separation, initialized at 1
        self.beta = beta # weight for genetic variance, initialized at 1
        self.gamma = gamma # weight for geographic cost, initialized at 1
        self.offset = offset # bias to shift fitness to positive range, initialized at 1.0
        self.cluster_balance_penalty = cluster_balance_penalty # penalty coefficient for uneven cluster sizes
        self.num_subjects = genetic_matrix.shape[0]
        if min_group_size is None:
            self.min_group_size = max(1, self.num_subjects // (k_groups * 10))
        else:
            self.min_group_size = min_group_size # minim size of cluster

        # numpy matrix index handling
        i, j = np.triu_indices(self.num_subjects, k=1) 
        self.pair_i = i 
        self.pair_j = j
        self.genetic_pairs = genetic_matrix[i, j]
        self.geographic_pairs = geographic_matrix[i, j]

    def evaluate(self, individual:Individual):
        '''evaluates the finess on an individual and assigns it to it'''
        chr = np.asarray(individual.chromosome)

        if not self.validate_constraints(chr): # checks for constraints
            individual.fitness = self.PENALTY
            return individual.fitness

        same = chr[self.pair_i] == chr[self.pair_j]
        if np.any(~same):
            separation = float(self.genetic_pairs[~same].mean())
        else:
            separation = 0.0
        if np.any(same):
            variance = float(self.genetic_pairs[same].mean())
        else:
            variance = 0.0

        # compute cluster balance penalty (only for extreme deviations)
        counts = np.bincount(chr, minlength=self.k_groups)
        mean_size = self.num_subjects / self.k_groups
        threshold_low = 0.5 * mean_size
        threshold_high = 2.0 * mean_size

        balance_penalty = 0.0
        for size in counts:
            if size < threshold_low:
                balance_penalty += (threshold_low - size) ** 2
            elif size > threshold_high:
                balance_penalty += (size - threshold_high) ** 2

        # fitness score computation (see FITNESS_FORMULA for ground truth)
        individual.fitness = self.offset + (self.alpha * separation - self.beta * variance + self.gamma * self.geographic_pairs.mean() - self.cluster_balance_penalty * balance_penalty)

        return individual.fitness

    def validate_constraints(self, chr):
        '''checks whether group sizes are inside permitted thresholds'''
        counts = np.bincount(chr, minlength=self.k_groups) # counts cluster sizes
        return bool(np.all(counts >= self.min_group_size)) # checks whether all clusters are big enough

    def get_fitness_formula(self):
        '''returns the fitness formula being used (single source of truth from FITNESS_FORMULA)'''
        return self.FITNESS_FORMULA
