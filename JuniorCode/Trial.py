"""Run a single trial."""

from Agent import agent
from Environment import environment
from Helper import get_distance

from copy import deepcopy


class trial():
    """Run a single trial."""

    def __init__(self,
                 controller,
                 comm_disabled=False,
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
        self.comm_disabled = comm_disabled
        self.verbose = verbose

        # initialize environment
        self.env = environment(width=env_width, height=env_height,
                               targets=targets)

        # the same ann used for this trial
        self.ann = deepcopy(controller)

        # initialize agents for the trial
        self.env.agents = [
            agent(name=self.name+'agent0', color='red'),
            agent(name=self.name+'agent1', color='orange'),
            agent(name=self.name+'agent2', color='cyan'),
            agent(name=self.name+'agent3', color='green')
            ]

    def trial_setup(self):
        """Set up initial positions for the agents."""
        def setup_agent(a):
            """Generate initial position for an agent."""
            a.randomize_position(self.env)
            a.loc_data = []
            a.ang_data = []
            a.input_data = []
            a.output_data = []
            a.ann = deepcopy(self.ann)

        [setup_agent(a) for a in self.env.agents]
        # validate the environment
        if self.verbose:
            self.env.show()

    def new_ann(self, controller):
        """Change ann for the trial without having to change anything else."""
        self.ann = deepcopy(controller)

    def run(self, record=True, save=False):
        """Run trial."""
        def run_step():
            """Run one iteration of the trial."""
            [run_step_agent(a) for a in self.env.agents]

        def run_step_agent(a):
            """Run one iteration of the trial of an agent."""
            # store current position
            a.loc_data.append(a.loc)
            a.ang_data.append(a.ang)

            # first get all sensor data
            a.get_ground_reading(self.env)
            a.get_ir_readings(self.env)
            a.get_comm_readings(self.env, comm_disabled=self.comm_disabled)

            # then get outputs
            # updates left_output, right_output, comm_output
            a.get_output()

            # This is technically a sensor node, but...
            # due to the way this is implemented, it's computed in the
            # ann controller
            # Update after network propagation in order to save data
            # can change this in the future

            # store current sensor and actuator data
            inputs = a.ir_readings + a.comm_readings + \
                [a.ground_reading]
            a.input_data.append(inputs)
            outputs = [a.left_output, a.right_output, a.comm_output]
            a.output_data.append(outputs)

            # finally, get new location
            a.update_loc(self.env)
            # this updates loc and ang
            # so essential to store current data before this

        # set up
        self.trial_setup()

        # run trials
        [run_step() for i in range(self.iteration)]

        # get fitness
        self.get_fitness()

        # record data
        if record:
            self.data = [[a.loc_data,
                          a.ang_data,
                          a.input_data,
                          a.output_data] for a in self.env.agents]
        # if save:
        #    pickle.dump(self.data, open('trial_data/' +
        #                                self.name + '.trial', 'wb'))

    def get_fitness(self):
        """Get fitness for all steps and overall fitness for the trial."""
        all_data = [a.loc_data for a in self.env.agents]

        loc_data = [
            [all_data[i][j] for i in range(len(all_data))]
            for j in range(len(all_data[0]))
            ]

        self.step_fitness = [self.get_step_fitness(l) for l in loc_data]
        self.fitness = sum(self.step_fitness)

    def get_step_fitness(self, positions):
        """Get fitness of a step in the trial."""
        def check_target(loc, r=2.6):
            """Check if an agent is inside a target area."""
            target1 = self.env.targets[0]
            target2 = self.env.targets[1]

            d1 = get_distance(target1[0], loc)
            d2 = get_distance(target2[0], loc)

            # if agent is in target 1, return '1'
            # if agent is in target 2, return '2'
            target = '0'
            if d1 < target1[1] + r:
                target = '1'
            elif d2 < target2[1] + r:
                target = '2'
            return target

        # determine target areas for each agent
        targets = [check_target(loc) for loc in positions]

        # calculate score
        score = 0
        if targets.count('1') > 2:
            score += 0.5
            score -= (targets.count('1') - 2)
        elif targets.count('1') <= 2:
            score += targets.count('1') * 0.25

        if targets.count('2') > 2:
            score += 0.5
            score -= (targets.count('2') - 2)
        elif targets.count('2') <= 2:
            score += targets.count('2') * 0.25

        return score
