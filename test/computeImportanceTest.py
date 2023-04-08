from pickhardtpayments.fork.replicatingstrategy.SortingMetrics import compute_importance_for_each_node, \
    compute_avg_chan_cap_for_each_node
from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=2000)
# compute_importance_for_each_node(channel_graph=channel_graph, amt=1000)
compute_avg_chan_cap_for_each_node(channel_graph=channel_graph)
