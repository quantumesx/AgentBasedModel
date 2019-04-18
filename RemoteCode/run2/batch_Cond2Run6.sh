#!/bin/bash
#SBATCH -J c2r6
#SBATCH -o c2r6.out
#SBATCH --nodes=1
#SBATCH -w node3
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo make data directory

cd /data/xixu/Evocomm/Data
echo make data directory

mkdir Cond2Run6

echo set home directory

cd /data/xixu/Evocomm

# for every run, change this, the out file name, and the second system param
echo start: condition = 2, run = 6

srun -n 1 -N 1 -o Cond2Run6.out python3 RunExp.py 2 6
