import numpy as np
from individual import Individual


class FitnessEvaluator:
    """
    Scores an Individual (candidate partition) using NxN distance matrices.
    Matrix rows/columns index subjects (one person per index).

    fitness = alpha * separation - beta * variance - geographic_cost
    """

    PENALTY = -100000000

    def __init__(self,genetic_matrix,geographic_matrix,k_groups,alpha=1.0,beta=1.0,min_group_size=1,gamma=1.0):
        self.genetic_matrix = genetic_matrix
        self.geographic_matrix = geographic_matrix
        self.k_groups = k_groups
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.min_group_size = min_group_size
        self.num_subjects = genetic_matrix.shape[0]
        i, j = np.triu_indices(self.num_subjects, k=1)
        self.pair_i = i
        self.pair_j = j
        self.genetic_pairs = genetic_matrix[i, j]
        self.geographic_pairs = geographic_matrix[i, j]

    def evaluate(self, individual:Individual):
        chr = np.asarray(individual.chromosome, dtype=int)

        if not self.validate_constraints(chr):
            individual.fitness = self.PENALTY
            return individual.fitness

        same = chr[self.pair_i] == chr[self.pair_j]
        # mirarsho amb carinyo
        if np.any(~same):
            separation = float(self.genetic_pairs[~same].mean())
        else:
            separation = 0.0
        # mirarsho amb carinyo
        if np.any(same):
            variance = float(self.genetic_pairs[same].mean())
            geo_cost = float(self.geographic_pairs[same].mean())
        else:
            variance = 0.0
            geo_cost = 0.0

        individual.fitness = (
            self.alpha * separation - self.beta * variance - self.gamma * geo_cost
        )
        return individual.fitness

    def validate_constraints(self, chr):
        counts = np.bincount(chr, minlength=self.k_groups)
        return bool(np.all(counts >= self.min_group_size))
