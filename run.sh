#!/bin/bash
sbatch <<EOT
#!/bin/bash -l

#SBATCH --job-name=it_CC
#SBATCH --mem=32g
#SBATCH --time=24:00:00
#SBATCH --ntasks=4
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=lmoore@umn.edu
#SBATCH -e logs/iterativeCC-%j.err
#SBATCH -o logs/iterativeCC-%j.out
#SBATCH -A feczk001

module load fsl

python3 run.py /home/elisonj/shared/BCP/process/dcan_bibsnet/output_brainmasks

EOT