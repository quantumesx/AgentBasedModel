#!/bin/bash
#SBATCH -J test_data
#SBATCH -o test_data.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo set home directory

cd /data/xixu/Evocomm

echo condition = 1

# for every run, change this, the out file name, and the second system param
echo run = 0, test data storage

srun -n 1 -N 1 --time 15:00:00 -o new_test.out python3 RunExp.py 1 0
