"""Generate an agent."""

import random as rd
from Controller import controller
from Helper import find_dx, find_dy, find_loc, find_ang, norm_ang, get_distance
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow, Wedge, Ellipse, Rectangle
import math


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

    def get_ground_reading(self, env):
        """
        Get current sensor reading.

        If in target area, return 1; if not in target area, return 0.
        Calculation:

        Input:
        - env: for target_loc and target_r
        - self.loc

        Action:
        - update self.ground_reading

        """
        in_target = False
        reading = 0
        for target in env.targets:
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

    def get_comm_readings(self, agents):
        """
        Get comm sensor readings.

        Inputs:
        - position of the agent
        - position of all other agents
        - range of the 4 comm sensors

        Output:
        - list, reading of the 4 comm sensors
        """
        comm_sensors = self.comm_sensors

        received = [
            [0],
            [0],
            [0],
            [0]
        ]
        for agent in agents:
            # first, check if an agent is within range
            d = get_distance(self.loc, agent.loc)
            if d <= 100:  # if this is true, then it's within range
                # get the signal
                signal = agent.comm_output

                # determine which comm sensor receives the signal
                diff = norm_ang(find_ang(self.loc, agent.loc) - self.ang)

                if diff >= comm_sensors[0][0] or diff < comm_sensors[0][1]:
                    received[0].append(signal)
                elif diff >= comm_sensors[1][0] and diff < comm_sensors[1][1]:
                    received[1].append(signal)
                elif diff >= comm_sensors[2][0] and diff < comm_sensors[2][1]:
                    received[2].append(signal)
                elif diff >= comm_sensors[3][0] and diff < comm_sensors[3][1]:
                    received[3].append(signal)

        return max(received[0]), max(received[1]), \
            max(received[2]), max(received[3])

    def get_ir_readings(self, env):
        """Get readings for all IR sensors."""
        self.ir_readings = []

        # iterate through all ir sensors
        for i in range(len(self.ir_placement)):
            # first get loc and ang for the ir sensor
            placement_ang = norm_ang(self.ir_placement[i]+self.ang)
            # self.r-0.3 is default distance for IR sensor from center of body
            ir_loc = find_loc(self.loc, placement_ang, self.r-0.3)
            ir_ang = norm_ang(self.ir_ang[i]+self.ang)

            # get current reading for the ir sensor
            reading = self.ir_read(ir_loc, ir_ang, env)

            # update reading in the agent
            self.ir_readings.append(reading)

    def ir_read(ir_loc, ir_ang, env, ir_range=5):
        """
        Get the reading for an IR sensor.

        Inputs:
        - ir_loc: ir location, xy
        - ir_ang: ir angle
        - ir_range: default is 5 cm
        - env: environment; get width, height and agent attributes from it

        Output:
        - reading: float, sensor reading intensity, between 0 - 1
        """
        reading = 0

        # check wall
        distance_wall = []

        range_max = find_loc(ir_loc, ir_ang, ir_range)

        # 1st quadrant
        if ir_ang >= 0 and ir_ang < 90:
            # if this is true, then wall is detected
            if range_max[0] > env.width or range_max[1] > env.height:
                # if hitting wall via x axis
                if range_max[0] > env.width:
                    print('1st, x')
                    side_a = env.width - ir_loc[0]
                    ang_a = 90 - ir_ang
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    print('x diff:', side_a)
                    print('ang:', ang_a, 'distance:', d)
                    distance_wall.append(d)
                # if hitting wall via y axis
                if range_max[1] > env.height:
                    print('1st, y')
                    side_a = env.height - ir_loc[1]
                    ang_a = ir_ang
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    print('y diff:', side_a)
                    print('ang:', ang_a, 'distance:', d)
                    distance_wall.append(d)

        # 2nd quadrant
        elif ir_ang >= 90 and ir_ang < 180:
            # if this is true, then wall is detected
            if range_max[0] < 0 or range_max[1] > env.height:
                # if hitting wall via x axis
                if range_max[0] < 0:
                    print('2nd, x')
                    side_a = ir_loc[0]
                    ang_a = ir_ang - 90
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)
                # if hitting wall via y axis
                if range_max[1] > env.height:
                    print('2nd, y')
                    side_a = env.height - ir_loc[1]
                    ang_a = 180 - ir_ang
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)

        # 3rd quadrant
        elif ir_ang >= 180 and ir_ang < 270:
            # if this is true, then wall is detected
            if range_max[0] < 0 or range_max[1] < 0:
                # if hitting wall via x axis
                if range_max[0] < 0:
                    print('3rd, x')
                    side_a = ir_loc[0]
                    ang_a = 270 - ir_ang
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)
                # if hitting wall via y axis
                if range_max[1] < 0:
                    print('3rd, y')
                    side_a = ir_loc[1]
                    ang_a = ir_ang - 180
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)

        # 4th quadrant
        elif ir_ang >= 270 and ir_ang < 360:
            # if this is true, then wall is detected
            if range_max[0] > env.width or range_max[1] < 0:
                # if hitting wall via x axis
                if range_max[0] > env.width:
                    print('4th, x')
                    side_a = env.width - ir_loc[0]
                    ang_a = ir_ang - 270
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)
                # if hitting wall via x axis
                if range_max[1] < 0:
                    print('4th, y')
                    side_a = ir_loc[1]
                    ang_a = 360 - ir_ang
                    d = side_a * math.sin(math.radians(90)) / \
                        math.sin(math.radians(ang_a))
                    distance_wall.append(d)

        # detect agents
        distance_agents = []
        # iterate over each agent in the environment
        for a in env.agents:
            overlap = False
            detect = False

            # Step 1. Detection range overlap with agent?
            distance = get_distance(ir_loc, agent.loc)
            if distance < ir_range + agent.r:
                overlap = True
                print('\noverlap:', overlap)

            # Step 2. Check if agent at detectable angle
            if overlap:
                ir_agent_ang = find_ang(ir_loc, agent.loc)
                diff = abs(ir_ang-ir_agent_ang)
                # if the angle is greater than 180, take the complementary
                if diff > 180:
                    diff = 360 - diff

                if diff >= 90:
                    # pointed away, would not be able to detect the agent
                    print('pointed away')
                else:
                    side = get_distance(ir_loc, agent.loc)
                    # print('side:', side)
                    closest = side * math.sin(math.radians(diff)) / \
                        math.sin(math.radians(90))
                    # print(closest, agent_r)
                    if closest < agent.r:
                        print('detectable')
                        detect = True
                    else:
                        print('not close enough')

            if detect:
                possible_distance = []

                side_c = side
                side_a = agent.r
                ang_a = diff

                sin_c = side_c * (math.sin(math.radians(ang_a)) / agent.r)
                ang_c = math.degrees(math.asin(sin_c))

                for c in [ang_c, 180-ang_c]:
                    ang_b = 180 - (180-c) - ang_a
                    # print(ang_b, '\n')
                    side_b = math.sin(math.radians(ang_b)) * \
                        (side_a / math.sin(math.radians(ang_a)))
                    # print(side_b, '\n')
                    possible_distance.append(side_b)

                distance_agents.append(min(possible_distance))

        # review detection results
        distance = distance_wall + distance_agents
        if distance:
            reading = 1 - (ir_range - min(distance)) / ir_range

        return reading

    def get_output(self):
        """Feed input into the ann controller."""
        self.ann.input = self.ir_readings + \
            [self.ground_reading] + self.comm_reading + \
            [self.comm_self_reading]
        self.ann.feedforward()
        self.left_output = self.ann.output[0]
        self.right_output = self.ann.output[1]
        self.comm_output = self.ann.output[2]

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
