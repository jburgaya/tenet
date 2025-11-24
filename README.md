# Transmission  Events  NETworks

Analysis of transmission events in bacterial strains.

# Pipeline

Run PopPUNK outside the pipeline.

The pipeline consists on the following steps:

* Split strains into PopPUNK SCs with at least 3 strains/SC. Creates names.txt and rfile.txt with strains within the cluster (as in PopPIPE pipeline). Clusters are found in `out/clusters/{strain}`
* Align strains within each SC using ska build & ska align, using [ska](https://github.com/bacpop/ska.rust)
* Generate ML phylogeny using [iqtree](https://github.com/Cibiv/IQ-TREE)
* Calculate SNPs from fasta alignment. It uses [snp-dists](https://github.com/tseemann/snp-dists)
* Infer transmission events from snps, considering metadata: samplingdate and patient_id (if present). `snps2te.py` the script computes the expected snps / time elapsed + 90% CI.
* Merge into single output file `out/te_merged.tsv`
* Create transmission events networks and calculate network parameters over time.


Part of the pipeline is based on [PopPIPE pipeline](https://github.com/jburgaya/PopPIPE/tree/master#poppipe-population-analysis-pipeline-)


# Get started

Make a copy of this repository

```
git clone --recursive https://github.com/jburgaya/tenet.git TENET
cd TENET 
```

The pipeline depends on Conda.

```
conda env create -n tenet --file=environment.yaml
conda activate tenet
```

Run the bootstrap script to create the input files and directories

```
bash bootstrap.sh
```

## Modify the config file

Modify the params in the `config/config.yml` file

```
# ----- params ----- #

# ska options
ska:
  fastq_qual: 20
  fastq_cov: 4
  kmer: 31
  single_strand: false
  freq_filter: 0.9

# IQ-TREE options
iqtree:
  model: GTR+G+ASC
  alternative: GTR+G

# snps2te
# based on within patient snps accumulation
snps_day_ratio: 0.08
min_snps: 5

# min cluster size
min_cluster_size: 3

# ----- inputs ----- #
# already there produced outisde the pipeline
# data
data: "data/data.tsv"

# poppunk
poppunk_rfile: "poppunk_input.txt"
poppunk_clusters: "out/poppunk/poppunk_clusters/poppunk_clusters_clusters.csv"
poppunk_h5: "out/poppunk/Klebsiella_pneumoniae_v3_full/Klebsiella_pneumoniae_v3_full.h5"

```

## Run the pipeline!

Then run snakemake, first with a dry run `-n`, and then the actual run.

```
snakemake --use-conda --cores 12 tree merge -p -n
snakemake --use-conda --cores 12 tree merge -p
```

# Outputs

The pipeline will produce a unique file in `out/te_merged.tsv` with the pairwise comparison between samples within the dataset, the snps and expected snps based on the given snps/day ratio, and the classification as a transmission event or not.

Only the sequence clusters with > 3 sequences will be considered to run the pipeline. A phylogenetic tree for each cluster will be computed, and store within `out/clusters/{strain}/{strain}_tree`.


# Author

Judit Burgaya (judit.burgaya@gmail.com | BurgayaVentura.Judit@mh-hannover.de)
