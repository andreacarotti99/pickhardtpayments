from pickhardtpayments.pickhardtpayments import ChannelGraph

snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'

channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(
    tentative_nodes_to_keep=30,
    strategy="weighted_by_capacity")


d1 = channel_graph.get_nodes_capacities()

random_node = channel_graph.get_random_node_uniform_distribution()

print('random node is', random_node)

for dest_node in channel_graph.get_connected_nodes(random_node):
     ch = channel_graph.get_channel_without_short_channel_id(random_node, dest_node)
     channel_graph.close_channel(random_node, dest_node)



d2 = channel_graph.get_nodes_capacities()

print(d1)
print()
print(d2)
