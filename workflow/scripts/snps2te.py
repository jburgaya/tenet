import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import psutil


def get_memory_usage():
    """Returns the current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def get_options():
    """Parses command line arguments."""
    description = 'Parse SNP counts to transmission events from SNP-dists output dataframe. Default SNP threshold is 10.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('snp_dists', help='Output dataframe from snp-dists as TSV file')
    parser.add_argument('data', help='Metadata containing sampling date, and if available, patient ID')
    parser.add_argument('--snps', help='SNPs/day accumulation ratio', type=float, default=0.05)
    parser.add_argument('--min_snps', help='min number of SNPs considered a transmission independent of the time. Considering sequencing errors.', type=int, default=5)

    return parser.parse_args()


def load_data(snp_dists_path, metadata_path):
    """Loads SNP distances and metadata into pandas DataFrames."""
    s = pd.read_csv(snp_dists_path, delimiter="\t", header=None)
    m = pd.read_csv(metadata_path, delimiter="\t")
    return s, m


def prepare_data(s, m):
    """Merges metadata with SNP data and calculates date differences."""
    s.rename(columns={0: 'sample1', 1: 'sample2', 2: 'snps'}, inplace=True)

    # Merge metadata to add sampling dates
    s = s.merge(m[['sampleid', 'samplingdate']], left_on='sample1', right_on='sampleid', how='left')
    s.rename(columns={'samplingdate': 'date1'}, inplace=True)
    s = s.merge(m[['sampleid', 'samplingdate']], left_on='sample2', right_on='sampleid', how='left', suffixes=('', '_sample2'))
    s.rename(columns={'samplingdate': 'date2'}, inplace=True)

    # Ensure valid date parsing
    s['date1'] = pd.to_datetime(s['date1'], format='%Y-%m-%d', errors='coerce')
    s['date2'] = pd.to_datetime(s['date2'], format='%Y-%m-%d', errors='coerce')

    # Filter rows with missing dates
    s = s[s['date1'].notna() & s['date2'].notna()]

    # Calculate absolute date difference
    s['date_diff'] = (s['date2'] - s['date1']).dt.days.abs()

    # Additional patient ID filtering (if applicable)
    if 'pat_id' in m.columns:
        s = s.merge(m[['sampleid', 'pat_id']], left_on='sample1', right_on='sampleid', how='left')
        s.rename(columns={'pat_id': 'pat_id1'}, inplace=True)
        s = s.merge(m[['sampleid', 'pat_id']], left_on='sample2', right_on='sampleid', how='left', suffixes=('', '_sample2'))
        s.rename(columns={'pat_id': 'pat_id2'}, inplace=True)

        s = s[~((s['pat_id1'].notna()) & (s['pat_id2'].notna()) & (s['pat_id1'] == s['pat_id2']))]

    # Drop self-comparisons and duplicates
    s = s[s['sample1'] != s['sample2']]
    s.reset_index(drop=True, inplace=True)

    s['pair'] = s.apply(lambda row: '-'.join(sorted([str(row['sample1']), str(row['sample2'])])), axis=1)
    s = s.drop_duplicates(subset=['pair']).drop(columns=['pair'])

    return s


def calculate_transmission_events(s, snps_per_day, min_snps):
    """Calculates transmission events based on accumulated SNPs and adds a 'transmission' column."""
    # Calculate expected accumulated SNPs
    expected_snps = s["date_diff"] * snps_per_day

    # Calculate lower and upper bounds for the CI
    lower_bound = expected_snps * (1 - 0.05)
    upper_bound = expected_snps * (1 + 0.05)

    s['expected_snps'] = expected_snps
    s['CI'] = lower_bound.astype(str) + '-' + upper_bound.astype(str)
    
    # set transmission to 1 if:
    # snps are <= expected snps
    # snps fall within CI range
    s['transmission'] = np.where(
        (s['snps'] <= expected_snps) | 
        ((s['snps'] >= lower_bound) & (s['snps'] <= upper_bound)) |
        (s['snps'] < min_snps), 
        1, 
        0
    )

    # Add transmission for SNP thresholds
    thresholds = [10, 20, 30, 100]
    for t in thresholds:
        s[f'transmission_{t}SNP'] = np.where(s['snps'] < t, 1, 0)

    # Add transmission for date thresholds
    days_thresholds = [90, 180, 270, 365]
    for d in days_thresholds:
        s[f'transmission_{d}d'] = np.where((s['date_diff'] < d) & (s['transmission'] == 1), 1, 0)

    return s[['sample1', 'sample2', 'transmission', 'snps', 'expected_snps', 'CI', 'date_diff'] + 
             [f'transmission_{t}SNP' for t in thresholds] + 
             [f'transmission_{d}d' for d in days_thresholds]]


def save_results(s, output_file):
    """Saves the results to a TSV file."""
    s.to_csv(output_file, index=False, sep='\t')


def main():
    # Parse options
    options = get_options()

    # Start measuring time
    start_time = time.time()

    # Load SNP distances and metadata
    s, m = load_data(options.snp_dists, options.data)

    # Prepare and clean data
    s = prepare_data(s, m)

    # Calculate transmission events
    s = calculate_transmission_events(s, options.snps, options.min_snps)

    # Save the results
    output_file = f"{os.path.splitext(options.snp_dists)[0]}_te.tsv"
    save_results(s, output_file)

    # Measure and print running time
    running_time = time.time() - start_time
    print(f"Running time: {running_time:.2f} seconds")

    # Measure and print memory usage
    memory_usage = get_memory_usage()
    print(f"Memory usage: {memory_usage:.2f} MB")


if __name__ == "__main__":
    main()
