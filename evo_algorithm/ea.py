import random
from individual import Individual
from population import Population


class EvolutionaryAlgorithm:
    def __init__(self,num_subjects,k_groups,population_size,generations,crossover_rate,mutation_rate,elitism_count,evaluator):
        self.num_subjects = num_subjects
        self.k_groups = k_groups
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.evaluator = evaluator
        self.population = Population(population_size, num_subjects, k_groups)
        self.history = {
            "generation": [],
            "best_fitness": [],
            "mean_fitness": [],
            "worst_fitness": [],
        }

    def _record_fitness(self, generation):
        fits = [m.fitness for m in self.population.members]
        self.history["generation"].append(generation)
        self.history["best_fitness"].append(max(fits))
        self.history["mean_fitness"].append(sum(fits) / len(fits))
        self.history["worst_fitness"].append(min(fits))

    def run(self):
        for member in self.population.members:
            self.evaluator.evaluate(member)

        self.population.sort_by_fitness()
        self._record_fitness(0)
        print(f"Generation 0: best fitness = {self.population.best().fitness:.4f}")

        for gen in range(self.generations):
            next_pop = []
            next_pop.extend(self.population.members[: self.elitism_count])

            while len(next_pop) < self.population_size:
                parent1 = self.population.roulette_select()
                parent2 = self.population.roulette_select()

                if random.random() < self.crossover_rate:
                    c1, c2 = self._crossover(parent1, parent2)
                else:
                    c1 = parent1.chromosome.copy()
                    c2 = parent2.chromosome.copy()

                child1 = Individual(self.num_subjects, self.k_groups, c1)
                child2 = Individual(self.num_subjects, self.k_groups, c2)
                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)
                self.evaluator.evaluate(child1)
                self.evaluator.evaluate(child2)

                next_pop.append(child1)
                if len(next_pop) < self.population_size:
                    next_pop.append(child2)

            self.population.members = next_pop
            self.population.sort_by_fitness()
            self._record_fitness(gen + 1)
            print(f"Generation {gen + 1}: best fitness = {self.population.best().fitness:.4f}")

        return self.population.best()

    def _crossover(self, parent1, parent2):
        n = self.num_subjects
        if n <= 1:
            return parent1.chromosome.copy(), parent2.chromosome.copy()
        point = random.randint(1, n - 1)
        c1 = parent1.chromosome[:point] + parent2.chromosome[point:]
        c2 = parent2.chromosome[:point] + parent1.chromosome[point:]
        return c1, c2
