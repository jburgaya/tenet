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


def get_options():
    import argparse

    description = 'Generate TENET and calculate network parameters'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('snps2te',
                        help='Output file from snps2te.py containing multiple cols w/ te info')
    parser.add_argument('data',
                        help='Metadata')

    return parser.parse_args()


if __name__ == "__main__":
    options = get_options()

    # load data
    te = pd.read_csv(options.snps2te, sep="\t")
    d = pd.read_csv(options.data, sep="\t")


    # prepare te
    # drop duplicates if there are any
    d.drop_duplicates(subset='sampleid', inplace=True)
    # for klebsiella data, need to fill collection data with MHH and CPH
    d.loc[d['hospital_loc'] == 'Germany', 'collection'] = 'MHH'
    d.loc[d['hospital_loc'] == 'Denmark', 'collection'] = 'CPH'
    # prepare data for network
    # add date
    te['samplingdate1'] = te['sample1'].map(d.set_index('sampleid')['samplingdate'])
    te['samplingdate2'] = te['sample2'].map(d.set_index('sampleid')['samplingdate'])
    # add ST
    te['ST1'] = te['sample1'].map(d.set_index('sampleid')['ST'])
    te['ST2'] = te['sample2'].map(d.set_index('sampleid')['ST'])
    # add hospital_loc and collection
    te['hospital_loc1'] = te['sample1'].map(d.set_index('sampleid')['hospital_loc'])
    te['hospital_loc2'] = te['sample2'].map(d.set_index('sampleid')['hospital_loc'])
    te['collection1'] = te['sample1'].map(d.set_index('sampleid')['collection'])
    te['collection2'] = te['sample2'].map(d.set_index('sampleid')['collection'])
    # add ressitance score
    te['resistance1'] = te['sample1'].map(d.set_index('sampleid')['resistance_score'])
    te['resistance2'] = te['sample2'].map(d.set_index('sampleid')['resistance_score'])
    # add virulence score
    te['virulence1'] = te['sample1'].map(d.set_index('sampleid')['virulence_score'])
    te['virulence2'] = te['sample2'].map(d.set_index('sampleid')['virulence_score'])
    # add isolation_source_categ
    te['isolation_source1'] = te['sample1'].map(d.set_index('sampleid')['isolation_source_categ'])
    te['isolation_source2'] = te['sample2'].map(d.set_index('sampleid')['isolation_source_categ'])
    # drop rows with empty samplingdate
    te = te[te['samplingdate1'].notna()]
    te = te[te['samplingdate2'].notna()]


    # calculate network measures for te_10_60d
    # get network properties
    # group by monthly counts
    te["samplingdate1"] = pd.to_datetime(te["samplingdate1"])
    te["month"] = te["samplingdate1"].dt.to_period("M")
    month_groups = te.groupby("month")

    # start empty list
    network_p = []

    # calculate network propertries
    for month, month_data in month_groups:
        G = nx.Graph()
    
        # add nodes and edges
        for _, row in month_data.iterrows():
            G.add_node(row['sample1'], ST=row['ST1'], loc=row["hospital_loc1"], collection=row["collection1"], r=row["resistance1"], v=row["virulence1"], source=row["isolation_source1"])
            G.add_node(row['sample2'], ST=row['ST2'], loc=row["hospital_loc2"], collection=row["collection2"], r=row["resistance2"], v=row["virulence2"], source=row["isolation_source2"])

            edge_length = row['te_10_60d']
            G.add_edge(row['sample1'], row['sample2'], weight=edge_length)

        # calculate connected components
        connected_components = list(nx.connected_components(G))
    
        # initialize lists to store centrality measures for connected components
        degrees_centrality_list = []
        closeness_centrality_list = []
        betweenness_centrality_list = []
        current_flow_betweenness_centrality_list = []
        load_centrality_list = []
        harmonic_centrality_list = []

        # iterate over connected components
        for subgraph_nodes in connected_components:
            subgraph = G.subgraph(subgraph_nodes)
        
            try:
                # calculate centrality measures for the connected component
                degrees_centrality = nx.degree_centrality(subgraph)
                closeness_centrality = nx.closeness_centrality(subgraph)
                betweenness_centrality = nx.betweenness_centrality(subgraph)
                current_flow_betweenness_centrality = nx.current_flow_betweenness_centrality(subgraph)
                load_centrality = nx.load_centrality(subgraph)
                harmonic_centrality = nx.harmonic_centrality(subgraph)

                # append centrality measures to respective lists
                degrees_centrality_list.append(degrees_centrality)
                closeness_centrality_list.append(closeness_centrality)
                betweenness_centrality_list.append(betweenness_centrality)
                current_flow_betweenness_centrality_list.append(current_flow_betweenness_centrality)
                load_centrality_list.append(load_centrality)
                harmonic_centrality_list.append(harmonic_centrality)
            except ZeroDivisionError:
                # handle division by zero error
                pass

        # calculate average centrality measures across connected components
        avg_degrees_centrality = sum(map(lambda x: sum(x.values()), degrees_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0
        avg_closeness_centrality = sum(map(lambda x: sum(x.values()), closeness_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0
        avg_betweenness_centrality = sum(map(lambda x: sum(x.values()), betweenness_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0
        avg_current_flow_betweenness_centrality = sum(map(lambda x: sum(x.values()), current_flow_betweenness_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0
        avg_load_centrality = sum(map(lambda x: sum(x.values()), load_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0
        avg_harmonic_centrality = sum(map(lambda x: sum(x.values()), harmonic_centrality_list)) / len(G.nodes) if len(G.nodes) > 0 else 0

        # Append results to the list
        network_p.append({
            'month': month,
            'degrees_centrality': avg_degrees_centrality,
            'closeness_centrality': avg_closeness_centrality,
            'betweenness_centrality': avg_betweenness_centrality,
            'current_flow_betweenness_centrality': avg_current_flow_betweenness_centrality,
            'load_centrality': avg_load_centrality,
            'harmonic_centrality': avg_harmonic_centrality,
        })


    # create df
    network_p_te_10_60 = pd.DataFrame(network_p)

    # save df
    output_file = f"{os.path.splitext(options.snps2te)[0]}_network_p.tsv"
    network_p_te_10_60.to_csv(output_file, index=False, sep='\t')

    
    # Draw network
    # plot month counts
    month_counts = te["month"].value_counts().sort_index()
    month_labels = month_counts.index.strftime('%Y-%m')

    plt.figure(figsize=(10, 6))
    plt.bar(month_labels, month_counts.values, color='xkcd:beige')
    plt.xlabel('')
    plt.ylabel('#')
    plt.title('')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output_file = f"{os.path.splitext(options.snps2te)[0]}_month_counts"

    plt.savefig(f'{output_file}.png',
            dpi=150,
            bbox_inches='tight',
            transparent=True)
    plt.savefig(f'{output_file}.svg',
            dpi=150,
            bbox_inches='tight',
            transparent=True);

    # plot network
    # define colors
    collections = {"MHH": "xkcd:lavender", "SRA": "xkcd:turquoise", "CPH": "xkcd:dark blue"}

    # iterate over each month and create a separate plot
    for month, month_data in month_groups:
        G = nx.Graph()
    
        # add nodes and edges
        for _, row in month_data.iterrows():
            G.add_node(row['sample1'], ST=row['ST1'], loc=row["hospital_loc1"], collection=row["collection1"], r=row["resistance1"], v=row["virulence1"], source=row["isolation_source1"])
            G.add_node(row['sample2'], ST=row['ST2'], loc=row["hospital_loc2"], collection=row["collection2"], r=row["resistance2"], v=row["virulence2"], source=row["isolation_source2"])
            if row['te_10_60d'] == 1:  
                edge_length = row['snps']
                G.add_edge(row['sample1'], row['sample2'], weight=edge_length)

        # draw the graph for the current month
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G, scale=5, dim=2, k=0.5)

        # draw edges with adjusted lengths
        nx.draw_networkx_edges(G, pos, width=[2], edge_vmin=0, edge_vmax=10, edge_color='black', alpha=1)

        # draw color-coded nodes based on collection
        node_colors = ["xkcd:lavender" if G.nodes[node]["collection"] == "MHH"
                       else "xkcd:turquoise" if G.nodes[node]["collection"] == "SRA"
                       else "xkcd:dark blue" for node in G.nodes]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=150)

        # legend
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label) for label, color in collections.items()]
        plt.legend(handles=legend_handles, loc='upper left', facecolor="white")
    
        plt.title(f'Month: {month}')
        output_file = f"{os.path.splitext(options.snps2te)[0]}_network_{month}"

        plt.savefig(f'{output_file}.png',
                dpi=150,
                bbox_inches='tight',
                transparent=True)
        plt.savefig(f'{output_file}.svg',
                dpi=150,
                bbox_inches='tight',
                transparent=True);
