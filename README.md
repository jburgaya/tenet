# tenet: from assemblies to **t**ransmission **e**vents **net**works

Analysis of transmission events in bacterial strains.

# Pipeline

The pipeline consists on the following steps:

* Identify PopPunk sequence clusters (SCs)
* split_clusters.py -> Split strains into PopPUNK SCs with at least 6 strains/SC. Creates an extra dir with SC with less than 6 strains/SC. Creates names.txt and rfile.txt with strains within the cluster (as in PopPIPE pipeline).
* Align strains within each SC (ska build, ska align) w/ [ska](https://github.com/bacpop/ska.rust)
* Generate ML phylogeny w/ [iqtree](https://github.com/Cibiv/IQ-TREE)
* count_snps-py -> Calculate SNPs from fasta alignment. It uses [snp-dists](https://github.com/tseemann/snp-dists)
* snps2te.py -> Infer transmission events from snps, including metadata features: samplingdate and patient_id
  * Get output df with all strains and all te
* tenet -> Create transmission events networks and calculate network parameters over time

Part of the pipeline is based on [PopPIPE pipeline](https://github.com/jburgaya/PopPIPE/tree/master#poppipe-population-analysis-pipeline-)

# Get started

The pipeline depends on Conda.

```
conda env create -n tenet --file=environment.yml
conda create -n poppipe snakemake python numpy iqtree rapidnj ete3 ska pp-sketchlib poppunk r-fastbaps mandrake
```

# Author

Judit Burgaya (judit.burgaya@gmail.com | BuirgayaVentura.Judit@mh-hannover.de)
