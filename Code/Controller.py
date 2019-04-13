"""
The controller module.

Functions:
1. Create a network object (preset node/connections metrics based on MN2007)
2. Read a genome (list) and convert it into the phenotype of a network
3. Give sensor inputs, get motor output
"""

import random as rd
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow
import math

from Helper import normalize


class MN_controller():
    """Generate a MN controller."""

    def __init__(self, genome=[], i=14, h=2, o=3,
                 comm_self_connected=True,
                 random=False, name='nameless_controller'):
        """Initialize the network."""
        super().__init__()

        # name
        self.name = name

        # condition
        self.comm_self_connected = comm_self_connected

        # initialize nodes
        self.i = i  # number of input nodes
        self.h = h  # number of hidden nodes
        self.o = o  # number of output nodes

        # with fixed default network architecture, use this to save time:
        nodes = default_node_list

        if comm_self_connected:
            self.genome_size = 69
            conn = default_connections
        else:
            self.genome_size = 65
            conn = default_connections_no_comm_self

        # genotype
        if genome:
            if len(genome) == self.genome_size:
                self.genome = genome
            else:
                print('Warning: Genome not expected size {}.'.format(
                    self.genome_size))
                if len(genome) == 69 and self.genome_size == 65:
                    print('Corrected.')
                    self.genome = [genome[i] for i in range(len(genome))
                                   if i not in comm_self_loci_new]
                else:
                    print('Not corrected')
        elif random:
            print('Warning: generating random network')
            self.genome = rd.choices(range(0, 256), k=self.genome_size)
        else:
            print('Error: No genome.')

        # get phenotype from genome
        nodes, conn = G_to_P(self.genome, nodes, conn)
        self.nodes = nodes
        self.connections = conn

    def generate_node_list(self):
        """Generate list of nodes for MN controller."""
        nodes = {}
        for n in range(self.i):
            if n <= 7:
                name = 'IR_' + str(n)
            elif n > 7 and n <= 11:
                name = 'comm_' + str(n-8)
            elif n == 12:
                name = 'ground'
            elif n == 13:
                name = 'comm_self'
            else:
                print('Error: unknown sensory neuron identity.')
            nodes[n] = {'type': 'sensory', 'name': name, 'time_const_locus': n}

        for n in range(self.h):
            name = 'internal_' + str(n+1)
            nodes[n+self.i] = {'type': 'internal', 'name': name,
                               'time_const_locus': n+self.i,
                               'bias_locus': n+self.i+self.h}

        for n in range(self.o):
            if n == 0:
                name = 'motor_left'
            elif n == 1:
                name = 'motor_right'
            elif n == 2:
                name = 'comm_unit'
            else:
                print('Error: unknown motor neuron identity.')
            nodes[n+self.i+self.h] = {'type': 'motor', 'name': name,
                                      'bias_locus': n+self.i+self.h*2}
        return nodes

    def generate_connection_list(self, comm_self_connected=True):
        """
        Generate list of all possible connections for MN controller.

        This version is exactly as the diagram shows.
        comm_self_connected:
        - if set to True, the network connections are exactly as the diagram
            suggests in M & N (2007).
                - Corresponds with a genome_size of 69
        - if set to False, connections to the comm_self nodes will not
            be included. This is used to see whether self modulation is
            needed for the evolution of communicationself.
                - This leads to 44 possible connections
                - Corresponds with a genome_size of 65
        """
        offset = self.i + self.h * 2 + self.o

        connections = {}
        n = 0

        for i in self.nodes.keys():
            # sensory nodes
            if self.nodes[i]['type'] == 'sensory':
                # comm_self node
                if self.nodes[i]['name'] == 'comm_self':
                    # do this only if comm_self_connected is set to be true
                    if comm_self_connected:
                        for j in self.nodes.keys():
                            # comm_self to motors and comm_unit
                            if self.nodes[j]['type'] == 'motor':
                                connections[n] = {'input': i, 'output': j,
                                                  'mode': 'sensor_to_motor',
                                                  'weight_locus': n+offset}
                                n += 1

                # other sensory nodes
                else:
                    for j in self.nodes.keys():
                        # sensor to internal
                        if self.nodes[j]['name'] == 'internal_1':
                            connections[n] = {'input': i, 'output': j,
                                              'mode': 'sensor_to_internal',
                                              'weight_locus': n+offset}
                            n += 1
                        # sensor to motor except for comm_unit
                        if self.nodes[j]['type'] == 'motor':
                            if self.nodes[j]['name'] != 'comm_unit':
                                connections[n] = {'input': i, 'output': j,
                                                  'mode': 'sensor_to_motor',
                                                  'weight_locus': n+offset}
                                n += 1

            # internal node 1
            if self.nodes[i]['name'] == 'internal_1':
                for j in self.nodes.keys():
                    # sensor to internal
                    if self.nodes[j]['name'] == 'internal_2':
                        connections[n] = {'input': i, 'output': j,
                                          'mode': 'internal_to_internal',
                                          'weight_locus': n+offset}
                        n += 1
                    # sensor to motor
                    if self.nodes[j]['type'] == 'motor':
                        connections[n] = {'input': i, 'output': j,
                                          'mode': 'internal_to_motor',
                                          'weight_locus': n+offset}
                        n += 1

            # internal node 2
            if self.nodes[i]['name'] == 'internal_2':
                for j in self.nodes.keys():
                    # sensor to internal
                    if self.nodes[j]['name'] == 'internal_1':
                        connections[n] = {'input': i, 'output': j,
                                          'mode': 'internal_to_internal',
                                          'weight_locus': n+offset}
                        n += 1

            # comm unit to comm_self
            # do this only if comm_self_connected is set to be true
            if comm_self_connected:
                if self.nodes[i]['name'] == 'comm_unit':
                    for j in self.nodes.keys():
                        if self.nodes[j]['name'] == 'comm_self':
                            connections[n] = {'input': i, 'output': j,
                                              'mode': 'motor_to_sensor',
                                              'weight_locus': n+offset}
                            n += 1
        return connections

    """
    def G_to_P(self):
        """"""Convert genome type to phenotype.""""""
        for n in self.nodes.keys():
            if 'time_const_locus' in self.nodes[n].keys():
                self.nodes[n]['time_const'] = normalize(self.genome[
                    self.nodes[n]['time_const_locus']], out_min=0, out_max=1)
            if 'bias_locus' in self.nodes[n].keys():
                self.nodes[n]['bias'] = normalize(self.genome[
                    self.nodes[n]['bias_locus']])

        for c in self.connections.keys():
            self.connections[c]['weight'] = normalize(self.genome[
                self.connections[c]['weight_locus']])
            print(self.connections[c]['weight'])
    """

    def sensor_to_motor(self, inputs):
        """
        Get motor outputs.

        Given the inputs, propagate the information, and return motor outputs.
        """
        # make sure the # of inputs is correct
        if len(inputs) != self.i-1:  # this should be 13
            print('Warning: incorrect input shape')

        self.propagate(inputs)

        # Use the following code if need to change controller architecture
        # for n in self.nodes.keys():
        #    if self.nodes[n]['name'] == 'motor_left':
        #        motor_left = self.nodes[n]['activation'][-1]
        #    elif self.nodes[n]['name'] == 'motor_right':
        #        motor_right = self.nodes[n]['activation'][-1]
        #    elif self.nodes[n]['name'] == 'comm_unit':
        #        comm_unit = self.nodes[n]['activation'][-1]

        # Otherwise, since we know the node id, this saves time
        motor_left = self.nodes[16]['activation'][-1]
        motor_right = self.nodes[17]['activation'][-1]
        comm_unit = self.nodes[18]['activation'][-1]

        return motor_left, motor_right, comm_unit

    def propagate(self, inputs, validate=False):
        """
        Update activations in nodes.

        inputs:
        - sensor inputs (expect)
        - self: layer parameters, nodes, connections
        - comm_unit_weight: whether weight is considered in the
            comm_unit - comm_self connections. If False, then the weight
            will always be set to 1

        actions:
        - get sensor activation for the current timestep
        - get internal neuron and motor activation for the next timestep
        - update these activation to the self.nodes attribute

        Note:
        - This function does not take into consideration of the actual # of the
        current timestep, and assumes that we start with activations of all
        nodes for the last time step as well as activation for internal & motor
        nodes for the current time step.
        - In this case, all sensory nodes activation list should have the same
        length, l (l>0), while other nodes should have length l+1 at the
        beginning of the operation.
        - The operation needs to be performed in the specific order as defined
        in this function.
            - step 1: get sensor activation (t) via sensor reading inputs
              (for comm_self (t), via comm_unit (t-1))
            - step 2: get internal nodes activation at t+1 via sensor(t)
            - step 3: get motor activation at t+1 via internal(t) and sensor(t)
        """
        def get_input_nodes(output_node):
            """Get all input giving nodes for a (internal or motor) node."""
            index = [d['output'] for d in list(self.connections.values())]
            indices = [i for i, x in enumerate(index) if x == output_node]
            input_nodes = [self.connections[i]['input'] for i in indices]
            return input_nodes

        def get_connections(output_node):
            index = [d['output'] for d in list(self.connections.values())]
            indices = [i for i, x in enumerate(index) if x == output_node]
            return indices

        def get_sensory_activation(n, signal):
            """Get sensor activation, given node # and signal."""
            # the node's time constant
            time_const = self.nodes[n]['time_const']
            activation_last = self.nodes[n]['activation'][-1]  # last time
            activation = activation_last * time_const \
                + signal * (1 - time_const)  # sensor node activation func

            self.nodes[n]['activation'].append(activation)

        def get_weighted_signal(c):
            """Get internal node sum signal, given node #."""
            input = self.nodes[self.connections[c]['input']]['activation'][-1]
            weight = self.connections[c]['weight']
            return input * weight

        def get_internal_activation(n):
            """Get internal node activation, given node #."""
            connections = get_connections(n)
            sum_signals = sum([get_weighted_signal(c) for c in connections])

            bias = self.nodes[n]['bias']
            time_const = self.nodes[n]['time_const']
            a_last = self.nodes[n]['activation'][-1]
            a_raw = bias + sum_signals

            # activation func for internal nodes
            activation = a_last * time_const + \
                ((1 + math.e ** (-a_raw)) ** -1) * (1 - time_const)

            # do not activate directly; update all together at the end of func
            return n, activation

        def get_motor_activation(n):
            """Get motor node activation, given node #."""
            connections = get_connections(n)
            sum_signals = sum([get_weighted_signal(c) for c in connections])

            bias = self.nodes[n]['bias']
            a_raw = bias + sum_signals
            activation = 1 / (1 + math.e ** (-a_raw))

            # do not activate directly; update all together at the end of func
            return n, activation

        # get the id # for all the neurons
        comm_self_node = 13
        other_sensory_nodes = [n for n in self.nodes.keys()
                               if self.nodes[n]['type'] == 'sensory'
                               and n != 13]
        internal_nodes = [n for n in self.nodes.keys()
                          if self.nodes[n]['type'] == 'internal']
        motor_nodes = [n for n in self.nodes.keys()
                       if self.nodes[n]['type'] == 'motor']

        if validate:
            # make sure the # of inputs is correct
            if len(inputs) != self.i-1:  # this should be 13
                print('Warning: incorrect input shape')

            # make sure the length of activations are as expected
            a_sensor = [self.nodes[n]['activation']
                        for n in other_sensory_nodes]
            len_sensor = [len(l) for l in a_sensor] + 1

            a_internal = [self.nodes[n]['activation'] for n in internal_nodes]
            len_internal = [len(l) for l in a_internal]

            a_motor = [self.nodes[n]['activation'] for n in motor_nodes]
            len_motor = [len(l) for l in a_motor]

            s_valid = max(len_sensor) == min(len_sensor)
            i_valid = max(len_internal) == min(len_internal)
            m_valid = max(len_motor) == min(len_motor)
            diff_valid = (max(len_sensor) - max(len_motor) == -1)
            eq_valid = (max(len_motor) == max(len_internal))
            if not (s_valid and i_valid and m_valid
                    and diff_valid and eq_valid):
                print('Warning: the lengths are not as predicted')
                print([len_sensor, len_internal, len_motor])
            # else:
                # print('lengths as predicted')

        # Step 1: update sensors
        [get_sensory_activation(n, inputs[n]) for n in other_sensory_nodes]

        # computation for comm_self is different than other sensors

        comm_unit = 18
        comm_self_signal = self.nodes[comm_unit]['activation'][-2]

        get_sensory_activation(comm_self_node, comm_self_signal)

        # Step 2: update internal nodes
        new_activations = [get_internal_activation(n) for n in internal_nodes]
        new_activations += [get_motor_activation(n) for n in motor_nodes]

        for n, a in new_activations:
            self.nodes[n]['activation'].append(a)

    def show(self):
        """Show network plot."""
        ax = plt.axes(xlim=(0, max(self.i, self.h, self.o)*25 + 100),
                      ylim=(0, 200))
        line, = ax.plot([], [])
        ax.set_aspect('equal')
        ax.figure.set_size_inches(5, 2)

        nodes = []

        x = 25
        y = 50
        for t in range(self.i):
            ax.add_patch(Circle((x, y), 10, color='green'))
            nodes.append((t, x, y))
            x += 25

        y += 50
        x = max(self.i, self.h, self.o) * 25 + 25
        for t in range(self.h):
            ax.add_patch(Circle((x, y), 10, color='purple'))
            nodes.append((t+self.i, x, y))
            x += 25

        y += 50
        x = (max(self.i, self.h, self.o)-self.o)/2 * 25 + 25
        for t in range(self.o):
            ax.add_patch(Circle((x, y), 10, color='blue'))
            nodes.append((t+self.i+self.h, x, y))
            x += 25

        for i in nodes:
            for c in self.connections.keys():
                if self.connections[c]['input'] == i[0]:
                    out = self.connections[c]['output']
                    j = nodes[out]

                    color = 'black'
                    if self.connections[c]['weight'] < 0:
                        color = 'blue'
                    elif self.connections[c]['weight'] > 0:
                        color = 'red'
                    ax.add_patch(FancyArrow(i[1], i[2],
                                            j[1]-i[1], j[2]-i[2],
                                            width=0.001,
                                            color=color,
                                            length_includes_head=True,
                                            head_width=5))

        ax.set_aspect('equal')
        ax.figure.set_size_inches(6, 6)


def G_to_P(genome, nodes, connections):
    """Convert genome type to phenotype."""
    # nodes
    for n in nodes.keys():
        if 'time_const_locus' in nodes[n].keys():
            nodes[n]['time_const'] = normalize(genome[
                nodes[n]['time_const_locus']], out_min=0, out_max=1)
        if 'bias_locus' in nodes[n].keys():
            nodes[n]['bias'] = normalize(genome[
                nodes[n]['bias_locus']])
    # connections
    for c in connections.keys():
        connections[c]['weight'] = normalize(genome[
            connections[c]['weight_locus']])

    return nodes, connections


def convert_genome(genome):
    """Convert genome size 69 to genome size 65."""
    if len(genome) == 69:
        new_genome = [genome[i] for i in range(len(genome))
                      if i not in comm_self_loci_new]
    else:
        print('Error: genome size is not as expected (69).')
        new_genome = []
    return new_genome


# loci to get rid of going from size 83 to 69
extra_loci = [24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 73]
# loci to get rid of going from size 83 to 65
comm_self_loci_old = [74, 75, 76, 82]
# loci to get rid of going from size 69 to 65
comm_self_loci_new = [60, 61, 62, 68]

default_node_list = {
    0: {'activation': [0],
        'name': 'IR_0',
        'time_const_locus': 0,
        'type': 'sensory'},
    1: {'activation': [0],
        'name': 'IR_1',
        'time_const_locus': 1,
        'type': 'sensory'},
    2: {'activation': [0],
        'name': 'IR_2',
        'time_const_locus': 2,
        'type': 'sensory'},
    3: {'activation': [0],
        'name': 'IR_3',
        'time_const_locus': 3,
        'type': 'sensory'},
    4: {'activation': [0],
        'name': 'IR_4',
        'time_const_locus': 4,
        'type': 'sensory'},
    5: {'activation': [0],
        'name': 'IR_5',
        'time_const_locus': 5,
        'type': 'sensory'},
    6: {'activation': [0],
        'name': 'IR_6',
        'time_const_locus': 6,
        'type': 'sensory'},
    7: {'activation': [0],
        'name': 'IR_7',
        'time_const_locus': 7,
        'type': 'sensory'},
    8: {'activation': [0],
        'name': 'comm_0',
        'time_const_locus': 8,
        'type': 'sensory'},
    9: {'activation': [0],
        'name': 'comm_1',
        'time_const_locus': 9,
        'type': 'sensory'},
    10: {'activation': [0],
         'name': 'comm_2',
         'time_const_locus': 10,
         'type': 'sensory'},
    11: {'activation': [0],
         'name': 'comm_3',
         'time_const_locus': 11,
         'type': 'sensory'},
    12: {'activation': [0],
         'name': 'ground',
         'time_const_locus': 12,
         'type': 'sensory'},
    13: {'activation': [0],
         'name': 'comm_self',
         'time_const_locus': 13,
         'type': 'sensory'},
    14: {'activation': [0, 0],
         'bias_locus': 16,
         'name': 'internal_1',
         'time_const_locus': 14,
         'type': 'internal'},
    15: {'activation': [0, 0],
         'bias_locus': 17,
         'name': 'internal_2',
         'time_const_locus': 15,
         'type': 'internal'},
    16: {'activation': [0, 0],
         'bias_locus': 18,
         'name': 'motor_left',
         'type': 'motor'},
    17: {'activation': [0, 0],
         'bias_locus': 19,
         'name': 'motor_right',
         'type': 'motor'},
    18: {'activation': [0, 0],
         'bias_locus': 20,
         'name': 'comm_unit',
         'type': 'motor'}
    }

default_connections = {
    0: {'input': 0,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 21},
    1: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 22},
    2: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 23},
    3: {'input': 1,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 24},
    4: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 25},
    5: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 26},
    6: {'input': 2,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 27},
    7: {'input': 2, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 28},
    8: {'input': 2, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 29},
    9: {'input': 3,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 30},
    10: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 31},
    11: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 32},
    12: {'input': 4,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 33},
    13: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 34},
    14: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 35},
    15: {'input': 5,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 36},
    16: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 37},
    17: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 38},
    18: {'input': 6,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 39},
    19: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 40},
    20: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 41},
    21: {'input': 7,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 42},
    22: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 43},
    23: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 44},
    24: {'input': 8,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 45},
    25: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 46},
    26: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 47},
    27: {'input': 9,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 48},
    28: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 49},
    29: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 50},
    30: {'input': 10,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 51},
    31: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 52},
    32: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 53},
    33: {'input': 11,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 54},
    34: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 55},
    35: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 56},
    36: {'input': 12,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 57},
    37: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 58},
    38: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 59},
    39: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 60},
    40: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 61},
    41: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 18,
         'weight_locus': 62},
    42: {'input': 14,
         'mode': 'internal_to_internal',
         'output': 15,
         'weight_locus': 63},
    43: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 16,
         'weight_locus': 64},
    44: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 17,
         'weight_locus': 65},
    45: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 18,
         'weight_locus': 66},
    46: {'input': 15,
         'mode': 'internal_to_internal',
         'output': 14,
         'weight_locus': 67},
    47: {'input': 18,
         'mode': 'motor_to_sensor',
         'output': 13,
         'weight_locus': 68}
    }

default_connections_no_comm_self = {
    0: {'input': 0,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 21},
    1: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 22},
    2: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 23},
    3: {'input': 1,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 24},
    4: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 25},
    5: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 26},
    6: {'input': 2,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 27},
    7: {'input': 2, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 28},
    8: {'input': 2, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 29},
    9: {'input': 3,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 30},
    10: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 31},
    11: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 32},
    12: {'input': 4,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 33},
    13: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 34},
    14: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 35},
    15: {'input': 5,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 36},
    16: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 37},
    17: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 38},
    18: {'input': 6,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 39},
    19: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 40},
    20: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 41},
    21: {'input': 7,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 42},
    22: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 43},
    23: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 44},
    24: {'input': 8,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 45},
    25: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 46},
    26: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 47},
    27: {'input': 9,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 48},
    28: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 49},
    29: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 50},
    30: {'input': 10,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 51},
    31: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 52},
    32: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 53},
    33: {'input': 11,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 54},
    34: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 55},
    35: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 56},
    36: {'input': 12,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 57},
    37: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 58},
    38: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 59},
    39: {'input': 14,
         'mode': 'internal_to_internal',
         'output': 15,
         'weight_locus': 60},
    40: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 16,
         'weight_locus': 61},
    41: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 17,
         'weight_locus': 62},
    42: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 18,
         'weight_locus': 63},
    43: {'input': 15,
         'mode': 'internal_to_internal',
         'output': 14,
         'weight_locus': 64}}
