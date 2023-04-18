import networkx as nx
import pandas as pd

from pickhardtpayments.fork.replicatingstrategy.SortingMetrics import assign_fee_and_cap_weight
from pickhardtpayments.pickhardtpayments import ChannelGraph


base = 20_000
channel_graph = ChannelGraph("../SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=100, strategy="weighted_by_capacity")
G_DiGraph = channel_graph.getDiGraph()


# df with the betwenness centrality with respect to the ppm fee
bc_ppm = nx.betweenness_centrality(G_DiGraph, weight='ppm', normalized=True)
df_bc_ppm = pd.DataFrame(list(bc_ppm.items()), columns=['node', 'bc_ppm'])

# df with the betwenness centrality with respect to the base fee
bc_base = nx.betweenness_centrality(G_DiGraph, weight='base', normalized=True)
df_bc_base = pd.DataFrame(list(bc_base.items()), columns=['node', 'bc_base'])

# df with the degree of each node
df_degree = pd.DataFrame({'node': list(channel_graph.network.nodes()), 'degree': list(dict(channel_graph.network.degree()).values())})

# df with the expected capacity of each node
df_exp_cap = pd.DataFrame(list(channel_graph.get_nodes_capacities().items()), columns=['node', 'exp_cap'])


# merge the df together
merged_df = pd.merge(pd.merge(pd.merge(df_bc_ppm, df_bc_base, on='node'), df_degree, on='node'), df_exp_cap, on='node')


sorted_df = merged_df.sort_values('bc_base', ascending=False)
pd.set_option('display.max_columns', None)

print(sorted_df)
