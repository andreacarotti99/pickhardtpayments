from pickhardtpayments.pickhardtpayments import ChannelGraph

snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'

channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(
    tentative_nodes_to_keep=100,
    strategy="weighted_by_capacity")


d1 = channel_graph.get_nodes_capacities()




random_node = "026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2"

random_node = channel_graph.get_random_node_uniform_distribution()


print('random node is', random_node)

print('capacity is: ', d1[random_node])

old_neighbors = channel_graph.get_connected_nodes(random_node)
new_neighbors = []

random_nodes = []

for dest_node in channel_graph.get_connected_nodes(random_node):
    for ch in channel_graph.get_channels(random_node, dest_node):
        channel_graph.close_channel(random_node, dest_node, ch.short_channel_id)

        new_random_node = channel_graph.get_random_node_uniform_distribution()
        while new_random_node == random_node or new_random_node in old_neighbors or new_random_node in new_neighbors:
            new_random_node = channel_graph.get_random_node_uniform_distribution()

        random_nodes.append(random_node)

        channel_graph.create_channel(random_node, new_random_node, ch.is_announced, ch.capacity,
                                         ch.flags, ch.is_active, ch.last_update, ch.base_fee, ch.ppm, ch.cltv_delta,
                                         ch.htlc_min_msat, ch.htlc_max_msat, str(ch.short_channel_id) + '_2')
        new_neighbors.append(new_random_node)

d2 = channel_graph.get_nodes_capacities()
print('capacity now is: ', d2[random_node])


combined_data = []

combined_data = [((node, channel_graph.[node], new_neighbors[node])) for node in random_nodes]




