#!/bin/bash
#SBATCH -J evocomm
#SBATCH -o evocomm.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --time=05:00:00
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo directory set

cd /home/xixu/RemoteCode/

echo run 1

srun -n 1 -N 1 --time 1:00:00 -o cond1run0.out python3 RunExp.py 1 0
srun -n 1 -N 1 --time 1:00:00 -o cond2run0.out python3 RunExp.py 2 0
srun -n 1 -N 1 --time 1:00:00 -o cond3run0.out python3 RunExp.py 3 0
srun -n 1 -N 1 --time 1:00:00 -o cond4run0.out python3 RunExp.py 4 0

echo run 2

srun -n 1 -N 1 --time 1:00:00 -o cond1run1.out python3 RunExp.py 1 1
srun -n 1 -N 1 --time 1:00:00 -o cond2run1.out python3 RunExp.py 2 1
srun -n 1 -N 1 --time 1:00:00 -o cond3run1.out python3 RunExp.py 3 1
srun -n 1 -N 1 --time 1:00:00 -o cond4run1.out python3 RunExp.py 4 1
