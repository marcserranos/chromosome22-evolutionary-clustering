import random
from handovers.evo_algorithm_handover.individual import Individual
from handovers.evo_algorithm_handover.population import Population


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

            # CROSSOVER: with a defined chance, selected parents have children 
                if random.random() < self.crossover_rate:
                    c1, c2 = self.crossover(parent1, parent2)
                else:
                    c1 = parent1.chromosome.copy() # if no crossover, children are deep copies of paretns
                    c2 = parent2.chromosome.copy()
                child1 = Individual(self.num_subjects, self.k_groups, c1) # actual generation of object Individual
                child2 = Individual(self.num_subjects, self.k_groups, c2)

            # MUTATION: children mutate with a fixed probability 
                child1.mutate(self.mutation_rate) 
                child2.mutate(self.mutation_rate)
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