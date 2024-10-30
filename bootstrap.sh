#!/bin/bash

set -e -o pipefail -u

mkdir -p out
mkdir -p out/logs
mkdir -p data
mkdir -p out/poppunk
mkdir -p out/clusters
mkdir -p out/plots

# use this case when you need a file with two columns tab separated
# echo -e "ID\tPath" > out/unitigs_input.tsv
# use this case when you need a file with a column with file names or path to files
# cat /dev/null > out/mash_input.txt

# use this function to read file names from a directory and copy them to a file
#_read_file_names() {
#   local indir="$1"
#   local extension="${2:-_1.fastq.gz}"  # Default value if extension is not provided
#   for file in "$indir"/*"$extension"; do
#        if [ -f "$file" ]; then
#            file=$(basename "$file")
#            file=${file%"$extension"}
#            echo "$file"
#        fi
#    done
#}
# Usage example:
#indir="/path/to/your/directory"
#_read_file_names "$indir"

