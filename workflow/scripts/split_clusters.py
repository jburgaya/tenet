#!/usr/bin/env python

'''Split files into PopPUNK Sequence Clusters'''

def get_options():
  import argparse
  
  description = 'Split fasta files into their PopPUNK Sequence Clusters. Default min. 6 sequences per cluster'
  parser = argparse.ArgumentParser(description=description)

  parser.add_argument('dir_path',
                      help='Path to fasta files directory')
  parser.add_argument('txt_file',
                      help='PopPUNK output file')
  parser.add_argument('new_dir_path',
                      help='Path to directory where to split the files')
  parser.add_argument('--min_seq_per_cluster',
                      default=6,
                      type=int,
                      help='Minimum required number of sequences per cluster')
  
  return parser.parse_args()

if __name__ == "__main__":
  options = get_options()

  import os
  import shutil
  import pandas as pd

  def split_files(dir_path, txt_file, new_dir_path, min_seq_per_cluster):
    # load files
    df = pd.read_csv(txt_file, sep=',', header=None, names=['Taxon', 'Cluster'])

    # group by cluster and count the number of taxon
    clusters = df.groupby('Cluster')['Taxon'].count()

    # iterate through the clusters that have at least min_seq_per_cluster sequences
    for cluster, count in clusters[clusters >= min_seq_per_cluster].items():
        # get filenames for this cluster
        filenames = df[df['Cluster'] == cluster]['Taxon'].values + '.fna'

        # create the directory for this cluster
        cluster_dir = os.path.join(new_dir_path, 'clusters', str(cluster))
        os.makedirs(cluster_dir, exist_ok=True)

        # copy the fasta files for this cluster to the new directory
        for filename in filenames:
            src = os.path.join(dir_path, filename)
            if os.path.exists(src):
                dst = os.path.join(cluster_dir, filename)
                shutil.copy2(src, dst)
            else:
                print(f"File '{filename}' not found in the fasta directory.")

  split_files(options.dir_path, options.txt_file, options.new_dir_path, options.min_seq_per_cluster)
  print("done")
