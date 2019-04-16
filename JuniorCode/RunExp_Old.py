"""
Run the experiment under the comm sensor + comm_self connected condition.

Takes 1 input argument: a number designating the current run.
"""

from Experiment import experiment
from Generate_First_Gen import read_first_gen_files
import pickle
import time
from multiprocessing import Pool


runs = [
    ('FirstGen/Run1Pop1069.txt', 'comm', True, 0),
    ('FirstGen/Run1Pop1069.txt', 'comm', True, 1),
    ('FirstGen/Run2Pop1069.txt', 'comm', True, 2),
    ('FirstGen/Run2Pop1065.txt', 'comm', False, 0),
    ('FirstGen/Run0Pop1065.txt', 'comm', False, 1),
    ('FirstGen/Run0Pop1065.txt', 'comm', False, 2),
    ('FirstGen/Run1Pop1069.txt', 'no_comm', True, 0),
    ('FirstGen/Run1Pop1069.txt', 'no_comm', True, 1),
    ('FirstGen/Run2Pop1069.txt', 'no_comm', True, 2),
    ('FirstGen/Run2Pop1065.txt', 'no_comm', False, 0),
    ('FirstGen/Run0Pop1065.txt', 'no_comm', False, 1),
    ('FirstGen/Run0Pop1065.txt', 'no_comm', False, 2),
]

pop = 10
gen = 2
trial_num = 1
top = 2
today = 'parallel_1'


def run_exp(param):
    """Run an experiment according to given parameters."""
    first_gen = read_first_gen_files(param[0])

    e = experiment(condition=param[1], comm_self_connected=param[2],
                   run_num=param[3], first_gen=first_gen, today=today,
                   pop=pop, gen=gen, trial_num=trial_num, include_top=top)

    e.run()
    e_filename = 'Data/{}_comm_cs_conn_Run{}.exp'.format(today, param[3])
    pickle.dump(e, open(e_filename, 'wb'))
    result = 'done'
    print('ok:', param)
    return result


before = time.time()
# r = tuple(map(run_exp, runs))

p = Pool(12)
r = p.map(run_exp, runs)

after = time.time()
print('time: {}'.format(after-before))
print(r)
