import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import psutil

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def get_options():
    description = 'Parse snps counts to transmission events from snps-dist output dataframe. Default snp threshold is 10.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('snp_dists', help='Output dataframe from snp-dists as tsv file')
    parser.add_argument('data', help='Metadata containing sampling date, and if available, patient id')

    return parser.parse_args()

if __name__ == "__main__":
    options = get_options()

    # start measuring time
    start_time = time.time()

    # load data
    s = pd.read_csv(options.snp_dists, delimiter="\t", header=None)
    m = pd.read_csv(options.data, delimiter="\t")

    # rename columns
    s.rename(columns={0: 'sample1', 1: 'sample2', 2: 'snps'}, inplace=True)

    # merge metadata with SNP data
    s = s.merge(m[['sampleid', 'samplingdate', 'pat_id']], left_on='sample1', right_on='sampleid', how='left')
    s.rename(columns={'samplingdate': 'date1', 'pat_id': 'pat_id1'}, inplace=True)
    s = s.merge(m[['sampleid', 'samplingdate', 'pat_id']], left_on='sample2', right_on='sampleid', how='left')
    s.rename(columns={'samplingdate': 'date2', 'pat_id': 'pat_id2'}, inplace=True)

    # calculate date difference in days
    s['date_diff'] = (pd.to_datetime(s['date2']) - pd.to_datetime(s['date1'])).dt.days
    s['date_diff'] = s['date_diff'].abs()

    # drop rows if pat_id sample1 == pat_id sample2, only if pat_id is not NaN
    s = s[~((s['pat_id1'].notna()) & (s['pat_id2'].notna()) & (s['pat_id1'] == s['pat_id2']))]

    # calculate transmission events based on conditions
    # add option to add multiple columns based on multiple conditions
    # specify thresholds
    s['te_5_30d'] = ((s['snps'] <= 5) & (s['date_diff'] <= 30)).astype(int)
    s['te_10_30d'] = ((s['snps'] <= 10) & (s['date_diff'] <= 30)).astype(int)
    s['te_30_30d'] = ((s['snps'] <= 30) & (s['date_diff'] <= 30)).astype(int)
    s['te_50_30d'] = ((s['snps'] <= 50) & (s['date_diff'] <= 30)).astype(int)
    s['te_100_30d'] = ((s['snps'] <= 100) & (s['date_diff'] <= 30)).astype(int)
    s['te_5_60d'] = ((s['snps'] <= 5) & (s['date_diff'] <= 60)).astype(int)
    s['te_10_60d'] = ((s['snps'] <= 10) & (s['date_diff'] <= 60)).astype(int)
    s['te_30_60d'] = ((s['snps'] <= 30) & (s['date_diff'] <= 60)).astype(int)
    s['te_50_60d'] = ((s['snps'] <= 50) & (s['date_diff'] <= 60)).astype(int)
    s['te_100_60d'] = ((s['snps'] <= 100) & (s['date_diff'] <= 60)).astype(int)

    # reorder columns
    s = s[['sample1', 'sample2', 'te_5_30d', 'te_10_30d', 'te_30_30d', 'te_50_30d', 'te_100_30d',
           'te_5_60d', 'te_10_60d', 'te_30_60d', 'te_50_60d', 'te_100_60d', 'snps', 'date_diff', 'pat_id1', 'pat_id2']]

    # drop rows if sample1 == sample2
    s = s[s['sample1'] != s['sample2']]
    s.reset_index(drop=True, inplace=True)

    # print samples presenting transmission events
    print(s[s['te_10_30d'] == 1])

    # measure and print running time
    end_time = time.time()
    running_time = end_time - start_time
    print(f"Running time: {running_time:.2f} seconds")

    # measure and print memory usage
    memory_usage = get_memory_usage()
    print(f"Memory usage: {memory_usage:.2f} MB")

    # save
    output_file = f"{os.path.splitext(options.snp_dists)[0]}_te.tsv"
    s.to_csv(output_file, index=False, sep='\t')

