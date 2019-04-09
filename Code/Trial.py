"""Run a single trial."""

from Agent import agent
from Environment import environment
from Helper import find_dx, find_dy, get_distance

from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow

from Controller import MN_controller

from tqdm import tqdm
import random as rd


class experiment():
    """Run an experiment."""

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
        self.trial = 20  # trial to run for each group in the population
        self.include_top = include_top

        self.genome_size = genome_size
        self.genome = []  # [[g1p1, g1p2, ...], [g2p1, g2p2, ...], ...]
        self.fitness = []  # [[g1p1, g1p2, ...], [g2p1, g2p2, ...], ...]
        self.top = []

        if new_run:
            self.generate_first_gen()
        else:
            pass

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
        for g in range(self.gen):
            print('Current generation:', g)

            # Get fitness for all populations
            pop_fitness = self.run_gen(self.genome[-1])

            # select 20 best performing teams
            top_genome = self.select_top(pop_fitness, top=self.include_top)
            self.top.append(top_genome)

            new_gen = self.get_new_population(top_genome)

            self.fitness.append(pop_fitness)
            self.genome.append(new_gen)

    def run_gen(self, gen_genome):
        """
        Run all trials for a generation.

        input:
        - gen_genome: a list of genome for every population in this generation
        - g: number indicating current generation #

        output:
        - gen_fitness: a list of the fitness for every corresponding population
        """
        # Just to make sure
        if len(gen_genome) != self.pop:
            print('Error: number of genome not equal to number of population.')

        gen_fitness = []

        # iterate through each population; default = 100
        for p in tqdm(range(self.pop)):
            genome = gen_genome[p]

            ann = MN_controller(genome)
            total_fit = []  # fitness of the trials

            # iterate through each trial; default = 20
            for i in range(self.trial):
                t = trial(ann)
                t.run(record=False)
                total_fit.append(t.fitness)
            fitness = sum(total_fit) / self.trial

            # update both the genome and the fitness to gen_fitness
            gen_fitness.append([genome, fitness])

        return gen_fitness

    def select_top(self, gen_fitness, top=20):
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
                                           reverse=True)[:top]]

        return top_genome

    def get_new_population(self, top_genome, mutation_rate=0.02):
        """
        Get new population.

        input:
        - top_genome: n top genome from the last generation
        - mutation_rate: rate of mutation, default = 0.02

        output:
        - next_gen: list of new genome for the next generation.
                    (length = self.population)
        """
        def mutate(l, mutation_rate):
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

        rep = self.pop / len(top_genome)
        if rep != int(rep):
            print('Warning: expected number of replica is not an integer.')

        next_gen = []
        # for every genotype:
        for g in top_genome:
            for r in range(int(rep)):
                # for every location:
                new = [mutate(l, mutation_rate) for l in g]
                next_gen.append(new)

        return next_gen


class trial():
    """Run a single trial."""

    def __init__(self,
                 ann,
                 iteration=1000,
                 time=0.1,
                 name='unnamed_trial',
                 preset='M&N, 2003',
                 env_height=270, env_width=270, targets=True,
                 verbose=False
                 ):
        """Initialize a trial."""
        super().__init__()
        self.name = name  # name for the trial
        self.preset = preset  # preset name
        self.iteration = iteration  # total numbers of iterations
        self.step_time = 0.1  # time for each iteration step in seconds
        self.step_fitness = []  # fitness at each timestep
        self.fitness = 0  # total fitness

        # initialize environment
        self.env = environment(width=env_width, height=env_height,
                               targets=targets)

        # the same ann used for this trial
        self.ann = ann

        # initialize agents for the trial
        self.env.agents = [
            agent(name=self.name+'agent0', color='red'),
            agent(name=self.name+'agent1', color='orange'),
            agent(name=self.name+'agent2', color='cyan'),
            agent(name=self.name+'agent3', color='green')
            ]

        for a in self.env.agents:
            a.randomize_position(self.env)
            a.loc_data = []
            a.ang_data = []
            a.input_data = []
            a.output_data = []
            a.ann = self.ann

        # validate the environment
        if verbose:
            self.env.show()

    def run(self, record=True):
        """Run trial."""
        self.step_fitness = []
        for i in range(self.iteration):
            # iterate through agents
            for a in self.env.agents:
                # store current location and sensor data
                a.loc_data.append(a.loc)
                a.ang_data.append(a.ang)

                # store current fitness score

                # first get all sensor data
                a.get_ground_reading(self.env)
                a.get_ir_readings(self.env)
                a.get_comm_readings(self.env)

                # then get outputs
                # updates left_output, right_output, comm_output
                a.get_output()

                # This is technically a sensor node, but...
                # due to the way this is implemented, it's computed in the
                # ann controller
                # Update after network propagation in order to save data
                # can change this in the future
                a.comm_self_reading = a.ann.nodes[13]['activation'][-1]

                # store current sensor and actuator data
                inputs = a.ir_readings + a.comm_readings + \
                    [a.ground_reading] + [a.comm_self_reading]
                a.input_data.append(inputs)
                outputs = [a.left_output, a.right_output, a.comm_output]
                a.output_data.append(outputs)

                # finally, get new location
                a.update_loc(self.env)
                # this updates loc and ang
                # so essential to store current data before this
            self.step_fitness.append(self.get_step_fitness(self.env.agents))

        if record:
            self.data = [[a.loc_data,
                          a.ang_data,
                          a.input_data,
                          a.output_data] for a in self.env.agents]

        self.fitness = sum(self.step_fitness)

    def get_step_fitness(self, agents):
        """Get fitness of a trial."""
        target1 = self.env.targets[0]
        target2 = self.env.targets[1]

        t1 = 0
        t2 = 0
        for a in agents:
            d1 = get_distance(target1[0], a.loc)
            d2 = get_distance(target2[0], a.loc)
            if d1 < target1[1] + a.r:
                t1 += 1
            if d2 < target2[1] + a.r:
                t2 += 1

        score = 0
        for t in [t1, t2]:
            if t <= 2:
                score += 0.25 * t
            else:
                score += 0.5
                score -= 1 * t - 2

        return score

    def show(self):
        """Plot out the trial."""
        ax = plt.axes(xlim=(-30, 300), ylim=(-30, 300))
        line, = ax.plot([], [])

        ax.add_patch(FancyArrow(0, 0, 300, 0, color='black'))
        ax.add_patch(FancyArrow(0, 0, 0, 300, color='black'))
        ax.add_patch(FancyArrow(270, 270, 0, -300, color='black'))
        ax.add_patch(FancyArrow(270, 270, -300, 0, color='black'))

        # add targets
        for target in self.env.targets:
            ax.add_patch(Circle(target[0], target[1], color='gray'))

        for a in self.env.agents:
            for i in range(self.iteration):
                ax.add_patch(Circle(a.loc_data[-i], a.r, color=a.color))
                ax.add_patch(FancyArrow(a.loc_data[-i][0], a.loc_data[-i][1],
                                        find_dx(a.loc_data[-i][0],
                                                a.ang_data[-i], a.r),
                                        find_dy(a.loc_data[-i][1],
                                                a.ang_data[-i], a.r),
                                        color='black',
                                        length_includes_head=True,
                                        head_width=0.2))

        ax.set_aspect('equal')
        ax.figure.set_size_inches(6, 6)
