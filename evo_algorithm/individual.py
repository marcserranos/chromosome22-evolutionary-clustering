import random

class Individual:
    """
    this class represents one possible partition of all subjects into K groups
    """
    def __init__(self, num_subjects: int, k_groups: int, chromosome = None):
        self.num_subjects = num_subjects 
        self.k_groups = k_groups

        # makes it possible to test specific starting arrangements
        if chromosome is None:
            self.chromosome = self.initialize_randomly()
        else:
            self.chromosome = list(chromosome)

        self.fitness = None # starts uninitialized

    def initialize_randomly(self):
        '''gives a totally random arrangement for all subjects in K groups (chromosome)'''
        return [random.randrange(self.k_groups) for _ in range(self.num_subjects)]

    def mutate(self, mutation_rate: float):
        '''mutates chromosome for a mutation rate chance in every position, where a mutation
        means that a subject is changed to a different random cluster'''
        # block below handles elegantly the random assignment
        for i in range(self.num_subjects):
            if random.random() >= mutation_rate:
                continue
            current = self.chromosome[i]
            new_group = random.randrange(self.k_groups - 1) # grabs a random cluster 
            if new_group >= current:
                new_group += 1 # handles k_groups - 1 logic to correctly assign
            self.chromosome[i] = new_group

    def copy(self):
        '''deep copies the individual for various potential purposes'''
        other = Individual(self.num_subjects, self.k_groups, self.chromosome)
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
