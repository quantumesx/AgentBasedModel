"""
Run the test for a final genome.

Take sys argumens:
Cond: 1, 2, 3 or 4
Run: an integer designating the current run
"""

from Experiment import experiment
from Generate_First_Gen import read_first_gen_files
import sys
import pickle
from multiprocessing import Pool

# Preset experimental parameters
pop = 100
test_trial = 1000
prefix = 'JREvocomm'


class test():
    """Run a test."""

    def __init__(self,
                 condition,
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
        self.data_dir = 'Data/Cond{}Run{}/'.format(condition,
                                                   run_num)

        if condition == '1':
            self.condition = 'comm'
            self.comm_disabled = False
            self.csc_bool = True
            self.csc = 'cs_conn'
            self.genome_size = 69
        elif condition == '2':
            self.condition = 'comm'
            self.comm_disabled = False
            self.csc_bool = False
            self.csc = 'cs_disconn'
            self.genome_size = 65
        elif condition == '3':
            self.condition = 'no_comm'
            self.comm_disabled = True
            self.csc_bool = True
            self.csc = 'cs_conn'
            self.genome_size = 69
        elif condition == '4':
            self.condition = 'no_comm'
            self.comm_disabled = True
            self.csc_bool = False
            self.csc = 'cs_disconn'
            self.genome_size = 65
        else:
            print('Error: Please enter valid condition.')

        self.run_num = run_num

        self.pop = pop  # population size
        self.gen = gen  # total # of generations to run

        self.trial_num = trial_num  # trial to run for each team of robots
        self.include_top = include_top

        # header for data files
        self.header = make_header(self.genome_size, self.trial_num)

        self.genome = []  # updates every generation: [[p1, p2, ...]]
        self.fitness = []  # updates every generation: [[p1, p2, ...]]
        self.top = []

        # initialize genome for first gen
        self.genome = first_gen

        # initialize trial object
        # this ann doesn't matter; a new network will be generated for each pop
        place_holder_ann = MN_controller(self.genome[0],
                                         comm_self_connected=self.csc_bool)
        self.trial = trial(place_holder_ann, comm_disabled=self.comm_disabled)

        # self.genome.append(random_first_gen(self.pop, self.genome_size))


def test_genome(genome, cond):
    """Given a final genome, run 1000 trials for testing."""
    if cond == '1':
        genome_size = 69
        comm_disabled = False
        comm_self_connected = True
    elif cond == '2':
        genome_size = 65
        comm_disabled = False
        comm_self_connected = False
    elif cond == '3':
        genome_size = 69
        comm_disabled = True
        comm_self_connected = True
    elif cond == '4':
        genome_size = 65
        comm_disabled = True
        comm_self_connected = False
    else:
        print('Error: please enter a valid condition.')

    def get_genotype_fitness(self):
        """Get the fitness of a genotype through behavioral trials."""
        self.trial.run(record=False, save=False)
        # print(len(self.trial.ann.nodes[15]['activation']),
        #      len(self.trial.env.agents[0].ann.nodes[15]['activation']),
        #      len(self.trial.env.agents[0].loc_data))
        # self.trial.fitness
        return self.trial.fitness

    def get_all_fitness(self, params):
        """
        Get the fitness of an entire generation.

        params = (genome, p)
        written this way to enable multithreading
        """
        genome = params[0]
        p = params[1]

        # print('population: {} / {}'.format(p+1, self.pop))
        ann = MN_controller(genome, comm_self_connected=self.csc_bool)
        self.trial.new_ann(ann)
        # fitness of the trials
        total_fit = [self.get_genotype_fitness()
                     for i in range(self.trial_num)]

        # iterate through each trial; default = 20
        fitness = sum(total_fit) / self.trial_num

        # update both the genome and the fitness to gen_fitness
        return p, fitness, total_fit

    def get_gen_fitness(self, gen):
        """
        Run all trials for a generation.

        input:
        - gen_genome: a list of genome for every genotype in this generation
        - g: number indicating current generation #

        output:
        - gen_fitness: a list of the fitness for every corresponding population
        """
        gen_genome = self.genome

        # Just to make sure
        if len(gen_genome) != self.pop:
            print('Error: number of genome not equal to number of population.')

        params = [(gen_genome[p], p) for p in range(self.pop)]

        p = Pool(24)

        gen_fitness = p.map(self.get_all_fitness, params)

        p.close()
        p.join()

        filename = '{}_{}_{}_Run{}_Gen{}.dat'.format(self.today,
                                                     self.condition,
                                                     self.csc,
                                                     self.run_num,
                                                     gen)

        # pop, loci, total fitness, trial fitnesses
        flat_data = [
            [p] + gen_genome[p] + [gen_fitness[p][1]] + gen_fitness[p][2]
            for p in range(len(gen_fitness))
            ]

        with open(self.data_dir+filename, 'w', newline='') as data_file:
            wr = csv.writer(data_file, quoting=csv.QUOTE_ALL)

            wr.writerow(self.header)
            for l in flat_data:
                wr.writerow(l)


if __name__ == '__main__':


    # System parameters
    cond = sys.argv[1]
