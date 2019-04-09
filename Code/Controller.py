"""
The controller module.

Functions:
1. Creating a network
2. Updating weights of a network
3.
"""

import random as rd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrow
import math

from Helper import normalize


class MN_controller():
    """Generate a MN controller."""

    def __init__(self, genome=[], i=14, h=2, o=3,
                 genome_size=83, random=False, name='nameless_controller'):
        """Initialize the network."""
        super().__init__()

        # name
        self.name = name

        # initialize nodes
        self.i = i  # number of input nodes
        self.h = h  # number of hidden nodes
        self.o = o  # number of output nodes

        # genotype
        if genome:
            self.genome = genome
        elif random:
            genome = rd.choices(range(0, 255), k=genome_size)
            self.genome = genome
        else:
            print('Error: No genome.')

        # phenotype

        # with fixed default network architecture, use this to save time:
        self.nodes = self.get_default_nodes()
        self.connections = self.get_default_connections()

        # In the case of variable network dimensions, use the follow lines
        # self.nodes = self.generate_node_list()
        # self.connections = self.generate_connection_list()

        # initialize activations
        # for n in self.nodes.keys():
        #    self.nodes[n]['activation'] = []
        #    self.nodes[n]['activation'].append(0)
        #    if self.nodes[n]['type'] != 'sensory':
        #        self.nodes[n]['activation'].append(0)

        self.G_to_P()  # get phenotype from genome

    def get_default_nodes(self):
        """Return node list for default MN controller."""
        return default_node_list

    def get_default_connections(self):
        """Return connection list for default MN controller."""
        return default_connection_list

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

    def generate_connection_list(self):
        """Generate list of all possible connections for MN controller."""
        offset = self.i + self.h * 2 + self.o

        connections = {}
        n = 0

        for i in self.nodes.keys():
            # sensory nodes
            if self.nodes[i]['type'] == 'sensory':
                for j in self.nodes.keys():
                    # sensor to internal
                    if self.nodes[j]['name'] == 'internal_1':
                        connections[n] = {'input': i, 'output': j,
                                          'mode': 'sensor_to_internal',
                                          'weight_locus': n+offset}
                        n += 1
                    # sensor to motor
                    if self.nodes[j]['type'] == 'motor':
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
            if self.nodes[i]['name'] == 'comm_unit':
                for j in self.nodes.keys():
                    if self.nodes[j]['name'] == 'comm_self':
                        connections[n] = {'input': i, 'output': j,
                                          'mode': 'motor_to_sensor',
                                          'weight_locus': n+offset}
                        n += 1

        return connections

    def G_to_P(self):
        """Convert genome type to phenotype."""
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

    def propagate(self, inputs, comm_unit_weight=False, validate=False):
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
            index = [d['output'] for d in list(conn.values())]
            indices = [i for i, x in enumerate(index) if x == output_node]
            input_nodes = [conn[i]['input'] for i in indices]
            return input_nodes

        def get_connections(output_node):
            index = [d['output'] for d in list(conn.values())]
            indices = [i for i, x in enumerate(index) if x == output_node]
            return indices

        def get_sensory_activation(n, signal):
            """Get sensor activation, given node # and signal."""
            time_const = nodes[n]['time_const']  # the node's time constant
            activation_last = nodes[n]['activation'][-1]  # last time
            activation = activation_last * time_const \
                + signal * (1 - time_const)  # sensor node activation func
            self.nodes[n]['activation'].append(activation)

        def get_weighted_signal(c):
            """Get internal node sum signal, given node #."""
            input = nodes[conn[c]['input']]['activation'][-1]
            weight = conn[c]['weight']
            return input * weight

        def get_internal_activation(n):
            """Get internal node activation, given node #."""
            connections = get_connections(n)
            sum_signals = sum([get_weighted_signal(c) for c in connections])

            bias = nodes[n]['bias']
            time_const = nodes[n]['time_const']
            a_last = nodes[n]['activation'][-1]
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

            bias = nodes[n]['bias']
            a_raw = bias + sum_signals
            activation = 1 / (1 + math.e ** (-a_raw))

            # do not activate directly; update all together at the end of func
            return n, activation

        # otherwise variable names are too long
        nodes = self.nodes
        conn = self.connections

        # get the id # for all the neurons
        comm_self_node = 13
        other_sensory_nodes = [n for n in nodes.keys()
                               if nodes[n]['type'] == 'sensory' and n != 13]
        internal_nodes = [n for n in nodes.keys()
                          if nodes[n]['type'] == 'internal']
        motor_nodes = [n for n in nodes.keys()
                       if nodes[n]['type'] == 'motor']

        if validate:
            # make sure the # of inputs is correct
            if len(inputs) != self.i-1:  # this should be 13
                print('Warning: incorrect input shape')

            # make sure the length of activations are as expected
            a_sensor = [nodes[n]['activation']
                        for n in other_sensory_nodes]
            len_sensor = [len(l) for l in a_sensor] + 1

            a_internal = [nodes[n]['activation'] for n in internal_nodes]
            len_internal = [len(l) for l in a_internal]

            a_motor = [nodes[n]['activation'] for n in motor_nodes]
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
        comm_self_signal = 0
        for c in get_input_nodes(comm_self_node):  # there should only be 1
            if comm_unit_weight:
                    # method 1: treat comm_unit (t-1)* weight as sensor
                    # for internal and motors, activation at current
                    # time step t is already calculated, so t-1 is the
                    # second to last value.
                input = nodes[conn[c]['input']]['activation'][-2]
                weight = conn[c]['weight']
                comm_self_signal += input * weight
            else:
                # method 2: treat comm_unit as sensor (no weight)
                input = nodes[conn[c]['input']]['activation'][-2]
                comm_self_signal += input
        get_sensory_activation(comm_self_node, comm_self_signal)

        # Step 2: update internal nodes
        new_activations = [get_internal_activation(n)
                           for n in internal_nodes]
        new_activations += [get_motor_activation(n) for n in motor_nodes]

        for n, a in new_activations:
            nodes[n]['activation'].append(a)

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

                    color = 'gray'
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


class controller():
    """Generate a controller."""

    def __init__(self, genome=[], i=14, h=2, o=3, preset='',
                 verbose=False, random=False):
        # i: input, h: hidden, o: output
        """
        Initialize a network.

        Arguments:
        i = number of input nodes
        h = number of hidden nodes
        o = number of output nodes
        """
        super().__init__()

        # initialize nodes
        self.i = i  # number of input nodes
        self.h = h  # number of hidden nodes
        self.o = o  # number of output nodes

        self.genome = []

        self.input_activation = [0] * i  # activation of input nodes

        self.hidden_activation = [0]*h  # activation of hidden nodes
        self.hidden_bias = [0]*h  # bias of hidden nodes

        self.output_activation = [0]*o  # activation of output nodes
        self.output_bias = [0]*o  # bias of output nodes

        self.i2h_weights = [[0]*i]*h
        self.h2o_weights = [[0]*h]*o

        # Order of calculation:
        # First iterate through receiving nodes,
        # Then for each receiving node iterate through activated nodes
        # E.g.:
        # All input nodes->hidden 1; all input nodes->hidden 2; ...
        # Therefore the weights are formated correspondingly as:
        # [
        #   [input1-hidden1, input2-hidden1, ...],
        #   [all inputs to hidden2], ...
        # ]

        if random:
            self.initialize_random_weights()
            self.initialize_random_bias()
        elif genome:
            self.GtoP(genome)
        else:
            print('No genome; weights randomly generated.')
            self.initialize_random_weights()
            self.initialize_random_bias()

    def initialize_random_weights(self):
        """
        Initialize weights with random values.

        The random values are drawn from uniform distribution (-1, 1).
        """
        # initialize weights (random values from uniform distribution (-1, 1))
        self.i2h_weights = []
        for i in range(self.h):
            w = []
            for j in range(self.i):
                w.append(rd.uniform(-5, 5))
            self.i2h_weights.append(w)

        self.h2o_weights = []
        for i in range(self.o):
            w = []
            for j in range(self.h):
                w.append(rd.uniform(-5, 5))
            self.h2o_weights.append(w)

    def initialize_random_bias(self):
        """
        Initialize biases with random values.

        The random values are drawn from uniform distribution (-1, 1).
        """
        self.hidden_bias = []
        for i in range(self.h):
            self.hidden_bias.append(rd.uniform(-5, 5))

        self.output_bias = []
        for i in range(self.o):
            self.output_bias.append(rd.uniform(-5, 5))

    def update_MnN(self):
        """Perform network computation based on Maracoo and Nolfi (2003)."""
        pass

    def feedforward(self):
        """Perform feedforward computation."""
        # hidden node activation
        for i in range(self.h):
            h_raw = []
            for j in range(self.i):
                activation = self.hidden_bias[i] + \
                    self.input_activation[j] * self.i2h_weights[i][j]
                h_raw.append(activation)
            # currently use tanh as activation function
            self.hidden_activation[i] = np.tanh(sum(h_raw))
        # print(self.hidden)

        for i in range(self.o):
            o_raw = []
            for j in range(self.h):
                activation = self.output_bias[i] + \
                    self.hidden_activation[j] * self.h2o_weights[i][j]
                o_raw.append(activation)
            # currently use tanh as activation function
            self.output_activation[i] = np.tanh(sum(o_raw))

    def GtoP(self, genome):
        """
        Convert genome to network metrics.

        Need to update this to fit MN network.
        """
        n = 0

        self.i2h_weights = []
        for i in range(self.h):
            w = []
            for j in range(self.i):
                w.append(normalize(genome[n]))
                n += 1
            self.i2h_weights.append(w)
        print(n)

        self.h2o_weights = []
        for i in range(self.o):
            w = []
            for j in range(self.h):
                w.append(normalize(genome[n]))
                n += 1
            self.h2o_weights.append(w)
        print(n)

        self.hidden_bias = [normalize(x) for x in genome[n:n+self.h]]
        self.output_bias = [normalize(x) for x in genome[n+self.h:]]

    def mutate(self, rate=0.2):
        """Mutate weight and biases in a network."""
        # mutate input bias
        new_input_bias = []
        for i in range(self.i):
            if rd.uniform(0, 1) >= rate:
                new_input_bias.append(self.input_bias[i])
            else:
                new_input_bias.append(rd.uniform(-1, 1))
        self.input_bias = new_input_bias

        # mutate hidden bias
        new_hidden_bias = []
        for i in range(self.h):
            if rd.uniform(0, 1) >= rate:
                new_hidden_bias.append(self.hidden_bias[i])
            else:
                new_hidden_bias.append(rd.uniform(-1, 1))
        self.hidden_bias = new_hidden_bias

        # mutate output bias
        new_output_bias = []
        for i in range(self.o):
            if rd.uniform(0, 1) >= rate:
                new_output_bias.append(self.output_bias[i])
            else:
                new_output_bias.append(rd.uniform(-1, 1))
        self.output_bias = new_output_bias

        # mutate input to hideen weights
        new_i2h_weights = []
        for h in range(self.h):
            weights = []
            for i in range(self.i):
                if rd.uniform(0, 1) >= rate:
                    weights.append(self.i2h_weights[h][i])
                else:
                    weights.append(rd.uniform(-1, 1))
            new_i2h_weights.append(weights)
        self.i2h_weights = new_i2h_weights

        # mutate hideen to output weights
        new_h2o_weights = []
        for o in range(self.o):
            weights = []
            for h in range(self.h):
                if rd.uniform(0, 1) >= rate:
                    weights.append(self.h2o_weights[o][h])
                else:
                    weights.append(rd.uniform(-1, 1))
            new_h2o_weights.append(weights)
        self.h2o_weights = new_h2o_weights

        print('All mutated')

    def show(self):
        """Show network."""
        ax = plt.axes(xlim=(0, max(self.i, self.h, self.o)*25 + 25),
                      ylim=(0, 200))
        line, = ax.plot([], [])
        ax.set_aspect('equal')
        ax.figure.set_size_inches(5, 2)

        i_nodes = []
        h_nodes = []
        o_nodes = []

        x = 25
        y = 150
        for t in range(self.i):
            ax.add_patch(Circle((x, y), 10, color='green'))
            i_nodes.append((x, y))
            x += 25

        y -= 50
        x = (max(self.i, self.h, self.o)-self.h)/2 * 25 + 25
        for t in range(self.h):
            ax.add_patch(Circle((x, y), 10, color='purple'))
            h_nodes.append((x, y))
            x += 25

        y -= 50
        x = (max(self.i, self.h, self.o)-self.o)/2 * 25 + 25
        for t in range(self.o):
            ax.add_patch(Circle((x, y), 10, color='blue'))
            o_nodes.append((x, y))
            x += 25

        for t in i_nodes:
            for j in h_nodes:
                ax.add_patch(FancyArrow(t[0], t[1],
                                        j[0]-t[0], j[1]-t[1],
                                        width=0.00000001,
                                        color='black',
                                        length_includes_head=True,
                                        head_width=3))
        for t in h_nodes:
            for j in o_nodes:
                ax.add_patch(FancyArrow(t[0], t[1],
                                        j[0]-t[0], j[1]-t[1],
                                        width=0.00000001,
                                        color='black',
                                        length_includes_head=True,
                                        head_width=3))


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

default_connection_list = {
    0: {'input': 0,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 21},
    1: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 22},
    2: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 23},
    3: {'input': 0, 'mode': 'sensor_to_motor',
        'output': 18, 'weight_locus': 24},
    4: {'input': 1,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 25},
    5: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 26},
    6: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 17, 'weight_locus': 27},
    7: {'input': 1, 'mode': 'sensor_to_motor',
        'output': 18, 'weight_locus': 28},
    8: {'input': 2,
        'mode': 'sensor_to_internal',
        'output': 14,
        'weight_locus': 29},
    9: {'input': 2, 'mode': 'sensor_to_motor',
        'output': 16, 'weight_locus': 30},
    10: {'input': 2, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 31},
    11: {'input': 2, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 32},
    12: {'input': 3,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 33},
    13: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 34},
    14: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 35},
    15: {'input': 3, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 36},
    16: {'input': 4,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 37},
    17: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 38},
    18: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 39},
    19: {'input': 4, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 40},
    20: {'input': 5,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 41},
    21: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 42},
    22: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 43},
    23: {'input': 5, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 44},
    24: {'input': 6,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 45},
    25: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 46},
    26: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 47},
    27: {'input': 6, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 48},
    28: {'input': 7,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 49},
    29: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 50},
    30: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 51},
    31: {'input': 7, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 52},
    32: {'input': 8,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 53},
    33: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 54},
    34: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 55},
    35: {'input': 8, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 56},
    36: {'input': 9,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 57},
    37: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 16, 'weight_locus': 58},
    38: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 17, 'weight_locus': 59},
    39: {'input': 9, 'mode': 'sensor_to_motor',
         'output': 18, 'weight_locus': 60},
    40: {'input': 10,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 61},
    41: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 62},
    42: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 63},
    43: {'input': 10,
         'mode': 'sensor_to_motor',
         'output': 18,
         'weight_locus': 64},
    44: {'input': 11,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 65},
    45: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 66},
    46: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 67},
    47: {'input': 11,
         'mode': 'sensor_to_motor',
         'output': 18,
         'weight_locus': 68},
    48: {'input': 12,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 69},
    49: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 70},
    50: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 71},
    51: {'input': 12,
         'mode': 'sensor_to_motor',
         'output': 18,
         'weight_locus': 72},
    52: {'input': 13,
         'mode': 'sensor_to_internal',
         'output': 14,
         'weight_locus': 73},
    53: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 16,
         'weight_locus': 74},
    54: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 17,
         'weight_locus': 75},
    55: {'input': 13,
         'mode': 'sensor_to_motor',
         'output': 18,
         'weight_locus': 76},
    56: {'input': 14,
         'mode': 'internal_to_internal',
         'output': 15,
         'weight_locus': 77},
    57: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 16,
         'weight_locus': 78},
    58: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 17,
         'weight_locus': 79},
    59: {'input': 14,
         'mode': 'internal_to_motor',
         'output': 18,
         'weight_locus': 80},
    60: {'input': 15,
         'mode': 'internal_to_internal',
         'output': 14,
         'weight_locus': 81},
    61: {'input': 18,
         'mode': 'motor_to_sensor',
         'output': 13,
         'weight_locus': 82}
    }
