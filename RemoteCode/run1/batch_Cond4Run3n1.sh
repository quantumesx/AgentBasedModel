#!/bin/bash
#SBATCH -J c4r3
#SBATCH -o c4r3.out
#SBATCH --nodes=1
#SBATCH -w node3
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

echo make data directory

cd /data/xixu/Evocomm/Data
echo make data directory

mkdir Cond4Run3

echo set home directory

cd /data/xixu/Evocomm

# for every run, change this, the out file name, and the second system param
echo start: condition = 4, run = 3

srun -n 1 -N 1 -o Cond4Run3.out python3 RunExp.py 4 3
