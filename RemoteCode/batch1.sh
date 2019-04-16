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

echo load module

module load python3

echo run 1

python3 RunExp.py 1 0
python3 RunExp.py 2 0
python3 RunExp.py 3 0
python3 RunExp.py 4 0

echo run 2

python3 RunExp.py 1 1
python3 RunExp.py 2 1
python3 RunExp.py 3 1
python3 RunExp.py 4 1
