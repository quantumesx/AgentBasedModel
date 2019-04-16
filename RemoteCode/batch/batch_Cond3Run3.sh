#!/bin/bash
#SBATCH -J c3r3
#SBATCH -o c3r3.out
#SBATCH --nodes=1
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo make data directory

cd /data/xixu/Evocomm/Data
echo make data directory

mkdir Cond3Run3

echo set home directory

cd /data/xixu/Evocomm

# for every run, change this, the out file name, and the second system param
echo start: condition = 3, run = 3

srun -n 1 -N 1 -o Cond3Run3.out python3 RunExp.py 3 3
