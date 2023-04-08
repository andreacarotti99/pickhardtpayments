import networkx as nx

from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.fork.replicatingstrategy.SortingMetrics import sort_dict_by_value_descending, \
    compute_edge_betweenness_for_each_node
from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")

channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000)



print(channel_graph.network.number_of_edges())

# create an undirected graph from G
H = nx.MultiGraph(channel_graph.network)

print(H.number_of_edges())

# remove parallel edges
H = nx.Graph([(u, v) for u, v, d in H.edges(data=True)])

channel_graph.network = H

# visual = VisualNetworkRepresentation(channel_graph)
# visual.show_network(keep_labels=False)

print(H.number_of_edges())


nodes_to_copy_dict = (compute_edge_betweenness_for_each_node(H))

print(nodes_to_copy_dict)
