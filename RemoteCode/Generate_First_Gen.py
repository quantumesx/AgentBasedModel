"""Generate files for the first generations for experiment runs."""

import random as rd
from Controller import convert_genome
import sys


def generate_first_gen(prefix, run, pop):
    """Generate the first generation genome for n experimental runs."""
    for r in range(run):
        print('Current run:', r)
        genome_69 = []
        for i in range(pop):
            genome_69.append(rd.choices(range(0, 256), k=69))

        # then generate genome of size 65
        genome_65 = [convert_genome(g) for g in genome_69]

        filename_69 = 'FirstGen/{}Run{}Pop{}69.txt'.format(prefix, r, pop)
        save_first_gen_files(genome_69, filename_69)
        filename_65 = 'FirstGen/{}Run{}Pop{}65.txt'.format(prefix, r, pop)
        save_first_gen_files(genome_65, filename_65)


def save_first_gen_files(genome, filename):
    """Save a generation's genome to a text file."""
    with open(filename, 'w') as f:
        for g in genome:
            g_s = [str(i) for i in g]
            f.write(",".join(g_s))
            f.write('\n')


def read_first_gen_files(filename):
    """Read a text file that contains a genome."""
    with open(filename, 'r') as f:
        first_gen = []
        raw = f.readlines()
        for l in raw:
            g = [int(s) for s in l.strip('\n').split(',')]
            first_gen.append(g)

    return first_gen


if __name__ == '__main__':

    # Either change these manually before running the script
    # Or take system arguments
    prefix = sys.argv[1]
    run = int(sys.argv[2])  # number of runs
    pop = int(sys.argv[3])  # number of genomes in each population
    generate_first_gen(prefix, run, pop)
