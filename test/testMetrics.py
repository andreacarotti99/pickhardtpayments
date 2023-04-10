from pickhardtpayments.fork.replicatingstrategy.SortingMetrics import *
from pickhardtpayments.pickhardtpayments import ChannelGraph




channel_graph = ChannelGraph("../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=2000, strategy="random")

# assign_pickhardt_weights(channel_graph=channel_graph, mu=1, amount=500_000)
# betwenness_pickhardt_weight_dict = betwenness_pickhardt_weight_dict(channel_graph)

assign_fee_and_cap_weight(channel_graph=channel_graph, amount=10_000)
betwenness_weighted_cap_and_fee_dict = betwenness_weighted_cap_and_fee_dict(channel_graph, fee_weight=0.5, cap_weight=0.5)

print(betwenness_weighted_cap_and_fee_dict)

sorted_important_nodes = sort_dict_by_value_descending(betwenness_weighted_cap_and_fee_dict)

