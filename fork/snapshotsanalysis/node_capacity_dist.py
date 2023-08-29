from pickhardtpayments.pickhardtpayments import ChannelGraph

snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'
channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(
    tentative_nodes_to_keep=500,
    strategy="weighted_by_capacity")

node_capacity_dict = channel_graph.get_nodes_capacities()

sorted_capacities = sorted(node_capacity_dict.values())

print(sorted_capacities)
