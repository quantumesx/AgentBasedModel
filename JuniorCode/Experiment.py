"""Run an evolutionary experiment."""

from Controller import MN_controller
from Trial import trial

# from tqdm import tqdm
import random as rd
import csv
# import pickle


class experiment():
    """
    Run an experiment.

    required inputs:
    - conditions:
        'comm': comm sensor readings are available
        'no comm': comm sensor readings are disabled for the network
    - comm_self_connected:
        'True': connections involving comm_self are untouched
        'False': connections involving comm_self are disabled
    - run_num: number of the current run (out of 10)
    - first_gen: the randomly generated first generation of the current
        experimental run
    - today: today's date (yyyy-mm-dd)
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
                 condition,
                 comm_self_connected,
                 run_num,
                 first_gen,
                 today,
                 pop=100,
                 gen=100,
                 include_top=20,
                 trial_num=20,
                 iteration=1000,
                 time=0.1,
                 env_height=270, env_width=270, targets=True,
                 ):
        """Initialize the experiment."""
        self.today = today
        self.condition = condition
        self.run_num = run_num

        self.pop = pop  # population size
        self.gen = gen  # total # of generations to run

        self.trial_num = trial_num  # trial to run for each team of robots
        self.include_top = include_top

        if comm_self_connected:
            self.csc_bool = True
            self.csc = 'cs_conn'
            self.genome_size = 69
        else:
            self.csc_bool = False
            self.csc = 'cs_disconn'
            self.genome_size = 65

        # header for data files
        self.header = make_header(self.genome_size, self.trial_num)

        self.genome = []  # updates every generation: [[p1, p2, ...]]
        self.fitness = []  # updates every generation: [[p1, p2, ...]]
        self.top = []

        # this controller is more just a placeholder
        if condition == 'comm':
            comm_disabled = False
        elif condition == 'no_comm':
            comm_disabled = True
        else:
            print('Error: Please enter valid condition.')

        # initialize trial object
        # this ann doesn't matter; a new network will be generated for each pop
        place_holder_ann = MN_controller(random=True)
        self.trial = trial(place_holder_ann, comm_disabled=comm_disabled)
        self.genome = first_gen

        # self.genome.append(random_first_gen(self.pop, self.genome_size))

    def run(self, begin=0):
        """Run experiment."""
        # iterate through each generation
        [self.run_gen(gen) for gen in range(begin, self.gen)]
        # pickle.dump(self, open('experiment.exp', 'wb'))

    def run_gen(self, gen):
        """Run one generation."""
        print('current generation: {} / {}'.format(gen+1, self.gen))
        # Get fitness for all genotypes in this generation
        self.get_gen_fitness(gen)

        # select 20 best performing teams
        self.select_top()

        # Generate new generation
        self.get_new_generation(gen)

    def get_gen_fitness(self, gen):
        """
        Run all trials for a generation.

        input:
        - gen_genome: a list of genome for every genotype in this generation
        - g: number indicating current generation #

        output:
        - gen_fitness: a list of the fitness for every corresponding population
        """
        def get_genotype_fitness():
            """Get the fitness of a genotype through behavioral trials."""
            self.trial.run(record=False, save=False)
            # print(len(self.trial.ann.nodes[15]['activation']),
            #      len(self.trial.env.agents[0].ann.nodes[15]['activation']),
            #      len(self.trial.env.agents[0].loc_data))
            # self.trial.fitness
            return self.trial.fitness

        def get_all_fitness(genome, g, p):
            """Get the fitness of an entire generation."""
            print('population: {} / {}'.format(p+1, self.pop))
            ann = MN_controller(genome, comm_self_connected=self.csc_bool)
            self.trial.new_ann(ann)
            # fitness of the trials
            total_fit = [get_genotype_fitness()
                         for i in range(self.trial_num)]

            # iterate through each trial; default = 20
            fitness = sum(total_fit) / self.trial_num

            # update both the genome and the fitness to gen_fitness
            return p, fitness, total_fit

        gen_genome = self.genome

        # Just to make sure
        if len(gen_genome) != self.pop:
            print('Error: number of genome not equal to number of population.')

        gen_fitness = [get_all_fitness(gen_genome[p], gen, p)
                       for p in range(self.pop)]

        filename = 'Data/{}_{}_{}_Run{}_Gen{}.dat'.format(self.today,
                                                          self.condition,
                                                          self.csc,
                                                          self.run_num,
                                                          gen)

        # pop, loci, total fitness, trial fitnesses
        flat_data = [
            [p] + gen_genome[p] + [gen_fitness[p][1]] + gen_fitness[p][2]
            for p in range(len(gen_fitness))
            ]

        with open(filename, 'w', newline='') as data_file:
            wr = csv.writer(data_file, quoting=csv.QUOTE_ALL)

            wr.writerow(self.header)
            for l in flat_data:
                wr.writerow(l)

        # update self.fitness
        self.fitness = gen_fitness

    def select_top(self):
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

        gen_fitness = self.fitness
        top_genome = [g[0] for g in sorted(gen_fitness, key=get_key,
                                           reverse=True)[:self.include_top]]
        # update self.top
        self.top = top_genome

    def get_new_generation(self, gen, mutation_rate=0.02):
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
                return rd.choice(range(0, 256))
            else:
                return l

        def mutate_genome(g, mutation_rate):
            """Mutate a population's genome."""
            return [mutate_loc(l, mutation_rate) for l in g]

        top_genome = self.top

        rep = self.pop / len(top_genome)
        if rep != int(rep):
            print('Warning: expected number of replica is not an integer.')

        # for every genotype:
        # outcomes should be g1, g1, g1, ... g2, g2, ....
        next_gen = [mutate_genome(self.genome[g], mutation_rate)
                    for g in top_genome
                    for r in range(int(rep))]

        if gen == self.gen-1:
            filename = 'Data/{}_{}_{}_Run{}_final.genome'.format(
                self.today,
                self.condition,
                self.csc,
                self.run_num)
            with open(filename, 'w', newline='') as data_file:
                wr = csv.writer(data_file, quoting=csv.QUOTE_ALL)
                # write header
                tail = self.trial_num + 1
                wr.writerow(self.header[:-tail])
                # write each row of data
                for p in range(len(next_gen)):
                    wr.writerow([p] + next_gen[p])
        else:
            # update self.genome
            self.genome = next_gen


def random_first_gen(pop, genome_size):
    """Generate random genome for the first generation."""
    def generate_random_genome(genome_size):
        genome = rd.choices(range(0, 256), k=genome_size)
        return genome

    first_gen = [generate_random_genome(genome_size)
                 for p in range(pop)]

    return first_gen


def make_header(genome_size, trial_num):
    """Generate header for the data files."""
    loci = ['locus_'+str(i) for i in range(genome_size)]
    trial_fit = ['trial_'+str(i)+'_fit' for i in range(trial_num)]
    header = ['pop'] + loci + ['total_fit'] + trial_fit
    return header
