#!/usr/bin/env python

import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib import rcParams

sns.set_style('ticks', rc={"axes.facecolor": (0, 0, 0, 0)})
sns.set_context('talk')

from scipy.stats import spearmanr
from statsmodels.stats.multitest import fdrcorrection

def get_options():
    import argparse

    description = 'Generate correlations from network parameters and COVID19 restrictions'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('net',
                        help='Network parameters output from tenet.py')
    parser.add_argument('data',
                        help='Metadata')
    parser.add_argument('restrictions',
                        help='Tab separated data with covid restrictions')

    return parser.parse_args()


if __name__ == "__main__":
    options = get_options()

    # load data
    n = pd.read_csv(options.net, sep="\t")
    m = pd.read_csv(options.data, sep="\t")
    r = pd.read_csv(options.restrictions, sep="\t")

    # get mean values by month
    r['month'] = pd.PeriodIndex(r['samplingdate'], freq='M')

    grouped = r.groupby('month')
    month_means = grouped[['CHindex_DEU', 'CHindex_DNK', 'Sindex_DEU', 'Sindex_DNK',
                           'movement_change_DEU', 'movement_change_DNK',
                           'stilled_users_change_DEU', 'stilled_users_change_DNK']].mean()

    month_means.reset_index(inplace=True)

    # need to modify object types before merging
    month_means['month'] = month_means['month'].astype(str)
    n["month"] = n["month"].astype(str)
    r_n = pd.merge(n, month_means, on="month", how="left")
    r_n = r_n.fillna(0)

    # add metadata to df
    m.rename(columns={"month_year":"month"}, inplace=True)
    # calculate female percentage by month
    total_samples_per_month = m.groupby("month").size()
    female_percentage = m[m["sex"] == "F"].groupby("month").size() / total_samples_per_month * 100

    # calculate bin_age by month
    # define bins for age groups
    age_bins = pd.IntervalIndex.from_tuples([(0, 10), (10, 60), (60, 110)])
    m['bin_age'] = m['bin_age'].apply(lambda x: int(x.strip('()').split(',')[0]) if isinstance(x, str) else x)
    age_groups = pd.cut(m['bin_age'], bins=age_bins)
    age_counts = m.groupby(['month', age_groups]).size().unstack(fill_value=0)

    # Calculate mean scores by trimester
    mean_scores = m.groupby('month').agg({
        'virulence_score': 'mean',
        'resistance_score': 'mean'})
    # merge all results into a single DataFrame
    result_df = pd.concat([female_percentage.rename('female_percentage'), age_counts, mean_scores], axis=1)

    # twist results_df
    result_df.reset_index(inplace=True)
    result_df['month'] = result_df['month'].astype(str)
    # merge all three dfs
    all_params = pd.merge(result_df, r_n, on="month")
    # correlation matrix between all parameters
    corr_matrix = all_params.corr(numeric_only=True)

    # save df
    corr_matrix.to_csv(f"{os.path.splitext(options.net)[0]}_corrmatrix.tsv", sep="\t", index=False)


    # Plotting

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs resistance score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['degrees_centrality'], corr_matrix['resistance_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["degrees_centrality", "resistance_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['degrees_centrality'], corr_matrix['resistance_score'], 1)
    plt.plot(corr_matrix['degrees_centrality'], m*corr_matrix['degrees_centrality'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('Degrees Centrality')
    plt.ylabel('Resistance score')

    output_file = f"{os.path.splitext(options.net)[0]}_degreescentrality_resistance_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs virulence score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['degrees_centrality'], corr_matrix['virulence_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["degrees_centrality", "virulence_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['degrees_centrality'], corr_matrix['virulence_score'], 1)
    plt.plot(corr_matrix['degrees_centrality'], m*corr_matrix['degrees_centrality'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('Degrees Centrality')
    plt.ylabel('Virulence score')

    output_file = f"{os.path.splitext(options.net)[0]}_degreescentrality_virulence_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs resistance score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['movement_change_DEU'], corr_matrix['resistance_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["movement_change_DEU", "resistance_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['movement_change_DEU'], corr_matrix['resistance_score'], 1)
    plt.plot(corr_matrix['movement_change_DEU'], m*corr_matrix['movement_change_DEU'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('Movement change')
    plt.ylabel('Resistance score')

    output_file = f"{os.path.splitext(options.net)[0]}_movementchange_resistance_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs virulence score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['movement_change_DEU'], corr_matrix['virulence_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["movement_change_DEU", "virulence_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['movement_change_DEU'], corr_matrix['virulence_score'], 1)
    plt.plot(corr_matrix['movement_change_DEU'], m*corr_matrix['movement_change_DEU'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('Movement change')
    plt.ylabel('Virulence score')

    output_file = f"{os.path.splitext(options.net)[0]}_movementchange_virulence_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs resistance score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['CHindex_DEU'], corr_matrix['resistance_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["CHindex_DEU", "resistance_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['CHindex_DEU'], corr_matrix['resistance_score'], 1)
    plt.plot(corr_matrix['CHindex_DEU'], m*corr_matrix['CHindex_DEU'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('CH index')
    plt.ylabel('Resistance score')

    output_file = f"{os.path.splitext(options.net)[0]}_CHindex_resistance_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    plt.figure(figsize=(10, 10))
    # Scatter plot for degrees centrality vs virulence score
    plt.subplot(2, 2, 1)
    plt.scatter(corr_matrix['CHindex_DEU'], corr_matrix['virulence_score'], color='blue')
    plt.text(0.2, 0.8, f'corr={corr_matrix.at["CHindex_DEU", "virulence_score"]:.2f}', fontsize=16, color='black', fontweight='bold')
    m, b = np.polyfit(corr_matrix['CHindex_DEU'], corr_matrix['virulence_score'], 1)
    plt.plot(corr_matrix['CHindex_DEU'], m*corr_matrix['CHindex_DEU'] + b, color='xkcd:reddish orange')
    plt.title('')
    plt.xlabel('CHindex')
    plt.ylabel('Virulence score')

    output_file = f"{os.path.splitext(options.net)[0]}_CHindex_virulence_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    # plot all params vs virulence score
    # select only numeric
    numeric_columns = all_params.select_dtypes(include=np.number)
    # compute correlation between 'virulence_score' and other numeric columns
    corr_series = numeric_columns.drop('virulence_score', axis=1).corrwith(all_params['virulence_score'])

    # Plot correlation results
    plt.figure(figsize=(20, 8))
    corr_series.plot(kind='bar', grid=True, title="Correlation with virulence score", color="xkcd:warm grey")
    plt.ylim(-1, 1)

    output_file = f"{os.path.splitext(options.net)[0]}_virulence_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    # plot all params vs resistance score
    # select only numeric
    numeric_columns = all_params.select_dtypes(include=np.number)
    # compute correlation between 'resistance_score' and other numeric columns
    corr_series = numeric_columns.drop('resistance_score', axis=1).corrwith(all_params['resistance_score'])

    # Plot correlation results
    plt.figure(figsize=(20, 8))
    corr_series.plot(kind='bar', grid=True, title="Correlation with resistance score", color="xkcd:warm grey")
    plt.ylim(-1, 1)

    output_file = f"{os.path.splitext(options.net)[0]}_resistance_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    # plot corre matrix of all params
    plt.figure(figsize = (20,18))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr_matrix, annot=False, cmap=cmap)
    plt.title("Correlation of network features - covid restrictions - strains features")

    output_file = f"{os.path.splitext(options.net)[0]}_all_corr"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);
