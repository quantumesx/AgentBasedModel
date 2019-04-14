"""Generate an environment."""


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
