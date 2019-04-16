#!/bin/bash
#SBATCH -J c1r0
#SBATCH -o c1r0.out
#SBATCH --nodes=1
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo make data directory

cd /data/xixu/Evocomm/Data
echo make data directory

mkdir Cond1Run0

echo set home directory

cd /data/xixu/Evocomm

# for every run, change this, the out file name, and the second system param
echo start: condition = 1, run = 0

srun -n 1 -N 1 -o Cond1Run0.out python3 RunExp.py 1 0
