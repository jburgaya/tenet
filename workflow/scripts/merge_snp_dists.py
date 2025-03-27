import os
import pandas as pd

def merge_snp_dists(input_dir, output_file):
    # Initialize an empty list to hold dataframes
    dataframes = []
    
    # Iterate over directories in the input directory
    for cluster_dir in os.listdir(input_dir):
        cluster_path = os.path.join(input_dir, cluster_dir)
        
        # Check if the path is a directory and contains snp-dists.tsv
        snp_dists_file = os.path.join(cluster_path, "snp-dists.tsv")
        if os.path.isdir(cluster_path) and os.path.isfile(snp_dists_file):
            # Read the snp-dists.tsv file
            df = pd.read_csv(snp_dists_file, sep="\t", header=None)
            dataframes.append(df)
    
    # Concatenate all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Save the merged dataframe to the output file
    merged_df.to_csv(output_file, sep="\t", index=False, header=False)

if __name__ == "__main__":
    # Input and output paths
    input_directory = "out/clusters"
    output_filepath = "out/snp-dists_klebsiella.tsv"
    
    # Merge SNP distances
    merge_snp_dists(input_directory, output_filepath)

