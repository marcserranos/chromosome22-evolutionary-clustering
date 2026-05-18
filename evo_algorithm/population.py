import random
from individual import Individual


class Population:
    """A set of candidate partitions (Individuals) evolved in one experiment."""

    def __init__(self, size, num_subjects, k_groups):
        self.members = [Individual(num_subjects, k_groups) for _ in range(size)]

    def sort_by_fitness(self):
        self.members.sort(key=lambda x: x.fitness, reverse=True)

    def best(self):
        return self.members[0]

    def roulette_select(self):
        fitnesses = [m.fitness for m in self.members]
        worst = min(fitnesses)
        weights = [f - worst + 1e-9 for f in fitnesses]
        total = sum(weights)
        pick = random.uniform(0, total)
        running = 0.0
        for member, w in zip(self.members, weights):
            running += w
            if running >= pick:
                return member
        return self.members[-1]

    def __len__(self):
        return len(self.members)
