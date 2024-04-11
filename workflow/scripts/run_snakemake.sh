#!/bin/bash
#SBATCH --job-name=snakemake
#SBATCH --output=/vol/projects/jburgaya/pipeline/tenet/out/logs/snakemake.out
#SBATCH --error=/vol/projects/jburgaya/pipeline/tenet/out/logs/snakemake.err
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=20G
#SBATCH --time=48:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=judit.burgayaventura@helmholtz-hzi.de
#SBATCH --cluster=bioinf

# set path to conda
unset PYTHONPATH
export PATH=/vol/cluster-data/jburgaya/miniconda3/bin:$PATH
source /vol/cluster-data/jburgaya/miniconda3/etc/profile.d/conda.sh

cd /vol/projects/jburgaya/pipeline/tenet

# Run the provided command.
conda run -n poppipe "$@"

