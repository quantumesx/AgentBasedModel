"""Compute sensor related things."""

from Helper import norm_ang, find_loc


class ir_sensor():
    """Methods for IR sensors."""

    def __init__(self):
        """Initialize an ir sensor."""
        super().__init__()

    def get_ir_loc(agent_loc, agent_ang, ir_ang):
        """Get location of IR sensor."""
        ang = norm_ang(ir_ang+agent_ang)
        loc = find_loc(agent_loc, ang, 10)  # 10: distance from agent's center

        return loc, ang

    def get_ir_reading(loc, ang, ir_range, agents):
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
        # check for wall
        tip = find_loc(loc, ang, ir_range)
        if tip[0] <= 0:
            distance = loc[0]/abs(tip[0]-loc[0])
        elif tip[1] <= 0:
            distance = loc[1]/abs(tip[1]-loc[1])

        else:
            distance = 1

        wall_reading = 1-distance

        # check for agent
        for a in agents:
            # distance = agents.loc[0]
            pass

        reading = wall_reading

        return reading


class ground_sensor():
    """Methods for Ground sensors."""

    def __init__(self, loc):
        """Initialize a ground sensor."""
        super().__init__()
        self.modality = 'Ground'
        self.loc = loc  # in relation to the agent's center point
        self.reading = 0

    def get_reading(self, targets):
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
        self.reading = 0
        for target in targets:
            print('target:', target)
            print('self:', self.loc)
            x_delta = self.loc[0] - target[0][0] # difference on the x axis
            y_delta = self.loc[1] - target[0][1] # difference on the y axis

            distance_sqr = x_delta**2 + y_delta**2
            # print(distance_sqr, target[1]**2)

            if distance_sqr <= target[1]**2:
                in_target = True
                print('in target area\n')
            else:
                print('not in target area\n')
        if in_target:
            self.reading = 1


class comm_sensor():
    """Methods for comm sensors."""

    def __init__(self):
        """Initialize a comm. sensor."""
        super().__init__()
        self.modality = 'comm_other'
        self.loc = (0, 0)
        self.min_ang = -45
        self.max_ang = 45
        self.min = 0
        self.max = 225
        self.reading = 0  # range = 0 - 255

    def get_reading():
        """Get comm sensor readings."""
