# tenet: from assemblies to **t**ransmission **e**vents **net**works

Analysis of transmission events in bacterial strains.

# Pipeline

The pipeline consists on the following steps:
* Identify PopPunk sequence clusters (SCs)

* Use [PopPIPE pipeline](https://github.com/jburgaya/PopPIPE/tree/master#poppipe-population-analysis-pipeline-) to:
  * Split strains into PopPUNK SCs with at least 10 strains/SC
  * Align strains within each SC (ska build, ska align)
  * Generate ML phylogeny 

* Use tenet pipeline to:
  * Calculate SNPs per alignment
  * Infer transmission events (snps2te)
  * Get output df with all strains and all te
  * Create transmission events networks and calculate network parameters over time

# Author

Judit Burgaya (judit.burgaya@gmail.com | BuirgayaVentura.Judit@mh-hannover.de)
