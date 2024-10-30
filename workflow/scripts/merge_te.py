#!/usr/bin/env python

import argparse
from pathlib import Path

def merge_files(input_files, output_file):
    """Merges multiple input files into a single output file."""
    with output_file.open('w') as outfile:
        # Write header from the first file
        with input_files[0].open('r') as first_file:
            header = first_file.readline()
            outfile.write(header)

        # Write content from all files, skipping headers for subsequent files
        for file_path in input_files:
            with file_path.open('r') as infile:
                if file_path != input_files[0]:  # Skip header in subsequent files
                    infile.readline()
                outfile.writelines(infile)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Merge TE files")
    parser.add_argument('input_files', nargs='+', help='Input files to merge')
    parser.add_argument('output_file', help='Output file path')
    args = parser.parse_args()

    input_files = [Path(file) for file in args.input_files]
    output_file = Path(args.output_file)

    # Check if there are any input files
    if not input_files:
        raise ValueError("No input files provided.")

    # Merge files
    merge_files(input_files, output_file)

if __name__ == "__main__":
    main()
