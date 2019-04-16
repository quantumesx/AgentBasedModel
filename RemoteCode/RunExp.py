"""
Run the experiment under the comm sensor + comm_self connected condition.

Take sys argumens:
Cond: 1, 2, 3 or 4
Comm_self: 'cs_conn' or 'cs_disconn'
Run: an integer designating the current run
"""

from Experiment import experiment
from Generate_First_Gen import read_first_gen_files
import sys
import pickle


# Preset experimental parameters
pop = 100
gen = 2
trial_num = 20
top = 20
prefix = 'JREvocomm'

if __name__ == '__main__':

    # System parameters
    cond = sys.argv[1]
    if cond == '1':
        genome_size = 69
    elif cond == '2':
        genome_size = 65
    elif cond == '3':
        genome_size = 69
    elif cond == '4':
        genome_size = 65
    else:
        print('Error: please enter a valid condition.')

    run_num = int(sys.argv[2])

    # The corresponding first gen files should be generated before running this
    # via the generate_first_gen function
    # There should be 2 different files for each run
    # The pop argument is there mostly to avoid naming conflict
    first_gen_file = 'FirstGen/{}Run{}Pop{}{}.txt'.format(prefix,
                                                          run_num,
                                                          pop,
                                                          genome_size)
    first_gen = read_first_gen_files(first_gen_file)

    e = experiment(condition=cond,
                   run_num=run_num, first_gen=first_gen, today=prefix,
                   pop=pop, gen=gen, trial_num=trial_num, include_top=top)

    e.run()
    e_filename = 'Data/Cond{}Run{}/{}_{}_{}_Run{}.exp'.format(cond,
                                                              run_num,
                                                              prefix,
                                                              e.condition,
                                                              e.csc,
                                                              run_num)
    pickle.dump(e, open(e_filename, 'wb'))
