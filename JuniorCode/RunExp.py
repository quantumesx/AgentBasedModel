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

# System parameters
cond = sys.argv[1]
if cond == '1':
    comm_cond = 'comm'
    cs_cond = True
    genome_size = 69
elif cond == '2':
    comm_cond = 'comm'
    cs_cond = False
    genome_size = 65
elif cond == '3':
    comm_cond = 'no_comm'
    cs_cond = True
    genome_size = 69
elif cond == '4':
    comm_cond = 'no_comm'
    cs_cond = False
    genome_size = 65
else:
    print('Error: please enter a valid condition.')

run_num = sys.argv[2]

# Preset experimental parameters
pop = 50
gen = 3
trial_num = 10
top = 10
prefix = 'JRtest'


run_num = 0  # number designating the current run

# The corresponding first gen files should be generated before running this
# via the generate_first_gen function
# There should be 2 different files for each run
# The pop argument is there mostly to avoid naming conflict
first_gen_file = 'FirstGen/{}Run{}Pop{}{}.txt'.format(prefix,
                                                      run_num,
                                                      pop,
                                                      genome_size)
first_gen = read_first_gen_files(first_gen_file)


e = experiment(condition=comm_cond, comm_self_connected=cs_cond,
               run_num=run_num, first_gen=first_gen, today=prefix,
               pop=pop, gen=gen, trial_num=trial_num, include_top=top)

if __name__ == '__main__':
    e.run()
    e_filename = 'Data/{}_{}_{}_Run{}.exp'.format(prefix,
                                                  comm_cond,
                                                  cs_cond,
                                                  run_num)
    pickle.dump(e, open(e_filename, 'wb'))
