#!/bin/bash
#SBATCH -J c3r2
#SBATCH -o c3r2.out
#SBATCH --nodes=1
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo make data directory

cd /data/xixu/Evocomm/Data
echo make data directory

mkdir Cond3Run2

echo set home directory

cd /data/xixu/Evocomm

# for every run, change this, the out file name, and the second system param
echo start: condition = 3, run = 2

srun -n 1 -N 1 -o Cond3Run2.out python3 RunExp.py 3 2
