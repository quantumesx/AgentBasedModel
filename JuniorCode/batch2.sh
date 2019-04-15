#!/bin/bash
#SBATCH -J=evocomm
#SBATCH -o evocomm.out
#SBATCH --acount=xixu
#SBATCH --nodes=40
#SBATCH --tasks-per-node=1
#SBATCH --partition=general
#SBATCH --time=01:00:00
#SBATCH --mem=1GB
#SBATCH --mail-user=xixu@vassar.edu
#SBATCH --mail-type=ALL

cd /home/xixu/Code

python3 RunExpCommCS.py
