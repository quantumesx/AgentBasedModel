"""Run an evolutionary experiment."""

from Controller import MN_controller
from Trial import trial

from tqdm import tqdm
import random as rd
import pickle


class experiment():
    """
    Run an experiment.

    Overview of function order:
    Run()
    -> run the entire experiment and record data
    - Run_gen()
        -> run experiment for one generation and record data
        - get_gen_fitness()
            -> return [[genome, fitness], [genome, fitness], ...]
            - get_genotype_fitness()
                -> return fitness of one genotype
            - get_all_fitness()
                -> return fitness of all genotypes in the population
        - select_top()
            -> return top n best genotype
        - get_new_generation()
            -> return new generation based on top genotypes
            - mutate_genome()
                -> return a mutated genotype
                - mutate_loc()
                    -> mutate a single location

    """

    def __init__(self,
                 pop=100,
                 gen=100,
                 genome_size=83,
                 iteration=1000,
                 time=0.1,
                 preset='M&N, 2003',
                 env_height=270, env_width=270, targets=True,
                 trial=20,
                 include_top=20,
                 new_run=True
                 ):
        """Initialize the experiment."""
        self.pop = pop  # population size
        self.gen = gen  # total # of generations to run
        self.trial = trial  # trial to run for each group in the population
        self.include_top = include_top

        self.genome_size = genome_size
        self.genome = []  # [[g1p1, g1p2, ...], [g2p1, g2p2, ...], ...]
        self.fitness = []  # [[g1p1, g1p2, ...], [g2p1, g2p2, ...], ...]
        self.top = []

        if new_run:
            self.generate_first_gen()

    def generate_first_gen(self):
        """Generate genome for the first generation."""
        def generate_random_genome(genome_size):
            genome = rd.choices(range(0, 255), k=genome_size)
            return genome

        first_gen = [generate_random_genome(self.genome_size)
                     for p in range(self.pop)]

        self.genome.append(first_gen)

    def run(self):
        """Run experiment."""
        # iterate through each generation
        [self.run_gen(gen) for gen in range(self.gen)]
        pickle.dump(self, open('experiment.exp', 'wb'))

    def run_gen(self, gen):
        """Run one generation."""
        # Get fitness for all genotypes in this generation
        gen_fitness = self.get_gen_fitness(self.genome[-1], gen)

        # select 20 best performing teams
        top_genome = self.select_top(gen_fitness)

        # Generate new generation
        new_gen = self.get_new_generation(top_genome)

        # update info
        self.top.append(top_genome)
        self.fitness.append(gen_fitness)
        self.genome.append(new_gen)

    def get_gen_fitness(self, gen_genome, gen):
        """
        Run all trials for a generation.

        input:
        - gen_genome: a list of genome for every genotype in this generation
        - g: number indicating current generation #

        output:
        - gen_fitness: a list of the fitness for every corresponding population
        """
        def get_genotype_fitness(ann, g, p, t):
            """Get the fitness of a genotype through behavioral trials."""
            t = trial(ann, name='g{}p{}t{}'.format(g, p, t))
            t.run(record=False, save=False)
            return t.fitness

        def get_all_fitness(genome, g, p):
            """Get the fitness of an entire generation."""
            ann = MN_controller(genome)

            # fitness of the trials
            total_fit = [get_genotype_fitness(ann, g, p, i)
                         for i in range(self.trial)]

            # iterate through each trial; default = 20
            fitness = sum(total_fit) / self.trial

            # update both the genome and the fitness to gen_fitness
            return genome, fitness

        # Just to make sure
        if len(gen_genome) != self.pop:
            print('Error: number of genome not equal to number of population.')

        gen_fitness = [get_all_fitness(gen_genome[p], gen, p)
                       for p in tqdm(range(self.pop))]

        return gen_fitness

    def select_top(self, gen_fitness):
        """
        Select the top n (default=20) genome from a population.

        input:
        - gen_fitness: [[[genome1], fitness of genome1], [[genome2], fitness of
            genome2], ...]

        output:
        - top_genome: [[best genome1], [best genome2], ..., [best genome n]]
        """
        def get_key(item):
            return item[1]

        top_genome = [g[0] for g in sorted(gen_fitness, key=get_key,
                                           reverse=True)[:self.include_top]]

        return top_genome

    def get_new_generation(self, top_genome, mutation_rate=0.02):
        """
        Get population for the new generation.

        input:
        - top_genome: n top genome from the last generation
        - mutation_rate: rate of mutation, default = 0.02

        output:
        - next_gen: list of new genome for the next generation.
                    (length = self.pop)
        """
        def mutate_loc(l, mutation_rate):
            """
            Mutate a location in a genome.

            First, randomly generate a number between 0-1.
            If the number is smaller than mutation rate, return a new integer
            between 0 - 255.
            Otherwise, return the original integer it received.
            """
            r = rd.uniform(0, 1)
            if r < mutation_rate:
                return rd.choice(range(0, 255))
            else:
                return l

        def mutate_genome(g, mutation_rate):
            """Mutate a population's genome."""
            return [mutate_loc(l, mutation_rate) for l in g]

        rep = self.pop / len(top_genome)
        if rep != int(rep):
            print('Warning: expected number of replica is not an integer.')

        # for every genotype:
        # outcomes should be g1, g1, g1, ... g2, g2, ....
        next_gen = [mutate_genome(g, mutation_rate)
                    for g in top_genome
                    for r in range(int(rep))]
        return next_gen
