# tenet: from assemblies to **t**ransmission **e**vents **net**works

Analysis of transmission events in bacterial strains.

# Pipeline

The pipeline consists on the following steps:
* Identify STs/SCs
* Split strains into PopPUNK SCs
* Select only strains with at least 10 strains/SC
* Align strains within each SC (ska build, ska align)
* Calculate SNPs per alignment
* Infer transmission events (snps2te)
* Get output df with all strains and all te
* Create tenet

# Author

Judit Burgaya (judit.burgaya@gmail.com | BuirgayaVentura.Judit@mh-hannover.de)
