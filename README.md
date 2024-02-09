# iterative-chirality-correction

This code allows you to perform iterative chirality correction outside of the BIBSNet container using BIBSNet outputs, including both the derivatives and work dir, in order to solve chirality errors on superficial brain regions (importantly, it does not address current outstanding issues with midline chirality errors)

The `run.py` script takes a single argument `bibsnet_output_dir` which is the folder that contains subject/session folders each containing a subfolder called `work` that is BIBSNet work directory containing intermediate pipeline outputs 

This script runs serially instead of submitting each subject in parallel, but each operation per subject/session should only take 1-4 minutes

To execute, modify the input directory in line 18 of run.sh and execute `./run.sh` on the command line 