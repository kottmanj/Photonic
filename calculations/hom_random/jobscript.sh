#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --time=4:00:00
#SBATCH --job-name=photonic
#SBATCH --output=hom_job-%j.txt
#SBATCH --mail-type=FAIL
 
cd $SLURM_SUBMIT_DIR

source $HOME/bin/load_intel_compilers
 
module load intel/2018.2
module load intelpython3 

source /home/a/aspuru/kottmann/.virtualenvs/OpenVQE/bin/activate
export PYTHONPATH=${PYTHONPATH}:/home/a/aspuru/kottmann/devel/OpenVQE/
export PYTHONPATH=${PYTHONPATH}:/home/a/aspuru/kottmann/devel/photonic/

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

date
python write_inputs.py

for filename in input_* ; do
        echo "filename " $filename
        python hom_randomized_trotter.py filename=${filename}
	rm $filename
done

date 
