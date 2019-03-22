"""Generate an agent."""

import random as rd
from Controller import controller
from Helper import find_dx, find_dy, find_loc, norm_ang
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow, Wedge, Ellipse, Rectangle


class agent():
    """Generate an agent."""

    def __init__(self,
                 loc=(rd.uniform(20, 250), rd.uniform(20, 250)),
                 ang=(rd.uniform(0, 360)),
                 ir_ang=[90, 45, 0, 0, -45, -90, -180, 180],
                 ir_placement=[60, 36, 12, -12, -36, -60, -156, 156],
                 comm_sensors=[(315, 44), (45, 134), (135, 224), (225, 314)],
                 ann=controller(i=14, h=8, o=3),  # input, hidden, output #
                 ):
        """
        Initialize the environment.

        name: str, the name for the current environment
        Default height and width: 270
        """
        super().__init__()

        # fixed parameters
        self.r = 2.6

        # initial position
        self.loc = loc
        self.ang = ang
        self.color = (rd.uniform(0, 1), rd.uniform(0, 1), rd.uniform(0, 1))

        # set IR sensors
        self.ir_ang = ir_ang
        self.ir_placement = ir_placement
        self.ir_readings = [0]*len(ir_ang)

        # set ground sensor
        self.ground_reading = 0

        # set comm_others
        self.comm_sensors = comm_sensors
        self.comm_reading = [0]*len(comm_sensors)

        # controller
        self.ann = ann

        # actuators
        self.left_output = 0
        self.right_output = 0
        self.comm_output = 0

    def get_ground_reading(self, targets):
        """
        Get current sensor reading.

        If in target area, return 1; if not in target area, return 0.
        Calculation:

        Input:
        - target_loc
        - target_r
        - self.loc

        Validated: 03/05/19
        """
        in_target = False
        reading = 0
        for target in targets:
            # print('target:', target)
            # print('self:', self.loc)
            x_delta = self.loc[0] - target[0][0]  # difference on the x axis
            y_delta = self.loc[1] - target[0][1]  # difference on the y axis

            distance_sqr = x_delta**2 + y_delta**2
            # print(distance_sqr, target[1]**2)

            if distance_sqr <= target[1]**2:
                in_target = True
                # print('in target area\n')
            else:
                pass
                # print('not in target area\n')
        if in_target:
            reading = 1

        self.ground_reading = reading

    def get_ir_loc(agent_loc, agent_ang, ir_ang):
        """
        Get location of an IR sensor.

        Given agent loc, agent ang and ir ang relative to agent,
        find ir loc and ang.
        """
        ang = norm_ang(ir_ang+agent_ang)
        loc = find_loc(agent_loc, ang, 10)  # 10: distance from agent's center
        return loc, ang

    def get_ir_reading(self, ir_range=10):
        """
        Get reading in response to obstacle, including wall and other agents.

        The closer the distance, the higher the reading.
        Method:
        - 1. check for wall (write this first)
            - find intersect with the wall it's facing
            - check if distance is less than ir_range
            - right now, linear scaling
        - 2. check for other agents
            - for each of the other agents, check if center is within range
            - if so, check distance
        """
        for i in range(len(self.ir_angs)):
            ir_loc = get_ir_loc(self.loc, self.ang, self.ir_angs[i])
            loc = ir_loc[0]
            ang = ir_loc[1]
            # print(ir_loc)
            # check for wall
            tip = find_loc(loc, ang, ir_range)
            if tip[0] <= 0:
                distance = loc[0]/abs(tip[0]-loc[0])
                # print(loc[0], tip[0], distance)
            elif tip[1] <= 0:
                distance = loc[1]/abs(tip[1]-loc[1])
                # print(loc[1], tip[1], distance)
            else:
                distance = 1

            # print(distance)

            wall_reading = 1-distance

            # check for agent
            # for a in agents:
            # distance = agents.loc[0]**2

            reading = wall_reading
            self.ir_readings[i] = reading

    def get_output(self):
        """Feed input into the ann controller."""
        self.ann.input = self.ir_readings + \
            [self.ground_reading] + self.comm_reading + \
            [self.comm_self_reading]
        self.ann.feedforward()
        self.left_output = self.ann.output[0]
        self.right_output = self.ann.output[1]
        self.comm_output = self.ann.output[2]

    def get_comm_reading(self):
        """Get reading for the comm. sensors."""
        pass

    def update_loc(self):
        """
        Given speed of the wheel, calculate ang and displacement of agent.

        input: network output, float between 0 - 1

        ang: current ang + modifier
        displacement:
        """
        max_speed = 5

        left_speed = self.left_output*max_speed
        right_speed = self.right_output*max_speed

        # this is really rudimentary, need to change
        ang = (left_speed - right_speed) * 5.2
        distance = (left_speed + right_speed)/2

        # update ang
        self.ang = norm_ang(self.ang+ang)
        self.loc = find_loc(self.loc, self.ang, distance)

    def show(self, verbose=False):
        """Generate visualization of the agent."""
        # generate plot
        ax = plt.axes(xlim=(self.loc[0]-4, self.loc[0]+4),
                      ylim=(self.loc[1]-4, self.loc[1]+4))
        line, = ax.plot([], [])

        patches = self.get_patches(verbose)
        for p in patches:
            ax.add_patch(p)

        # fix aspect
        ax.set_aspect('equal')
        ax.figure.set_size_inches(6, 6)

        print(
            """
            position: {},
            angle: {}
            """.format(self.loc, self.ang)
        )

    def get_patches(self, verbose=False):
        """Get a list of patches for plotting via other functions."""
        patches = []

        if verbose:
            # body, color is cyan
            patches.append(Circle(self.loc, self.r, color='cyan'))

            # ground sensor
            patches.append(Circle(self.loc, 0.4, color='gray'))

            # comm unit
            patches.append(Circle(self.loc, 0.2, color='green'))

            # IR sensors
            for i in range(len(self.ir_ang)):

                # width and height of the rectangular IR sensor representation
                width = 0.2
                height = 0.5

                placement_ang = norm_ang(self.ir_placement[i]+self.ang)

                detect_ang = norm_ang(self.ir_ang[i]+self.ang)

                loc = find_loc(self.loc, placement_ang, self.r-0.3)

                patches.append(Rectangle((loc[0], loc[1]), width/2, height/2,
                                         angle=detect_ang, color='black'))
                patches.append(Rectangle((loc[0], loc[1]), height/2, width/2,
                                         angle=detect_ang+90, color='black'))
                patches.append(Rectangle((loc[0], loc[1]), width/2, height/2,
                                         angle=detect_ang+180, color='black'))
                patches.append(Rectangle((loc[0], loc[1]), height/2, width/2,
                                         angle=detect_ang+270, color='black'))

                # easier but uglier to use Ellipses; abandoned
                # ax.add_patch(Ellipse(loc, 0.2, 0.7,
                #                      angle=detect_ang, color='black'))
                patches.append(FancyArrow(loc[0], loc[1],
                                          find_dx(loc[0], detect_ang, 0.5),
                                          find_dy(loc[1], detect_ang, 0.5),
                                          color='black',
                                          length_includes_head=False,
                                          head_width=0.15))

            # comm sensors
            comm_sensors = self.comm_sensors
            # use different, random color to distinguish between the 4 sensors
            for comm_range in comm_sensors:
                patches.append(Wedge(self.loc, 0.8,
                               norm_ang(comm_range[0]+self.ang),
                               norm_ang(comm_range[1]+self.ang), 0.3,
                               color=(rd.uniform(0, 1),
                                      rd.uniform(0, 1),
                                      rd.uniform(0, 1))))

            # wheels
            left_ang = norm_ang(self.ang+90)
            right_ang = norm_ang(self.ang-90)
            left_center = find_loc(self.loc, left_ang, self.r-0.4)
            right_center = find_loc(self.loc, right_ang, self.r-0.4)
            # wheels are represented with a ellipse
            # width=0.3, length=1.5
            patches.append(Ellipse(left_center, 0.3, 1.5,
                                   left_ang, color='red'))
            patches.append(Ellipse(right_center, 0.3, 1.5,
                                   right_ang, color='red'))
            # add mid line
            patches.append(FancyArrow(self.loc[0], self.loc[1],
                                      find_dx(self.loc[0], self.ang, self.r),
                                      find_dy(self.loc[1], self.ang, self.r),
                                      color='black',
                                      length_includes_head=True,
                                      head_width=0.2))
        else:
            # body; color is as assigned
            patches.append(Circle(self.loc, self.r, color=self.color))

            # add a longer mid line for better display in the environment
            patches.append(FancyArrow(self.loc[0], self.loc[1],
                                      find_dx(self.loc[0], self.ang, 15),
                                      find_dy(self.loc[1], self.ang, 15),
                                      color='black',
                                      length_includes_head=True,
                                      head_width=6))

        return patches
