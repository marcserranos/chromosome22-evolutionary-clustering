import random
from individual import Individual
from population import Population


class EvolutionaryAlgorithm:
    '''runs the evolutionary algorithm for a set number of generations and set of given parameters
    
    pd: will be improved to be more modular, with convergence goals and steadiness control
    instead of fixed generations number'''

    def __init__(self,num_subjects,k_groups,population_size,generations,crossover_rate,mutation_rate,elitism_count,evaluator):
        self.num_subjects = num_subjects # number of subjects in data
        self.k_groups = k_groups
        self.population_size = population_size # number of individuals per generation
        self.generations = generations # fixed gen number
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count # number of auto-saved individuals
        self.evaluator = evaluator # from class FitnessEvaluator
        self.population = Population(population_size, num_subjects, k_groups)
        # lists for data preservation and later visualization
        self.history = {"generation":[],"best_fitness":[],"mean_fitness":[],"worst_fitness":[]}
        # lineage tracking
        self.id_counter = 0
        self.individual_store = {}

    def _record_fitness(self, generation):
        '''saves historic data on fitness in every generation'''
        fits = [m.fitness for m in self.population.members] # iterates through individuals
        self.history["generation"].append(generation)
        self.history["best_fitness"].append(max(fits))
        self.history["mean_fitness"].append(sum(fits) / len(fits))
        self.history["worst_fitness"].append(min(fits))

    def run(self):
        '''runs the ea.'''

        # STARTING CASE
        # evaluates fitness for every individual
        for member in self.population.members:
            self.id_counter += 1
            member.id = self.id_counter
            member.parent_id = None
            self.individual_store[member.id] = member
            self.evaluator.evaluate(member)

        # saves history and prints for following
        self.population.sort_by_fitness() # sorts population by descending fitness
        self._record_fitness(0)
        print(f"Generation 0: best fitness = {self.population.best().fitness:.4f}") 

        # ITERATIVE GENERATIONS CASE
        for gen in range(self.generations):
            next_pop = []

            # ELITISM: auto-saves as many indivduals as required in input
            next_pop.extend(self.population.members[: self.elitism_count]) 

            # SELECTION: selects two parents via weighted roulette
            while len(next_pop) < self.population_size:
                parent1 = self.population.roulette_select()
                parent2 = self.population.roulette_select()

            # CROSSOVER: with self-adaptive crossover rate from parent, selected parents have children
                # Use parent1's crossover rate for child1, parent2's for child2
                if random.random() < parent1.crossover_rate:
                    c1, c2 = self.crossover(parent1, parent2)
                else:
                    c1 = parent1.chromosome.copy()
                    c2 = parent2.chromosome.copy()

                self.id_counter += 1
                child1 = Individual(self.num_subjects, self.k_groups, c1, parent1.mutation_rate, parent1.crossover_rate, id=self.id_counter, parent_id=parent1.id)
                self.individual_store[child1.id] = child1

                self.id_counter += 1
                child2 = Individual(self.num_subjects, self.k_groups, c2, parent2.mutation_rate, parent2.crossover_rate, id=self.id_counter, parent_id=parent2.id)
                self.individual_store[child2.id] = child2

            # MUTATION & ADAPTATION: children mutate chromosome and adapt rates
                child1.mutate(adaptive=True)
                child2.mutate(adaptive=True)
                self.evaluator.evaluate(child1) # new fitness evaluation
                self.evaluator.evaluate(child2)

                next_pop.append(child1) # adds child to next gen
                if len(next_pop) < self.population_size: # handles edge case and adds child2
                    next_pop.append(child2)

            # saves history and prints for following
            self.population.members = next_pop
            self.population.sort_by_fitness()
            self._record_fitness(gen + 1)
            if gen%100==0:
                print(f"Generation {gen}: best fitness = {self.population.best().fitness:.4f}")

        return self.population.best()

    def get_lineage(self, individual):
        """Walk backwards from individual to root, returning list [root, ..., individual]"""
        lineage = []
        current = individual
        while current is not None:
            lineage.append(current)
            if current.parent_id is None:
                break
            current = self.individual_store.get(current.parent_id)
        return lineage[::-1]

    def sample_lineage(self, lineage, num_samples=300):
        """Sample lineage evenly to get approximately num_samples points"""
        if len(lineage) <= num_samples:
            return lineage
        step = len(lineage) / num_samples
        sampled = [lineage[int(i * step)] for i in range(num_samples)]
        sampled[-1] = lineage[-1]  # ensure we always include the final individual
        return sampled

    def crossover(self, parent1, parent2):
        '''generates chromosomes for children from two parents by choosing a random cutoff point
        throughout the parents' chromosomes. child1 gets "dad's first half, mom's second", and 
        viceversa'''
        n = self.num_subjects
        if n <= 1:
            return parent1.chromosome.copy(), parent2.chromosome.copy()
        point = random.randint(1, n - 1) # cuts chromosome in random point
        c1 = parent1.chromosome[:point] + parent2.chromosome[point:]
        c2 = parent2.chromosome[:point] + parent1.chromosome[point:]
        return c1, c2