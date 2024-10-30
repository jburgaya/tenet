import os
import sys
from pathlib import Path

def run_iqtree(alignment_file, output_tree, model, prefix, threads):
    command = f"iqtree --quiet -st DNA -s {alignment_file} -T {threads} --prefix {prefix} -m {model}"
    exit_code = os.system(command)
    return exit_code

def main(alignment_file, output_tree, model, alternative_model, prefix, threads):
    with open(alignment_file) as aln:
        sequences = sum(1 for line in aln if line.startswith(">"))

    if sequences < 3:
        Path(output_tree).write_text("")
        print(f"Skipped tree construction for {output_tree} due to insufficient sequences.")
    else:
        print(f"Running IQ-TREE with model {model} for {output_tree}")
        exit_code = run_iqtree(alignment_file, output_tree, model, prefix, threads)
        
        if exit_code != 0:
            print(f"Initial model failed. Trying alternative model {alternative_model} for {output_tree}")
            exit_code = run_iqtree(alignment_file, output_tree, alternative_model, prefix, threads)

            if exit_code != 0:
                sys.exit(f"IQ-TREE failed with both {model} and {alternative_model} models.")
            else:
                print(f"Tree construction succeeded with alternative model {alternative_model}.")
        else:
            print(f"Tree construction succeeded with model {model}.")

if __name__ == "__main__":
    main(
        snakemake.input.alignment,
        snakemake.output.tree,
        snakemake.params.model,
        snakemake.params.alternative_model,
        snakemake.params.prefix,
        snakemake.threads,
    )
