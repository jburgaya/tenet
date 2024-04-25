import glob

input_pattern = "/vol/projects/jburgaya/pipeline/tenet/data/kpneumo/clusters/*/snp-dists_te.tsv"
output_file = "/vol/projects/jburgaya/pipeline/tenet/data/kpneumo/snp-dists_te_merged.tsv"

# Get a list of all files matching the input pattern
input_files = glob.glob(input_pattern)

# Open the output file in write mode
with open(output_file, 'w') as outfile:
    # Write the header from the first input file
    with open(input_files[0], 'r') as first_file:
        header = first_file.readline()
        outfile.write(header)

    # Concatenate data from all input files, skipping the header
    for file_path in input_files:
        with open(file_path, 'r') as infile:
            # Skip the header in all files except the first one
            if file_path != input_files[0]:
                next(infile)
            # Write the rest of the lines to the output file
            for line in infile:
                outfile.write(line)

