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

echo cond1 run0

srun -n 1 -N 1 --time 1:00:00 -o cond1run0.out python3 RunExp.py 1 0
