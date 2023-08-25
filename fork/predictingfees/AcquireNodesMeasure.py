import networkx as nx
import pandas as pd

from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.fork.predictingfees import centrality_func
from pickhardtpayments.pickhardtpayments import ChannelGraph

"""
Script to obtain "graphinfo.csv" containing topological features of the nodes, (not all features are normalized)
- betweenness centrality with weight: 1, ppm, base
- closeness centrality with weight: 1
- eigenvector centrality with weight: 1
- capacity of the node
- avg ppm and avg base of the node
- median ppm and median ppm of the node
- degree of the node and degree with 2 hops of the node
"""

# delete channels with less than a given number
# paths with maximum minimum capacity

base = 20_000
channel_graph = ChannelGraph("../SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000, strategy="weighted_by_capacity")

G_DiGraph = channel_graph.getDiGraph(amount=10_000, mu=1000)  # NB: the degree() function is broken on this graph...

# df with the eigenvector centrality with respect to the pickhardt weight
print("Computing eigenvector centrality (edges weight: pickhardt)...")
ec_pickhardt = nx.eigenvector_centrality(G_DiGraph, weight='pickhardt_weight', max_iter=400, tol=1024 * 1.0e-6)
df_ec_pickhardt = pd.DataFrame(list(ec_pickhardt.items()), columns=['node', 'ec_pickhardt'])

# df with the betwenness centrality using the same weight (1) for all the edges
print("Computing standard betwenness centrality (edges weight: 1)...")
bc_standard = nx.betweenness_centrality(G_DiGraph, normalized=True)
df_bc_standard = pd.DataFrame(list(bc_standard.items()), columns=['node', 'bc_standard'])

# df with the eigenvector centrality using the same weight (1) for all the edges
print("Computing standard eigenvector centrality (edges weight: 1)...")
ec_standard = nx.eigenvector_centrality(G_DiGraph)
df_ec_standard = pd.DataFrame(list(ec_standard.items()), columns=['node', 'ec_standard'])

# df with the closeness centrality using the same weight (1) for all the edges
print("Computing standard closeness centrality (edges weight: 1)...")
closeness_standard = nx.closeness_centrality(G_DiGraph)
df_closeness_standard = pd.DataFrame(list(closeness_standard.items()), columns=['node', 'closeness_standard'])

# df with the betwenness centrality with respect to the ppm fee
print("Computing betwenness centrality (edges weight: ppm)...")
bc_ppm = nx.betweenness_centrality(G_DiGraph, weight='ppm', normalized=True)
df_bc_ppm = pd.DataFrame(list(bc_ppm.items()), columns=['node', 'bc_ppm'])

# df with the betwenness centrality with respect to the base fee
print("Computing betwenness centrality (edges weight: base)...")
bc_base = nx.betweenness_centrality(G_DiGraph, weight='base', normalized=True)
df_bc_base = pd.DataFrame(list(bc_base.items()), columns=['node', 'bc_base'])

# df with the betwenness centrality with respect to the capacity
print("Computing betwenness centrality (edges weight: 1000/capacity)...")
bc_capacity = nx.betweenness_centrality(G_DiGraph, weight='capacity', normalized=True)
df_bc_capacity = pd.DataFrame(list(bc_base.items()), columns=['node', 'bc_capacity'])

# df with the betwenness centrality with respect to the pickhardt weight
print("Computing betwenness centrality (edges weight: pickhardt weight)...")
bc_pickhardt = nx.betweenness_centrality(G_DiGraph, weight='pickhardt_weight', normalized=True)
df_bc_pickhardt = pd.DataFrame(list(bc_pickhardt.items()), columns=['node', 'bc_pickhardt'])







# This is not working... gives the same values as the closeness standard
# print("Computing standard closeness centrality (edges weight: 1)...")
# closeness_capacity = nx.closeness_centrality(G_DiGraph, distance='capacity')
# df_closeness_capacity = pd.DataFrame(list(closeness_standard.items()), columns=['node', 'closeness_capacity'])

# df with the degree of each node
print("Computing degree (1 hop distance)...")
df_degree = pd.DataFrame(list(centrality_func.compute_degrees_at_distance(G_DiGraph, radius=1).items()),
                         columns=['node', 'degree'])

# df with the "degree two hops" / ego distance 2 of all the nodes
print("Computing degree (2 hop distance)...")
df_degree_distance_2 = pd.DataFrame(list(centrality_func.compute_degrees_at_distance(G_DiGraph, radius=2).items()),
                                    columns=['node', 'degree_2_hops'])

# df with the expected capacity of each node
print("Computing expected capacity...")
df_exp_cap = pd.DataFrame(list(channel_graph.get_nodes_capacities().items()), columns=['node', 'exp_cap'])

# df with the avg base fee and the avg ppm of each node
print("Computing avg ppm and avg base...")
avg_ppm_dict, avg_base_dict = centrality_func.get_average_node_ppm_and_base_fee(channel_graph)
df_avg_ppm = pd.DataFrame(list(avg_ppm_dict.items()), columns=['node', 'avg_ppm'])
df_avg_base = pd.DataFrame(list(avg_base_dict.items()), columns=['node', 'avg_base'])

# df with the median base fee and the median ppm of each node
print("Computing median ppm and median base...")
median_ppm_dict, median_base_dict = centrality_func.get_median_node_ppm_and_base_fee(channel_graph)
df_median_ppm = pd.DataFrame(list(median_ppm_dict.items()), columns=['node', 'median_ppm'])
df_median_base = pd.DataFrame(list(median_base_dict.items()), columns=['node', 'median_base'])





# Merge the df together and save the final df into a csv
df_list = [
    df_avg_ppm,
    df_avg_base,
    df_bc_ppm,
    df_bc_base,
    df_degree,
    df_exp_cap,
    df_bc_standard,
    df_ec_standard,
    df_median_base,
    df_median_ppm,
    df_closeness_standard,
    df_degree_distance_2,
    df_bc_capacity,
    df_bc_pickhardt,
    df_ec_pickhardt
    # df_closeness_capacity
]
merged_df = df_list[0]
for df in df_list[1:]:
    merged_df = pd.merge(merged_df, df, on='node')

merged_df.to_csv('graphinfo.csv', index=False)
print("File correctly saved...")
# sorted_df = merged_df.sort_values('bc_base', ascending=False)
# pd.set_option('display.max_columns', None)
# print(sorted_df)
