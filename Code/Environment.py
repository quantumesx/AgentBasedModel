"""Generate an environment."""

from matplotlib import pyplot as plt
from matplotlib.patches import Circle


class environment():
    """Generate an environment."""

    def __init__(self, name='M&N, 2003', height=270, width=270, targets=True):
        """
        Initialize the environment.

        name: str, the name for the current environment
        Default height and width: 270
        """
        super().__init__()
        self.name = name
        self.height = height
        self.width = width
        self.targets = []
        self.agents = []

        self.initialize_targets()

    def initialize_targets(self):
        """Add targets as described in Marocoo & Nolfi (2007)."""
        self.add_target(target_loc=(80, 80), target_r=35)
        self.add_target(target_loc=(190, 190), target_r=35)

    def add_target(self, target_loc, target_r):
        """
        Set parameters for the target areas of the environment.

        target_loc: list of tuples, (x, y) coordinates for each target area
        target_r: int, radius of the target areas
        """
        self.targets.append([target_loc, target_r])

    def show(self, verbose=False):
        """Plot out the current environment (including targets and agents)."""
        ax = plt.axes(xlim=(0, self.width), ylim=(0, self.height))
        line, = ax.plot([], [])

        patches = self.get_patches(verbose)
        for p in patches:
            ax.add_patch(p)

        # add text to notate position of each agent
        for i in range(len(self.agents)):
            ax.text(self.agents[i].loc[0]+10, self.agents[i].loc[1], str(i+1))

        ax.set_aspect('equal')

    def get_patches(self, verbose=False):
        """Get a list of patches for plotting via other functions."""
        patches = []
        for target in self.targets:
            patches.append(Circle(target[0], target[1], color='gray'))

        for agent in self.agents:
            p = agent.get_patches(verbose)
            patches += p

        return patches
