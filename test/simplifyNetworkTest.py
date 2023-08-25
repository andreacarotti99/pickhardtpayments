from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.pickhardtpayments import ChannelGraph

snapshot_file = "cosimo_19jan2023_converted.json"
channel_graph = ChannelGraph("../fork/SNAPSHOTS/" + snapshot_file)

print(f"Nodes in the network: {channel_graph.network.number_of_nodes()}")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=2000, strategy="random")
print(f"Nodes in the network: {channel_graph.network.number_of_nodes()}")

v = VisualNetworkRepresentation(channel_graph.network)
v.show_network(keep_labels=False)
