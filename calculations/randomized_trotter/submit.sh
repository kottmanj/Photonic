#!/bin/bash

python write_inputs
for filename in input_* ; do
    echo "submitting filename=" $filename
    cat template | sed "s|XFILENAMEX|${filename}|g" > tmp_submit_script
    sbatch tmp_submit_script
    rm tmp_submit_script
done
