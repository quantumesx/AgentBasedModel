"""Run a single trial."""

from Agent import agent
from Environment import environment
from Controller import controller

from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow
from Helper import find_dx, find_dy


class experiment():
    """Run an experiment."""

    def __init__(self,
                 pop=100,
                 gen=100,
                 iteration=1000,
                 time=0.1,
                 preset='M&N, 2003',
                 env_height=270, env_width=270, targets=True,
                 ):
        """Initialize the experiment."""
        pass


class trial():
    """Run a single trial."""

    def __init__(self,
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

        # initialize environment
        self.env = environment(width=env_width, height=env_height,
                               targets=targets)

        # the same ann used for this trial
        self.ann = controller(random=True)

        # initialize agents for the trial
        self.env.agents = [
            agent(name='robot0', color='red'),
            agent(name='robot1', color='orange'),
            agent(name='robot2', color='cyan'),
            agent(name='robot3', color='green')
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

    def run(self):
        """Run trial."""
        for i in tqdm(range(self.iteration)):
            # iterate through agents
            for a in self.env.agents:
                # store current location and sensor data
                a.loc_data.append(a.loc)
                a.ang_data.append(a.ang)

                # first get all sensor data
                a.get_ground_reading(self.env)
                a.get_ir_readings(self.env)
                a.get_comm_readings(self.env)
                a.comm_self_reading = a.comm_output

                # then get outputs
                # updates left_output, right_output, comm_output
                a.get_output()

                # store current sensor and actuator data
                a.input_data.append(a.ann.input_activation)
                a.output_data.append(a.ann.output_activation)

                # finally, get new location
                a.update_loc(self.env)
                # this updates loc and ang
                # so essential to store current data before this

        self.data = []
        for a in self.env.agents:
            self.data.append(
                [a.loc_data, a.ang_data, a.input_data, a.output_data]
            )

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
