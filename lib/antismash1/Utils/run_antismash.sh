#!/bin/bash

fasta_file_path=$1
gff_file_path=$2
output_dir=$3


antismash_options_str=""
shift
shift
shift

for astr in "$@"; do
  antismash_options_str+=" $astr"
done

echo $antismash_options_str
#source /opt/conda3/etc/profile.d/conda.sh && conda activate py39  && antismash  $fasta_file_path --genefinding-gff3  $gff_file_path --clusterhmmer   --output-dir $output_dir  --cb-knownclusters --cc-mibig 
source /opt/conda3/etc/profile.d/conda.sh && conda activate py39  && antismash  $fasta_file_path --genefinding-gff3  $gff_file_path  --output-dir $output_dir  $antismash_options_str
