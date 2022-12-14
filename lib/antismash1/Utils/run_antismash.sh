#!/bin/bash

fasta_file_path=$1
gff_file_path=$2
output_dir=$3

source /miniconda/etc/profile.d/conda.sh && conda activate py39  && antismash  $fasta_file_path --genefinding-gff3  $gff_file_path  --output-dir $output_dir  --cb-knownclusters --cc-mibig 

