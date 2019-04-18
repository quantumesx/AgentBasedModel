"""Analyze results."""

from Controller import MN_controller
from Trial import trial
import pandas as pd
import pickle


def get_loci(df):
    loci = [c for c in df.columns if 'locus' in c]
    return loci


def get_genome(gen_df, pop):
    loci = [c for c in gen_df.columns if 'locus' in c]
    p = gen_df[gen_df['pop']==pop][loci].values.tolist()[0]
    return p


def test_fitness(gen_df, pop, cond):
    g = get_genome(gen_df, pop)
    print(len(g))
    print(g)
    if cond == 1:
        ann = MN_controller(g, comm_self_connected=True)
        t = trial(ann, comm_disabled=False)
    elif cond == 2:
        ann = MN_controller(g, comm_self_connected=False)
        t = trial(ann, comm_disabled=False)
    elif cond == 3:
        ann = MN_controller(g, comm_self_connected=True)
        t = trial(ann, comm_disabled=True)
    elif cond == 4:
        ann = MN_controller(g, comm_self_connected=False)
        t = trial(ann, comm_disabled=True)

    total = []
    for i in range(10):
        t.run()
        total.append(t.fitness)

    print(sum(total)/10)
    print(total)
    return total


def lookup_fit(gen_df, pop):
    p = gen_df[gen_df['pop'] == pop]['total_fit'].values.tolist()[0]
    print(p)
    return p
