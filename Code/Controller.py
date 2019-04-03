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
from Helper import normalize


class MN_controller():
    """Generate a MN controller."""

    def __init__(self, genome, i=14, h=2, o=3):
        """Initialize the network."""
        super().__init__()

        # initialize nodes
        self.i = i  # number of input nodes
        self.h = h  # number of hidden nodes
        self.o = o  # number of output nodes

        # genotype
        self.genome = genome

        # phenotype
        self.nodes = self.generate_node_list()
        self.connections = self.generate_connection_list()
        self.G_to_P()  # get phenotype from genome

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
            self.nodes[n]['activation'] = []
            if 'time_const_locus' in self.nodes[n].keys():
                self.nodes[n]['time_const'] = normalize(self.genome[
                    self.nodes[n]['time_const_locus']], out_min=0, out_max=1)
            if 'bias_locus' in self.nodes[n].keys():
                self.nodes[n]['bias'] = normalize(self.genome[
                    self.nodes[n]['bias_locus']])

        for c in self.connections.keys():
            self.connections[c]['weight'] = normalize(self.genome[
                self.connections[c]['weight_locus']])

    def iterate(self, inputs):
        """
        Update activations in nodes.

        inputs:
        - sensor inputs (expect)
        - self: layer parameters, nodes, connections

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

        # otherwise variable names are too long
        nodes = self.nodes
        conn = self.connections

        # whether weight is considered in comm_unit - comm_self connections
        comm_unit_weight = True

        # make sure the # of inputs is correct
        if len(inputs) != self.i-1:  # this should be 13
            print('Warning: incorrect input shape')

        # get the id # for all the neurons
        sensory_nodes = [n for n in nodes.keys()
                         if nodes[n]['type'] == 'sensor']
        internal_nodes = [n for n in nodes.keys()
                          if nodes[n]['type'] == 'internal']
        motor_nodes = [n for n in nodes.keys()
                       if nodes[n]['type'] == 'motor']

        # make sure the length of activations are as expected
        a_sensor = [nodes[n]['activation'] for n in sensory_nodes]
        len_sensor = [len(l) for l in a_sensor]

        a_internal = [nodes[n]['activation'] for n in internal_nodes]
        len_internal = [len(l) for l in a_internal]

        a_motor = [nodes[n]['activation'] for n in motor_nodes]
        len_motor = [len(l) for l in a_motor]

        s_valid = max(len_sensor) == min(len_sensor)
        i_valid = max(len_internal) == min(len_internal)
        m_valid = max(len_motor) == min(len_motor)
        diff_valid = (max(len_sensor) - max(len_motor) == -1)
        eq_valid = (max(len_motor) == max(len_internal) == 0)
        if not (s_valid and i_valid and m_valid and diff_valid and eq_valid):
            print('Warning: the lengths are not as predicted')
            print([len_sensor, len_internal, len_motor])
        else:
            print('lengths as predicted')

        # Step 1: update sensors
        for n in sensory_nodes:
            # computation for comm_self is different than other sensors
            if nodes[n]['name'] == 'comm_self':
                sum_signal = 0
                for c in conn.keys():
                    if conn[c]['output'] == n:  # there should only be one tho
                        if comm_unit_weight:
                            # method 1: treat comm_unit (t-1)* weight as sensor
                            # for internal and motors, activation at current
                            # time step t is already calculated, so t-1 is the
                            # second to last value.
                            input = nodes[conn[c]['input']]['activation'][-2]
                            weight = conn[c]['weight']
                            sum_signal += input * weight
                        else:
                            # method 2: treat comm_unit as sensor (no weight)
                            input = nodes[conn[c]['input']]['activation'][-2]
                            sum_signal += input
            # computation for other sensors
            else:
                signal = inputs[n]  # signal from the sensor inputs
                time_const = nodes[n]['time_const']  # the node's time constant
                activation_last = nodes[n]['activation'][-1]  # last time
                activation = activation_last * time_const \
                    + signal * (1 - time_const)  # sensor node activation func
                self.nodes[n]['activation'].append(activation)

        # Step 2: update internal nodes
        internal_activations = []
        for n in internal_nodes:
            sum_signals = 0
            for c in conn.keys():
                if conn[c]['output'] == n:
                    input = nodes[conn[c]['input']]['activation'][-1]
                    weight = conn[c]['weight']
                    sum_signals += input * weight

            bias = nodes[n]['bias']
            time_const = nodes[n]['time_const']
            a_last = nodes[n]['activation'][-1]
            a_raw = bias + sum_signals

            # activation func for internal nodes
            activation = a_last * time_const + \
                ((1 + math.e ** (-a_raw)) ** -1) * (1 - time_const)

            # do not activate directly; update all together at the end of func
            internal_activations.append((n, activation))

        # Step 3: update motor nodes
        motor_activations = []
        for n in motor_nodes:
            sum_signals = 0
            for c in conn.keys():
                if conn[c]['output'] == n:
                    input = nodes[conn[c]['input']]['activation'][-1]
                    weight = conn[c]['weight']
                    sum_signals += input * weight

            bias = nodes[n]['bias']
            a_raw = bias + sum_signals
            activation = 1 / (1 + math.e ** (-a_raw))

            # do not activate directly; update all together at the end of func
            internal_activations.append((n, activation))


        for n in nodes.keys():

            # get summation of activations of incoming signals
            sum_signals = 0

            for c in connections.keys():
                # get all the connections where the current node is
                if connections[c]['output'] == n:
                    # add the weighted signal to raw activation
                    sum_signals += nodes[connections[c]['input']]['activation'][i] * connections[c]['weight']

            # run the summation of signals through the activation function
            if nodes[n]['type'] == 'motor':
                bias = nodes[n]['bias']
                activation_raw = bias + sum_signals
                activation = 1 / 1 + math.e ** (-activation_raw)
                nodes[n]['activation'].append(activation)

            elif nodes[n]['type'] == 'internal':
                bias = nodes[n]['bias']
                time_const = nodes[n]['time_const']

                activation_raw = bias + sum_signals
                activation = nodes[n]['activation'][i] * time_const + (1 + math.e**(-activation_raw))** -1 * (1 - time_const)
                nodes[n]['activation'].append(activation)

            elif nodes[n]['type'] == 'sensor':
                time_const = nodes[n]['time_const']
                activation_raw = sum_signals

                activation = nodes[n]['activation'][i] * time_const + sum_signals * (1 - time_const)
                nodes[n]['activation'].append(activation)
`

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
