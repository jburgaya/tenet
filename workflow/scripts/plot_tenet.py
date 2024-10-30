import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse

# Load your data
def load_data(te_file, data_file):
    te = pd.read_csv(te_file, sep="\t")
    metadata = pd.read_csv(data_file, sep="\t")
    metadata.columns = metadata.columns.str.strip()  # Strip whitespace from column names
    return te, metadata

# Create a color mapping from unique mlst values
def create_color_mapping(metadata):
    unique_mlst = metadata['mlst'].unique()
    colors = plt.cm.get_cmap('tab10', len(unique_mlst))  # Using a colormap
    color_mapping = {mlst: colors(i) for i, mlst in enumerate(unique_mlst)}
    return color_mapping

# Map sampling dates from metadata to transmission events
def map_sampling_dates(te, metadata):
    te = te.copy()  # Avoid modifying the original dataframe
    te = te.merge(metadata[['sampleid', 'samplingdate']], left_on='sample1', right_on='sampleid', how='left')
    te['samplingdate'] = pd.to_datetime(te['samplingdate'], format='%d.%m.%Y')  # Convert to datetime
    return te

# Create the network graph
def create_network(te, metadata, color_mapping, date_filter=None):
    G_combined = nx.Graph()
    
    # Filter the transmission events by date if specified
    if date_filter:
        te = te[te['samplingdate'].dt.to_period('M') == date_filter]

    # Add all unique nodes with color attributes
    all_nodes = set(te['sample1']).union(set(te['sample2']))
    
    for node in all_nodes:
        # Set color based on color_column (mlst), default to grey if not found
        mlst_value = metadata.loc[metadata['sampleid'] == node, 'mlst']
        if not mlst_value.empty:
            color = color_mapping.get(mlst_value.values[0], 'grey')  # Default to grey if not found
        else:
            color = 'grey' 
        
        G_combined.add_node(node, color=color)

    # Add edges based on transmission
    for _, row in te.iterrows():
        if row['transmission'] == 1:  # Adjust the condition as necessary
            G_combined.add_edge(row['sample1'], row['sample2'])

    return G_combined

# Draw the network
def draw_network(G_combined, title, output_prefix):
    node_colors = [G_combined.nodes[node]['color'] for node in G_combined.nodes()]
    plt.figure(figsize=(12, 8))  # Set figure size
    nx.draw(G_combined, node_color=node_colors, with_labels=True, font_size=8)
    plt.title(title)
    plt.savefig(f"{output_prefix}.png")  # Save as PNG
    plt.savefig(f"{output_prefix}.svg")  # Save as SVG
    plt.close()

# Main function to run the script
def main(te_file, data_file, color_column):
    te, metadata = load_data(te_file, data_file)

    # Map sampling dates from metadata to transmission events
    te = map_sampling_dates(te, metadata)

    # Create color mapping
    color_mapping = create_color_mapping(metadata)

    # Create and draw combined network
    G_combined = create_network(te, metadata, color_mapping)
    draw_network(G_combined, "Combined Network Graph", "out/plots/network_combined")

    # Create and draw monthly networks
    for month in te['samplingdate'].dt.to_period('M').unique():
        G_monthly = create_network(te, metadata, color_mapping, date_filter=month)
        draw_network(G_monthly, f"Network Graph for {month}", f"out/plots/network_{month}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot a network graph based on transmission data.")
    parser.add_argument("te_file", help="Path to the transmission events file.")
    parser.add_argument("data_file", help="Path to the metadata file.")
    parser.add_argument("--color_column", default="mlst", help="Column for coloring nodes (default: 'mlst').")
    parser.add_argument("--sample_column", default="sampleid", help="Column for sample IDs (default: 'sampleid').")
    parser.add_argument("--date_column", default="samplingdate", help="Column for sampling dates (default: 'samplingdate').")

    args = parser.parse_args()
    
    main(args.te_file, args.data_file, args.color_column)

