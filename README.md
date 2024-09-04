# Transmission  Events  NETworks

Analysis of transmission events in bacterial strains.

# Pipeline

Run PopPUNK outside the pipeline.

The pipeline consists on the following steps:

* ```split_clusters.py``` -> Split strains into PopPUNK SCs with at least 6 strains/SC. Creates an extra dir with SC with less than 6 strains/SC. Creates names.txt and rfile.txt with strains within the cluster (as in PopPIPE pipeline).
* Align strains within each SC using ska build & ska align, using [ska](https://github.com/bacpop/ska.rust)
* Generate ML phylogeny using [iqtree](https://github.com/Cibiv/IQ-TREE)
* Calculate SNPs from fasta alignment. It uses [snp-dists](https://github.com/tseemann/snp-dists)
* ```snps2te.py``` -> Infer transmission events from snps, including metadata features: samplingdate and patient_id
  * Get output df with all strains and all te
* ```tenet``` -> Create transmission events networks and calculate network parameters over time


Part of the pipeline is based on [PopPIPE pipeline](https://github.com/jburgaya/PopPIPE/tree/master#poppipe-population-analysis-pipeline-)


# Get started

The pipeline depends on Conda.

```
conda env create -n tenet --file=environment.yml
conda create -n tenet snakemake python numpy iqtree rapidnj ete3 ska pp-sketchlib poppunk r-fastbaps mandrake
```

# Author

Judit Burgaya (judit.burgaya@gmail.com | BurgayaVentura.Judit@mh-hannover.de)
