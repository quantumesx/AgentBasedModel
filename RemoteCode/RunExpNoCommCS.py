"""
Run the experiment under the no comm sensor + comm_self connected condition.

Takes 1 input argument: a number designating the current run.
"""

from Experiment import experiment
from Generate_First_Gen import read_first_gen_files
import sys
import pickle


pop = 10
gen = 3
trial_num = 3
top = 2
today = '2019_04_32'


run_num = int(sys.argv[1])  # number designating the current run
first_gen_file = 'FirstGen/Run{}Pop{}69.txt'.format(run_num, pop)
first_gen = read_first_gen_files(first_gen_file)


e = experiment(condition='no_comm', comm_self_connected=True,
               run_num=run_num, first_gen=first_gen, today=today,
               pop=pop, gen=gen, trial_num=trial_num, include_top=top)

if __name__ == '__main__':
    e.run()
    e_filename = 'Data/{}_comm_no_cs_conn_Run{}.exp'.format(today, run_num)
    pickle.dump(e, open(e_filename, 'wb'))
